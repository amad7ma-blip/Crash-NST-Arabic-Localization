"""Build complete Arabic localization update.pak (UI + all 14 spoken cinematics) and verify."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

WS = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic'
GAME_ARCH = r'C:\Program Files (x86)\Steam\steamapps\common\Crash Bandicoot - N Sane Trilogy\archives'
PKG_DIR = os.path.join(WS, 'package')
PKG_DATA = os.path.join(PKG_DIR, 'data')
LOGS_DIR = os.path.join(WS, 'workspace', 'logs')
EXTRACTED_DIR = os.path.join(WS, 'workspace', 'extracted')
REPORTS_DIR = os.path.join(WS, 'reports')

sys.path.insert(0, os.path.join(WS, 'workspace', 'scripts'))
from nst_alchemy import IgaArchiveV11, IgzDoc, build_iga_v11
from cutscene_subtitles_builder import build_cutscene_subtitle_entries, build_shot_ui_igz
from cutscene_subtitles_data import (
    ALL_CUTSCENE_GROUPS,
    ALL_CUTSCENE_SPECS,
    TALKING_HEAD_AND_BOSS_DIALOGUES,
)

# Reuse bitmap font glyph extraction & renderer from main UI localization builder
_spec = importlib.util.spec_from_file_location(
    'build27', os.path.join(WS, 'workspace', 'scripts', '27_build_full_arabic_update.py')
)
_b27 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b27)


def test_shot_ui_roundtrip():
    """Verify build_shot_ui_igz preserves extra cues such as Crash2_Intro Shot02 Cinematic_Text."""
    with IgaArchiveV11(os.path.join(GAME_ARCH, 'Crash2_Intro_Cinematic.pak')) as a2:
        orig_raw = a2.read('cutscene/2017/Crash2/Crash2_Intro_Cinematic/Crash2_Intro_Cinematic_Shot02_ui.igz')
    orig_doc = IgzDoc(orig_raw)
    rebuilt_raw = build_shot_ui_igz(orig_raw, [(16.466667, 'Cinematic_Text')], 'Test02')
    reb_doc = IgzDoc(rebuilt_raw)
    assert sorted(reb_doc.objects.values()) == sorted(orig_doc.objects.values()), 'Object types mismatch'
    assert reb_doc.strings[0] == 'Cinematic_Text'
    assert reb_doc.u32(reb_doc.root_offset + 0x10) == 3
    print('[1/6] Shot02_ui roundtrip check PASSED:', len(rebuilt_raw), 'bytes (orig', len(orig_raw), 'bytes)')


def verify_c2_shot02_preserved(raw_igz: bytes):
    """Ensure Crash2_Intro_Cinematic_Shot02_ui.igz still triggers Cinematic_Text alongside Arabic cues."""
    doc = IgzDoc(raw_igz)
    for required in ('Cinematic_Text', 'Sub_C2_Intro_02', 'Sub_C2_Intro_03'):
        assert required in doc.strings, f'Missing {required} in Crash2_Intro Shot02_ui: {doc.strings}'


def write_bilingual_report(cue_meta: dict):
    """Export full bilingual report covering 15 cinematics (14 spoken + 1 silent) & 48 _LOC_ lines."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    # Load observed durations if available
    dur_map = {}
    dx_path = os.path.join(LOGS_DIR, 'dialogue_durations_and_xrefs.json')
    if os.path.exists(dx_path):
        try:
            dx = json.load(open(dx_path, encoding='utf-8'))
            if isinstance(dx, dict):
                items = dx.get('dialogues') or dx.get('clips') or dx
                if isinstance(items, dict):
                    for k, v in items.items():
                        if isinstance(v, dict) and 'duration_s' in v:
                            dur_map[k] = v['duration_s']
                        elif isinstance(v, dict) and 'duration' in v:
                            dur_map[k] = v['duration']
                elif isinstance(items, list):
                    for it in items:
                        if isinstance(it, dict) and 'id' in it:
                            dur_map[it['id']] = it.get('duration_s') or it.get('duration')
        except Exception:
            pass

    total_cues = sum(len(s['cues']) for s in ALL_CUTSCENE_SPECS)
    md = [
        '# السجل الكامل لترجمة المشاهد السينمائية والحوارات — Crash Bandicoot N. Sane Trilogy',
        '',
        '## ملخص الحالة والتغطية',
        '',
        f'- **المشاهد السينمائية المحقونة داخل اللعبة (`update.pak`)**: **14 مشهدًا ناطقًا** من أصل **15 مشهدًا** (إجمالي **{total_cues} لوحة ترجمة نصية** موزعة بدقة على **{len(ALL_CUTSCENE_SPECS)} لقطة `_ui.igz`**).',
        '- **المشهد الصامت**: `Crash1_Outro_Cinematic` صامت بالكامل (`0` أحداث حوار صوتي) ولا يتطلب ترجمة.',
        '- **الحوارات الصوتية `_LOC_` المستخرجة والمترجمة (48 مقطعًا)**: تشمل **35 حوارًا لرؤوس المحادثة (`TalkingHeads`)** في غرف الانتقال لكراش 2 وكراش 3 + **13 سطرًا لشاشات العنوان والزعماء داخل المعارك**.',
        '  - *ملاحظة تقنية حول `TalkingHeads`*: تختلف حوارات رؤوس المحادثة داخل غرف الانتقال (`L200_Hub` و`L300_Hub`) عن المشاهد السينمائية لأنها تُستدعى برمجيًا عبر عقد `VSC` ولا يمتلك محرك اللعبة نداء `CGuiEventSubtitlesShow` متصلًا بالـ VSC في النسخة الأصلية؛ ونظرًا لعدم توفر تشغيل فعلي لـ Steam أثناء البناء لاختبار حقن بايتكود `VSC` في الميدان، تم الحفاظ على سلامة الـ Hubs من التلف، وإتاحة النص المترجم الكامل للجميع في هذا السجل وملفات البيانات إلى أن يتاح اختبار VSC حيًا.',
        '',
        '---',
        '',
        '## القسم الأول: المشاهد السينمائية المفعّلة داخل اللعبة (`14` مشهدًا ناطقًا)',
        '',
    ]

    for idx, grp in enumerate(ALL_CUTSCENE_GROUPS, 1):
        md.append(f"### {idx}. {grp['title_ar']} (`{grp['archive']}` — {grp['game']})")
        md.append('')
        md.append('| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |')
        md.append('|---|---:|---|---|---|')
        for shot in grp['specs']:
            for cue in shot['cues']:
                t_glob = shot['shot_start_global'] + cue['t_local']
                t_end = t_glob + cue['dur']
                ar_flat = cue['ar'].replace('\n', ' / ')
                en_flat = cue['en'].replace('\n', ' ')
                md.append(f"| `{cue['id']}` | `{t_glob:.2f}s–{t_end:.2f}s` | {cue['speaker']} | {en_flat} | {ar_flat} |")
        md.append('')

    md.extend([
        '### 15. مشهد النهاية الحقيقية — كراش 1 (`Crash1_Outro_Cinematic.pak`)',
        '- مشهد صامت بالكامل (`0` أحداث صوتية كلامية).',
        '',
        '---',
        '',
        '## القسم الثاني: الحوارات التفاعلية والزعماء (`48` مقطع `_LOC_`)',
        '',
        '### أ) حوارات رؤوس المحادثة (`TalkingHeads` — `35` مقطعًا)',
        '',
        '| المعرّف | الجزء | المتحدث | السياق | النص الإنجليزي | الترجمة العربية |',
        '|---|---|---|---|---|---|',
    ])
    for item in TALKING_HEAD_AND_BOSS_DIALOGUES:
        if item['category'] == 'TalkingHead':
            dur_str = f" ({dur_map[item['id']]:.1f}ث)" if item['id'] in dur_map and dur_map[item['id']] else ''
            md.append(
                f"| `{item['id']}` | {item['game']} | {item['speaker_ar']} | {item['context']}{dur_str} | {item['en']} | {item['ar']} |"
            )

    md.extend([
        '',
        '### ب) عبارات شاشات العنوان والزعماء داخل المعارك (`13` مقطعًا)',
        '',
        '| المعرّف | الجزء | المتحدث | السياق | النص الإنجليزي | الترجمة العربية |',
        '|---|---|---|---|---|---|',
    ])
    for item in TALKING_HEAD_AND_BOSS_DIALOGUES:
        if item['category'] != 'TalkingHead':
            md.append(
                f"| `{item['id']}` | {item['game']} | {item['speaker_ar']} | {item['context']} | {item['en']} | {item['ar']} |"
            )

    report_md_path = os.path.join(REPORTS_DIR, 'DIALOGUES_AND_CUTSCENES_AR.md')
    with open(report_md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')

    json_out_path = os.path.join(LOGS_DIR, 'cutscenes_and_dialogues_ar.json')
    with open(json_out_path, 'w', encoding='utf-8') as f:
        json.dump(
            {
                'cutscenes': ALL_CUTSCENE_GROUPS,
                'dialogues_loc': TALKING_HEAD_AND_BOSS_DIALOGUES,
                'stats': cue_meta,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f'[5/6] Wrote bilingual reports: {report_md_path} and {json_out_path}')
    return report_md_path, json_out_path


def main():
    os.makedirs(LOGS_DIR, exist_ok=True)
    test_shot_ui_roundtrip()

    base_pak = os.path.join(EXTRACTED_DIR, 'update_ui_base.pak')
    assert os.path.exists(base_pak), f'Missing base UI pak: {base_pak}'

    # Load all existing UI/font/LNG/texture entries from clean UI base (434 entries)
    merged: dict[str, bytes] = {}
    with IgaArchiveV11(base_pak) as ba:
        for e in ba.entries:
            merged[e.logical_name] = ba.read_entry(e)
    base_count = len(merged)
    print(f'[2/6] Loaded {base_count} base UI/font/texture entries from update_ui_base.pak')

    # Generate all 14 spoken cinematics' subtitle assets, Shot *_ui.igz files, and permanent domains
    sub_entries, used_cps = build_cutscene_subtitle_entries(
        GAME_ARCH,
        ALL_CUTSCENE_SPECS,
        font_name='GeekSpeak_Outline',
        scale=0.45,
        y_pos=375.0,
        wrap_width=54,
    )
    print(f'[3/6] Generated {len(sub_entries)} cutscene subtitle/shot/domain entries ({len(used_cps)} unique codepoints)')

    # Verify ZERO missing glyphs in fonts/GeekSpeak_Outline.igz across all 96 cues!
    glyphs, atlas = _b27.extract_bitmap_font_glyphs(merged['fonts/GeekSpeak_Outline.igz'])
    missing = sorted((cp, hex(cp), chr(cp)) for cp in used_cps if cp not in glyphs)
    assert not missing, f'Missing glyphs in GeekSpeak_Outline.igz: {missing}'

    merged.update(sub_entries)

    # Explicitly verify Crash2_Intro_Cinematic_Shot02_ui.igz still preserves 'Cinematic_Text'
    c2_s2_key = 'cutscene/2017/Crash2/Crash2_Intro_Cinematic/Crash2_Intro_Cinematic_Shot02_ui.igz'
    verify_c2_shot02_preserved(merged[c2_s2_key])

    # Build package/data/update.pak
    os.makedirs(PKG_DATA, exist_ok=True)
    out_pak = os.path.join(PKG_DATA, 'update.pak')
    build_iga_v11(merged, out_pak, compress=True)
    pak_size = os.path.getsize(out_pak)
    pak_sha = _b27.sha256_file(out_pak)

    # Update package/manifest.json with new version, size, and SHA-256
    manifest_path = os.path.join(PKG_DIR, 'manifest.json')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    manifest['version'] = '1.1.0'
    manifest['update_pak_size'] = pak_size
    manifest['update_pak_sha256'] = pak_sha
    manifest['cutscene_subtitles_count'] = sum(len(s['cues']) for s in ALL_CUTSCENE_SPECS)
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'[4/6] Built {out_pak} ({len(merged)} entries, {pak_size:,} B, sha256={pak_sha}) & updated manifest.json')

    # Install using official Install-Arabic.ps1 (also tests installer SHA-256 verification & marker update!)
    ps1_path = os.path.join(PKG_DIR, 'Install-Arabic.ps1')
    game_root = os.path.dirname(GAME_ARCH)
    res = subprocess.run(
        ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps1_path, '-GameDir', game_root, '-Yes', '-NoPause'],
        capture_output=True,
        text=True,
        encoding='utf-8',
    )
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        raise RuntimeError(f'Install-Arabic.ps1 failed with exit code {res.returncode}')

    dst_pak = os.path.join(GAME_ARCH, 'update.pak')
    assert _b27.sha256_file(dst_pak) == pak_sha, 'Installed update.pak SHA mismatch!'

    # Full read-back audit directly from installed game archives/update.pak!
    strips = []
    parsed_shot_uis = 0
    parsed_sub_ui = 0
    parsed_sub_lng = 0
    with IgaArchiveV11(dst_pak) as ua:
        assert len(ua.entries) == len(merged)
        dom_check = IgzDoc(ua.read('UI/Domains/juicedomain_permanent.igz'))
        pkg_check = IgzDoc(ua.read('packages/generated/UI/Domains/juicedomain_permanent_pkg.igz'))
        verify_c2_shot02_preserved(ua.read(c2_s2_key))

        # Verify all 14 spoken cinematics' shots and cues
        for grp in ALL_CUTSCENE_GROUPS:
            sample_added = False
            for shot in grp['specs']:
                s_doc = IgzDoc(ua.read(shot['shot_ui_logical']))
                parsed_shot_uis += 1
                for cue in shot['cues']:
                    nm = cue['id']
                    assert nm in s_doc.strings, f'Cue {nm} missing from shot UI {shot["shot_ui_logical"]}'
                    _ = IgzDoc(ua.read(f'ui/{nm}.igz'))
                    parsed_sub_ui += 1
                    lng_doc = IgzDoc(ua.read(f'ui/{nm}_en.lng'))
                    parsed_sub_lng += 1
                    vis_text = lng_doc.strings[0]
                    assert f'UI/{nm}.igz' in dom_check.strings, f'{nm} missing from juicedomain_permanent.igz'
                    assert f'ui/{nm.lower()}.igz' in pkg_check.strings, f'{nm} missing from pkg igz'
                    assert f'ui/{nm.lower()}_en.lng' in pkg_check.strings, f'{nm} lng missing from pkg'

                    # Sample 1 representative cue per cutscene + Crash2 "One year Later" preservation check
                    if not sample_added:
                        sample_added = True
                        lines = vis_text.split('\n')
                        line_imgs = [_b27.render_bitmap_line(ln, glyphs, atlas) for ln in lines]
                        w = max(im.width for im in line_imgs)
                        h = sum(im.height - 10 for im in line_imgs) + 12
                        box = Image.new('RGBA', (w, h), (18, 22, 32, 255))
                        cy = 0
                        for im in line_imgs:
                            box.alpha_composite(im, ((w - im.width) // 2, cy))
                            cy += im.height - 10
                        strips.append((f"{grp['name']} [{nm}]", box))

        # Also check existing C2 Cinematic_Text_en.lng in update.pak (One Year Later)
        cin_lng = IgzDoc(ua.read('ui/Cinematic_Text_en.lng'))
        cin_text = cin_lng.strings[0]
        cin_imgs = [_b27.render_bitmap_line(ln, glyphs, atlas) for ln in cin_text.split('\n')]
        w = max(im.width for im in cin_imgs)
        h = sum(im.height - 10 for im in cin_imgs) + 12
        cbox = Image.new('RGBA', (w, h), (18, 22, 32, 255))
        cy = 0
        for im in cin_imgs:
            cbox.alpha_composite(im, ((w - im.width) // 2, cy))
            cy += im.height - 10
        strips.append(('Cinematic_Text [C2 Intro S02 preserved]', cbox))

    sheet_w = max(im.width for _, im in strips) + 390
    sheet_h = sum(im.height + 10 for _, im in strips) + 20
    sheet = Image.new('RGBA', (sheet_w, sheet_h), (12, 16, 24, 255))
    draw = ImageDraw.Draw(sheet)
    cy = 10
    for lbl, im in strips:
        draw.text((12, cy + 16), lbl, fill=(140, 215, 255, 255))
        sheet.alpha_composite(im, (375, cy))
        cy += im.height + 10
    strip_path = os.path.join(LOGS_DIR, 'all_cutscenes_sample_strip.png')
    sheet.save(strip_path)

    stats = {
        'base_ui_entries': base_count,
        'total_pak_entries': len(merged),
        'pak_size_bytes': pak_size,
        'pak_sha256': pak_sha,
        'spoken_cutscenes_count': len(ALL_CUTSCENE_GROUPS),
        'shot_ui_igz_patched': parsed_shot_uis,
        'subtitle_cues_injected': parsed_sub_ui,
        'subtitle_lng_injected': parsed_sub_lng,
        'unique_arabic_codepoints': len(used_cps),
        'missing_glyphs': missing,
        'talking_heads_transcribed_and_translated': sum(
            1 for d in TALKING_HEAD_AND_BOSS_DIALOGUES if d['category'] == 'TalkingHead'
        ),
        'boss_and_title_loc_transcribed_and_translated': sum(
            1 for d in TALKING_HEAD_AND_BOSS_DIALOGUES if d['category'] != 'TalkingHead'
        ),
        'sample_strip_png': strip_path,
        'installer_exit_code': res.returncode,
    }
    report_md_path, json_out_path = write_bilingual_report(stats)

    build_report_path = os.path.join(LOGS_DIR, 'all_cutscenes_build_report.json')
    with open(build_report_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f'[6/6] FULL READ-BACK VERIFICATION PASSED!')
    print('BUILD REPORT:', json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
