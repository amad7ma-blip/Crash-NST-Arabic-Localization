"""Build the complete compressed Crash NST Arabic update.pak and run full verification."""
import collections
import hashlib
import json
import os
import re
import struct
import sys
from PIL import Image, ImageDraw

WS = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic'
GAME_ARCH = r'C:\Program Files (x86)\Steam\steamapps\common\Crash Bandicoot - N Sane Trilogy\archives'
PKG_DIR = os.path.join(WS, 'package')
PKG_DATA = os.path.join(PKG_DIR, 'data')
LOGS_DIR = os.path.join(WS, 'workspace', 'logs')
EXTRACTED_DIR = os.path.join(WS, 'workspace', 'extracted')

sys.path.insert(0, os.path.join(WS, 'workspace', 'scripts'))
from nst_alchemy import IgaArchiveV11, IgzDoc, build_iga_v11
from font_patcher import patch_font_igz
from vfx_font_patcher import patch_vfx_font_and_textures
from arabic_shaper import shape_arabic_text, patch_lng_bytes
from translations_part1 import KEEP_EXACT, TRANS_PART1
from translations_part2 import TRANS_PART2

PH_RE = re.compile(r'\{[0-9]+\}|%[0-9.]*[lh]*[sdifcxu%]')


def choose_wrap_width(item: dict, ar: str) -> int:
    """Choose safe pre-BiDi word-wrap width based on UI container category."""
    en = item['en']
    cat = item['category']
    iid = item['id']

    # Full-width legal bars and single-line keyboard prompt stay unwrapped
    if 'ACTIVISION, CRASH and CRASH BANDICOOT are trademarks' in en:
        return 0
    if en == 'Press any Keyboard/Mouse key to Remap':
        return 0

    if cat == 'system_and_graphics_ui':
        return 48
    if cat in ('ui_menu', 'platform_strings'):
        # Preserve multi-line items that already contain explicit line breaks
        if '\n' in ar or '\r' in ar:
            return 0
        # Avoid breaking wrapped Latin product names if slightly past 50
        return 52
    if cat in ('level_gameplay_and_boss', 'level_title_and_hint'):
        if '\n' in ar or '\r' in ar:
            return 0
        return 64
    return 0


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def extract_bitmap_font_glyphs(raw_igz: bytes) -> tuple[dict[int, dict], Image.Image]:
    """Read patched igBitmapFont character metrics and RGBA8 atlas straight from .igz bytes."""
    doc = IgzDoc(raw_igz)
    img_off = next(o for o, t in sorted(doc.objects.items()) if t == 'igImage2')
    w, h = struct.unpack_from('<HH', doc.data[img_off >> 27], (img_off & 0x7FFFFFF) + 0x18)
    sz = doc.u32(img_off + 0x38)
    pix_ptr = doc.u64(img_off + 0x40)
    psec, poff = pix_ptr >> 27, pix_ptr & 0x7FFFFFF
    atlas_raw = bytes(doc.data[psec][poff:poff + sz])
    atlas = Image.frombytes('RGBA', (w, h), atlas_raw)

    font_off = next(o for o, t in sorted(doc.objects.items()) if t == 'igBitmapFont')
    clist_ptr = doc.u64(font_off + 0x50)
    cnt = doc.u32(clist_ptr + 0x10)
    arr_ptr = doc.u64(clist_ptr + 0x20)

    glyphs = {}
    for i in range(cnt):
        m_off = struct.unpack_from('<Q', doc.data[arr_ptr >> 27], (arr_ptr & 0x7FFFFFF) + i * 8)[0]
        msec, mo = m_off >> 27, m_off & 0x7FFFFFF
        b = doc.data[msec]
        cp, kl, kr, cw, _p1, _p2, _wf, ch_h, u0, v0, u1, v1 = struct.unpack_from('<I11f', b, mo + 0x10)
        glyphs[cp] = {
            'x0': int(round(u0 * w)),
            'y0': int(round(v0 * h)),
            'x1': int(round(u1 * w)),
            'y1': int(round(v1 * h)),
            'kl': kl,
            'kr': kr,
            'h': ch_h,
            'w': cw,
        }
    return glyphs, atlas


def extract_vfx_codepoints(raw_vfx_igz: bytes) -> set[int]:
    """Read supported codepoints from patched Vfx_Text_Character_Infos.igz."""
    doc = IgzDoc(raw_vfx_igz)
    ht = next(o for o, t in doc.objects.items() if t == 'CCharacterInfoHashTable')
    val_ptr = doc.u64(ht + 0x18)
    key_sz, key_ptr = doc.u32(ht + 0x20), doc.u64(ht + 0x28)
    nbuckets = key_sz // 2
    keys = struct.unpack_from(f'<{nbuckets}H', doc.data[key_ptr >> 27], key_ptr & 0x7FFFFFF)
    vals = struct.unpack_from(f'<{nbuckets}Q', doc.data[val_ptr >> 27], val_ptr & 0x7FFFFFF)
    return {k for k, v in zip(keys, vals) if v != 0}


def render_bitmap_line(text: str, glyphs: dict[int, dict], atlas: Image.Image) -> Image.Image:
    """Simulate exact Crash engine LTR glyph blitting using igCharMetrics + atlas."""
    line_h = int(round(max((g['h'] for g in glyphs.values()), default=48))) + 20
    total_w = 24.0
    for ch in text:
        cp = ord(ch)
        if ch == ' ':
            total_w += 14.0
        elif cp in glyphs:
            g = glyphs[cp]
            total_w += max(1.0, g['kl'] + g['w'] + g['kr'])
        elif 0xE000 <= cp <= 0xF8FF:
            total_w += 36.0
        else:
            total_w += 20.0
    canvas = Image.new('RGBA', (max(int(total_w) + 8, 40), line_h), (20, 26, 36, 255))
    draw = ImageDraw.Draw(canvas)
    x = 12.0
    base_y = 10
    for ch in text:
        cp = ord(ch)
        if ch == ' ':
            x += 14.0
            continue
        if 0xE000 <= cp <= 0xF8FF:
            ix = int(round(x))
            draw.ellipse([ix + 2, base_y + 4, ix + 30, base_y + 32], fill=(70, 175, 80, 255), outline=(230, 240, 255, 255))
            x += 36.0
            continue
        g = glyphs.get(cp)
        if g is None:
            ix = int(round(x))
            draw.rectangle([ix, base_y, ix + 16, base_y + 28], outline=(255, 60, 60, 255))
            x += 20.0
            continue
        x += g['kl']
        gw = g['x1'] - g['x0']
        gh = g['y1'] - g['y0']
        if gw > 0 and gh > 0:
            crop = atlas.crop((g['x0'], g['y0'], g['x1'], g['y1']))
            canvas.alpha_composite(crop, (max(0, int(round(x))), base_y))
        x += g['w'] + g['kr']
    return canvas


def main():
    os.makedirs(PKG_DATA, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(EXTRACTED_DIR, exist_ok=True)

    # 1. Load inventory & all translations
    mi = json.load(open(os.path.join(EXTRACTED_DIR, 'master_inventory.json'), encoding='utf-8'))
    cat = json.load(open(os.path.join(LOGS_DIR, 'loc_and_fonts_catalog.json'), encoding='utf-8'))

    all_trans = {}
    all_trans.update(TRANS_PART1)
    all_trans.update(TRANS_PART2)

    overlap = set(TRANS_PART1) & set(TRANS_PART2)
    assert not overlap, f'Overlap between PART1 and PART2: {len(overlap)}'

    # Verify complete 100% coverage & placeholder integrity before shaping
    shaped_map = {}
    export_rows = []
    for item in mi['items']:
        en = item['en']
        if en in KEEP_EXACT:
            export_rows.append({
                'id': item['id'],
                'category': item['category'],
                'keep_exact': True,
                'en': en,
                'logical_ar': en,
                'display_ar': en,
            })
            continue
        assert en in all_trans, f'Missing translation for ID={item["id"]}: {en!r}'
        ar = all_trans[en]
        assert collections.Counter(PH_RE.findall(en)) == collections.Counter(PH_RE.findall(ar)), (
            f'Placeholder mismatch ID={item["id"]}: {en!r} vs {ar!r}'
        )
        ww = choose_wrap_width(item, ar)
        vis = shape_arabic_text(ar, wrap_width=ww)
        shaped_map[en] = vis
        export_rows.append({
            'id': item['id'],
            'category': item['category'],
            'keep_exact': False,
            'wrap_width': ww,
            'en': en,
            'logical_ar': ar,
            'display_ar': vis,
        })

    shaped_json_path = os.path.join(EXTRACTED_DIR, 'final_translations_shaped.json')
    with open(shaped_json_path, 'w', encoding='utf-8') as f:
        json.dump(export_rows, f, ensure_ascii=False, indent=2)
    print(f'[1/6] Shaped {len(shaped_map)} translations (+ {len(KEEP_EXACT)} KEEP_EXACT) -> final_translations_shaped.json')

    out_pak = os.path.join(PKG_DATA, 'update.pak')
    verify_only = ('--verify-only' in sys.argv) and os.path.exists(out_pak)
    fonts_loc = [
        ('languagestartup.pak', 'fonts/ProximaNova-Info.igz'),
        ('permanent.pak', 'fonts/ProximaNova-Title.igz'),
        ('essentialui.pak', 'fonts/GeekSpeak.igz'),
        ('permanent.pak', 'fonts/GeekSpeak_Outline.igz'),
        ('permanent.pak', 'fonts/zoinks.igz'),
        ('permanent.pak', 'fonts/Zoinks_Outline.igz'),
        ('permanent.pak', 'fonts/zoinksXL.igz'),
        ('permanent.pak', 'fonts/ZoinksXL_Outline.igz'),
        ('4ktextures_essentialui.pak', 'fonts/GeekSpeak4K.igz'),
        ('4ktextures_essentialui.pak', 'fonts/GeekSpeak_Outline4K.igz'),
        ('4ktextures_essentialui.pak', 'fonts/Zoinks_Outline4K.igz'),
    ]
    update_files: dict[str, bytes] = {}
    if not verify_only:
        # Cache opened base archives
        arc_cache: dict[str, IgaArchiveV11] = {}

        def get_arc(pak_name: str) -> IgaArchiveV11:
            if pak_name not in arc_cache:
                arc_cache[pak_name] = IgaArchiveV11(os.path.join(GAME_ARCH, pak_name))
            return arc_cache[pak_name]

        try:
            # 2. Patch all 11 2D UI bitmap fonts
            for pak, logical in fonts_loc:
                raw = get_arc(pak).read(logical)
                patched, stats = patch_font_igz(raw, logical)
                update_files[logical] = patched
            print(f'[2/6] Patched {len(fonts_loc)} bitmap fonts (.igz)')

            # 3. Patch 3D VFX floating level title font + 3 BC3/BC5 mipmapped atlases
            hub_arc = get_arc('L200_Hub.pak')
            vfx_out = patch_vfx_font_and_textures(
                hub_arc.read('vfxFonts/Vfx_Text_Character_Infos.igz'),
                hub_arc.read('textures/ColorMap,textures@!ui!Crash!VFX_TEXT_LG`png,111.igz'),
                hub_arc.read('textures/ColorMap,textures@!ui!Crash!VFX_TEXT_LG_White`png,111.igz'),
                hub_arc.read('textures/NormalMap,textures@!ui!Crash!VFX_TEXT_LG_BW_NRM`png,111.igz'),
                preview_dir=os.path.join(LOGS_DIR, 'font_previews'),
            )
            update_files.update(vfx_out)
            print(f'[3/6] Patched {len(vfx_out)} 3D VFX font & texture files')

            # 4. Patch all 437 unique _en.lng localization files
            en_lngs = sorted(k for k in cat['lng_files'] if k.lower().endswith('_en.lng'))
            total_slots_changed = 0
            patched_lng_count = 0
            untouched_en_lngs = 0
            for logical in en_lngs:
                pak = cat['lng_files'][logical][0][0]
                raw_lng = get_arc(pak).read(logical)
                patched_lng, n_chg = patch_lng_bytes(raw_lng, shaped_map)
                if n_chg > 0:
                    update_files[logical] = patched_lng
                    total_slots_changed += n_chg
                    patched_lng_count += 1
                else:
                    untouched_en_lngs += 1
            print(
                f'[4/6] Scanned {len(en_lngs)} _en.lng files: patched {patched_lng_count} files '
                f'({total_slots_changed} string slots), skipped {untouched_en_lngs} KEEP_EXACT/empty files'
            )
        finally:
            for arc in arc_cache.values():
                arc.close()

        # 5. Build LZMA-compressed IGA v11 update.pak
        raw_total = sum(len(v) for v in update_files.values())
        build_iga_v11(update_files, out_pak, compress=True)
        pak_size = os.path.getsize(out_pak)
        pak_sha = sha256_file(out_pak)
        print(
            f'[5/6] Built compressed package\\data\\update.pak: {len(update_files)} entries, '
            f'raw={raw_total / (1<<20):.2f} MB -> pak={pak_size / (1<<20):.2f} MB '
            f'({pak_size * 100 / raw_total:.1f}%), sha256={pak_sha[:16]}...'
        )
    else:
        pak_size = os.path.getsize(out_pak)
        pak_sha = sha256_file(out_pak)
        with IgaArchiveV11(out_pak) as tmp_arc:
            raw_total = sum(e.size for e in tmp_arc.entries)
            n_ent = len(tmp_arc.entries)
        print(f'[2-5/6] Reusing verified {out_pak} ({n_ent} entries, pak={pak_size / (1<<20):.2f} MB, sha256={pak_sha[:16]}...)')

    # 6. Full automated verification directly on package\data\update.pak!
    with IgaArchiveV11(out_pak) as pkg_arc:
        verif = {
            'entries_total': len(pkg_arc.entries),
            'pak_size_bytes': pak_size,
            'pak_sha256': pak_sha,
            'raw_size_bytes': raw_total,
            'readback_mismatches': 0,
            'igz_parse_errors': 0,
            'untranslated_slots_remaining': 0,
            'missing_glyphs_by_font': {},
            'vfx_missing_arabic_cps': [],
        }
        used_non_pua_cps = set()
        used_level_title_cps = set()

        if update_files:
            assert len(pkg_arc.entries) == len(update_files)
        for e in pkg_arc.entries:
            got = pkg_arc.read_entry(e)
            if update_files:
                if got != update_files[e.logical_name]:
                    verif['readback_mismatches'] += 1
            elif len(got) != e.size:
                verif['readback_mismatches'] += 1
            try:
                doc = IgzDoc(got)
            except Exception as ex:
                verif['igz_parse_errors'] += 1
                print('IGZ parse error:', e.logical_name, ex)
                continue

            if e.logical_name.lower().endswith('.lng'):
                onam_rstt = set()
                if doc.names_offset is not None:
                    cnt = doc.u32(doc.names_offset + 0x0C)
                    arr = doc.u64(doc.names_offset + 0x20)
                    for i in range(cnt):
                        onam_rstt.add(arr + i * 16)
                is_zoneinfo = '_zoneinfo_en.lng' in e.logical_name.lower() or 'hub' in e.logical_name.lower()
                for r_off in doc.offset_sets.get('RSTT', ()):
                    if r_off in onam_rstt:
                        continue
                    s = doc.string(doc.u64(r_off))
                    if s in shaped_map and s not in KEEP_EXACT:
                        verif['untranslated_slots_remaining'] += 1
                    for ch in s:
                        cp = ord(ch)
                        if cp in (0x0A, 0x0D) or ch == '|' or (0xE000 <= cp <= 0xF8FF):
                            continue
                        used_non_pua_cps.add(cp)
                        if is_zoneinfo and cp >= 0x80:
                            used_level_title_cps.add(cp)

        # Verify all 11 UI bitmap fonts cover EVERY emitted non-PUA codepoint
        for _, logical in fonts_loc:
            glyphs, _ = extract_bitmap_font_glyphs(pkg_arc.read(logical))
            missing = sorted(hex(cp) for cp in used_non_pua_cps if cp != 0x20 and cp not in glyphs)
            if missing:
                verif['missing_glyphs_by_font'][logical] = missing

        # Verify VFX font codepoints
        vfx_cps = extract_vfx_codepoints(pkg_arc.read('vfxFonts/Vfx_Text_Character_Infos.igz'))
        verif['vfx_missing_arabic_cps'] = sorted(hex(cp) for cp in used_level_title_cps if cp not in vfx_cps)

        # Render simulated in-game visual proof directly from update.pak atlases + .lng bytes
        info_glyphs, info_atlas = extract_bitmap_font_glyphs(pkg_arc.read('fonts/ProximaNova-Info.igz'))
        title_glyphs, title_atlas = extract_bitmap_font_glyphs(pkg_arc.read('fonts/ProximaNova-Title.igz'))
        geek_glyphs, geek_atlas = extract_bitmap_font_glyphs(pkg_arc.read('fonts/GeekSpeak.igz'))
        zoinks_glyphs, zoinks_atlas = extract_bitmap_font_glyphs(pkg_arc.read('fonts/zoinks.igz'))

        def first_line_from_lng(logical_lng: str, en_key: str) -> str:
            vis = shaped_map[en_key]
            # Confirm it actually lives inside the packed .lng inside update.pak!
            d_lng = IgzDoc(pkg_arc.read(logical_lng))
            vals = {d_lng.string(d_lng.u64(r)) for r in d_lng.offset_sets.get('RSTT', ())}
            assert vis in vals, f'{logical_lng} missing packed translation for {en_key!r}'
            return vis.replace('\r\n', '\n').split('\n')[0].split('|')[0]

        demos = [
            ('Title (ProximaNova-Title)', title_glyphs, title_atlas,
             first_line_from_lng('strings/pcPlatformStrings_en.lng', 'Crash Bandicoot 2: Cortex Strikes Back')),
            ('Menu (GeekSpeak)', geek_glyphs, geek_atlas,
             first_line_from_lng('ui/Crash_Main_Menu_en.lng', 'NEW GAME') + '   |   ' +
             first_line_from_lng('ui/Crash_Save_Load_en.lng', 'LOAD GAME') + '   |   ' +
             first_line_from_lng('ui/Crash_Main_Menu_en.lng', 'OPTIONS')),
            ('HUD (zoinks)', zoinks_glyphs, zoinks_atlas,
             first_line_from_lng('loosedata/guisystemdata_en.lng', 'PAUSED') + '   —   ' +
             first_line_from_lng('ui/GuiSharedAssets/Mack/Comp_PressToContinue_en.lng', 'PRESS \ue000 TO CONTINUE')),
            ('Hint (ProximaNova-Info)', info_glyphs, info_atlas,
             first_line_from_lng('maps/Crash1/L104_Boulders/L104_Boulders_zoneInfo_en.lng',
                                 ' Break all of the Boxes in a level to earn a Clear Gem.')),
            ('Tooltip (ProximaNova-Info)', info_glyphs, info_atlas,
             first_line_from_lng('loosedata/guisystemdata_en.lng',
                                 'This uses FXAA to smooth out jagged edges on the screen.|FXAA is turned off.|Low quality FXAA is used.|Medium quality FXAA is used.|High quality FXAA is used.')),
            ('Legal (ProximaNova-Info)', info_glyphs, info_atlas,
             first_line_from_lng('ui/legal_en.lng',
                                 '© 2018 Activision Publishing, Inc. ACTIVISION, CRASH and CRASH BANDICOOT are trademarks of Activision Publishing, Inc.')),
            ('Remap {0}->{1} (ProximaNova-Info)', info_glyphs, info_atlas,
             first_line_from_lng('strings/pcPlatformStrings_en.lng', 'Remap "{0}" to {1}?')),
        ]
        strips = [(lbl, render_bitmap_line(txt, g, atl)) for lbl, g, atl, txt in demos]
        max_w = max(im.width for _, im in strips) + 260
        tot_h = sum(im.height + 8 for _, im in strips) + 16
        sheet = Image.new('RGBA', (max_w, tot_h), (14, 18, 26, 255))
        draw = ImageDraw.Draw(sheet)
        cy = 8
        for lbl, im in strips:
            draw.text((10, cy + 12), lbl, fill=(140, 210, 255, 255))
            sheet.alpha_composite(im, (240, cy))
            cy += im.height + 8
        sim_path = os.path.join(LOGS_DIR, 'simulated_render_check.png')
        sheet.save(sim_path)

    with open(os.path.join(LOGS_DIR, 'build_verification.json'), 'w', encoding='utf-8') as f:
        json.dump(verif, f, ensure_ascii=False, indent=2)

    print('[6/6] Verification:', json.dumps(verif, ensure_ascii=False))
    assert verif['readback_mismatches'] == 0
    assert verif['igz_parse_errors'] == 0
    assert verif['untranslated_slots_remaining'] == 0
    # Note: report any missing glyphs in ProximaNova/GeekSpeak/zoinks loudly
    if verif['missing_glyphs_by_font']:
        print('WARNING missing_glyphs_by_font:', verif['missing_glyphs_by_font'])
    if verif['vfx_missing_arabic_cps']:
        print('WARNING vfx_missing_arabic_cps:', len(verif['vfx_missing_arabic_cps']), verif['vfx_missing_arabic_cps'][:12])


if __name__ == '__main__':
    main()
