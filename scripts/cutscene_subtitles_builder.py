"""Modular Alchemy IGZ/JuiceUI subtitle injector for Crash Bandicoot N. Sane Trilogy cutscenes."""
import os
import struct
import sys

from nst_alchemy import IgaArchiveV11, IgzDoc, fnv1a_lower
from arabic_shaper import shape_arabic_text

JUICE_UI_LNG_PREFIX = '<build>project:/temporary/mack/data/win64/output/ui/'


def pack_tdep(pairs: list[tuple[str, str]]) -> tuple[int, bytes]:
    """Encode TDEP dependency pairs with Alchemy's mandatory 4-byte NUL padding."""
    body = b''.join(k.encode('utf-8') + b'\0' + v.encode('utf-8') + b'\0' for k, v in pairs)
    body += b'\0' * (4 - (len(body) % 4))
    return len(pairs), body


def parse_tdep(raw_tdep: tuple[int, bytes]) -> list[tuple[str, str]]:
    """Decode TDEP pairs preserving exact key/value string order."""
    cnt, body = raw_tdep
    parts = body.split(b'\0')
    pairs = []
    idx = 0
    for _ in range(cnt):
        k = parts[idx].decode('utf-8')
        v = parts[idx + 1].decode('utf-8')
        pairs.append((k, v))
        idx += 2
    return pairs


def rehash_namelist(doc: IgzDoc) -> None:
    """Recompute FNV-1a lower hashes in ONAM igNameList after TSTR renames."""
    if doc.names_offset is None:
        return
    cnt = doc.u32(doc.names_offset + 0x10)
    arr = doc.u64(doc.names_offset + 0x20)
    for i in range(cnt):
        s_idx = doc.u64(arr + i * 16)
        s = doc.string(s_idx)
        struct.pack_into('<Q', *doc._loc(arr + i * 16 + 8), fnv1a_lower(s))


def build_subtitle_ui_igz(
    base_raw: bytes,
    ui_name: str,
    dur_s: float,
    font_name: str = 'GeekSpeak_Outline',
    scale: float = 0.45,
    y_pos: float = 375.0,
    width: float = 1600.0,
    height: float = 180.0,
) -> bytes:
    """Clone ui/Cinematic_Text.igz into a bottom-center crisp subtitle UI project."""
    doc = IgzDoc(base_raw)
    assert doc.strings[1] == 'Cinematic_Text', f'Unexpected TSTR[1]: {doc.strings[1]!r}'
    assert doc.strings[9] == 'ZoinksXL_Outline', f'Unexpected TSTR[9]: {doc.strings[9]!r}'

    # Update TSTR strings in-place so EXID/EXNM indices remain valid
    for i, s in enumerate(doc.strings):
        if s == 'Cinematic_Text':
            doc.strings[i] = ui_name
        elif s.startswith('Cinematic_Text_'):
            doc.strings[i] = f'{ui_name}_{s[len("Cinematic_Text_"):]}'
    doc.strings[9] = font_name
    rehash_namelist(doc)

    # Point English .lng dependency to Sub_<id>_en.lng while retaining shared assets
    pairs = parse_tdep(doc.fixups['TDEP'])
    new_pairs = []
    for k, v in pairs:
        if k == 'Cinematic_Text_en':
            new_pairs.append((f'{ui_name}_en', f'{JUICE_UI_LNG_PREFIX}{ui_name}_en.lng'))
        else:
            new_pairs.append((k, v))
    doc.fixups['TDEP'] = pack_tdep(new_pairs)

    # Reposition and size Text_Title placeable (0x4e0) for 1920x1080 bottom-center subtitles
    struct.pack_into('<3f', *doc._loc(0x4e0 + 0x68), 0.0, float(y_pos), 0.0)
    struct.pack_into('<2f', *doc._loc(0x4e0 + 0x98), float(width), float(height))

    # Configure igGuiText (0x950): pure solid white (gradient disabled) + subtitle scale
    struct.pack_into('<I', *doc._loc(0x950 + 0x40), 0)
    struct.pack_into('<6f', *doc._loc(0x950 + 0x44), 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    struct.pack_into('<2I', *doc._loc(0x950 + 0x5c), 2, 1)
    struct.pack_into('<f', *doc._loc(0x950 + 0x64), float(scale))
    struct.pack_into('<I', *doc._loc(0x950 + 0x68), 1)

    # Program animation duration (0x640, 0x8b0) and alpha fade keyframes (8192 ticks/sec)
    dur_s = max(0.8, float(dur_s))
    struct.pack_into('<f', *doc._loc(0x640 + 0x20), dur_s)
    struct.pack_into('<f', *doc._loc(0x8b0 + 0x20), dur_s)

    fade_in = min(0.10, dur_s * 0.25)
    fade_out_start = max(fade_in + 0.10, dur_s - 0.15)
    kf_specs = [
        (0x710, 0.0, 0.0),
        (0x748, fade_in, 1.0),
        (0x780, fade_out_start, 1.0),
        (0x7b8, dur_s, 0.0),
    ]
    for kf_off, t_sec, alpha in kf_specs:
        struct.pack_into('<I', *doc._loc(kf_off + 0x10), int(round(t_sec * 8192)))
        struct.pack_into('<f', *doc._loc(kf_off + 0x28), float(alpha))

    return doc.to_bytes()


def build_subtitle_lng_igz(base_lng_raw: bytes, ui_name: str, shaped_ar: str) -> bytes:
    """Clone ui/Cinematic_Text_en.lng with shaped RTL Arabic text for ui_name."""
    doc = IgzDoc(base_lng_raw)
    assert doc.strings[0] == 'One year Later', f'Unexpected LNG TSTR[0]: {doc.strings[0]!r}'
    assert doc.strings[1] == 'Cinematic_Text', f'Unexpected LNG TSTR[1]: {doc.strings[1]!r}'
    doc.strings[0] = shaped_ar
    doc.strings[1] = ui_name
    rehash_namelist(doc)
    return doc.to_bytes()


def build_shot_ui_igz(
    base_shot02_ui_raw: bytes,
    cues: list[tuple[float, str]],
    shot_tag: str,
) -> bytes:
    """Build a cutscene *_Shot*_ui.igz firing CCutsceneActionOpenUi at sorted local times."""
    sorted_cues = sorted(cues, key=lambda x: x[0])
    doc = IgzDoc(base_shot02_ui_raw)
    doc.strings = []
    doc.__dict__.pop('_string_index', None)
    doc.__dict__.pop('_string_count', None)
    doc.data = [bytearray()]
    doc.objects = {}
    doc.offset_sets = {'RVTB': set(), 'RSTT': set(), 'ROFS': set()}

    root_list = doc.new_object('igObjectList', align=8)
    # Pre-allocate array immediately after root_list to preserve compact layout
    n_cues = len(sorted_cues)
    all_objs_count = 2 * n_cues + 1
    obj_arr = doc.alloc(8 * all_objs_count, align=8)
    struct.pack_into('<IIII', *doc._loc(root_list + 0x10), all_objs_count, all_objs_count, 8 * all_objs_count, 0x01100000)
    doc.set_ptr(root_list + 0x20, obj_arr)

    actions = []
    for _, ui_name in sorted_cues:
        act = doc.new_object('CCutsceneActionOpenUi', align=8)
        struct.pack_into('<Q', *doc._loc(act + 0x08), 2)
        doc.set_string_ref(act + 0x18, ui_name)
        actions.append(act)

    kfs = []
    for i, (t_local_s, _) in enumerate(sorted_cues):
        kf = doc.new_object('JuiceActionKeyframe', align=8)
        struct.pack_into('<Q', *doc._loc(kf + 0x08), 2)
        struct.pack_into('<f', *doc._loc(kf + 0x10), float(t_local_s))
        doc.set_ptr(kf + 0x18, actions[i])
        kfs.append(kf)

    track = doc.new_object('JuiceActionTrack', align=8)
    struct.pack_into('<Q', *doc._loc(track + 0x08), 1)
    kf_arr = doc.alloc(8 * n_cues, align=8)
    struct.pack_into('<IIII', *doc._loc(track + 0x10), n_cues, n_cues, 8 * n_cues, 0x01100000)
    doc.set_ptr(track + 0x20, kf_arr)
    for i, kf in enumerate(kfs):
        doc.set_ptr(kf_arr + i * 8, kf)

    all_objs = actions + kfs + [track]
    for i, obj in enumerate(all_objs):
        doc.set_ptr(obj_arr + i * 8, obj)

    # Populate ONAM igNameList matching igObjectList order 1-to-1
    namelist = doc.new_object('igNameList', align=8)
    names = (
        [f'openUiAction_{shot_tag}_{i:02d}' for i in range(n_cues)]
        + [f'openUiKeyframe_{shot_tag}_{i:02d}' for i in range(n_cues)]
        + ['ui_track']
    )
    nl_arr = doc.alloc(16 * len(names), align=8)
    struct.pack_into('<IIII', *doc._loc(namelist + 0x10), len(names), len(names), 16 * len(names), 0x01100000)
    doc.set_ptr(namelist + 0x20, nl_arr)
    for i, nm in enumerate(names):
        doc.set_string_ref(nl_arr + i * 16, nm)
        struct.pack_into('<Q', *doc._loc(nl_arr + i * 16 + 8), fnv1a_lower(nm))

    doc.fixups['ROOT'] = (1, struct.pack('<I', root_list))
    doc.fixups['ONAM'] = (1, struct.pack('<I', namelist))
    doc.names_offset = namelist
    return doc.to_bytes()


def register_ui_in_permanent_domain(
    perm_igz_raw: bytes,
    perm_pkg_raw: bytes,
    ui_names: list[str],
) -> tuple[bytes, bytes]:
    """Register new UI/Sub_*.igz + *_en.lng assets inside juicedomain_permanent and its _pkg."""
    # 1. Update UI/Domains/juicedomain_permanent.igz
    dom = IgzDoc(perm_igz_raw)
    tdep_pairs = parse_tdep(dom.fixups['TDEP'])
    existing_tdep_keys = {k for k, _ in tdep_pairs}
    for nm in ui_names:
        if nm not in existing_tdep_keys:
            tdep_pairs.append((nm, f'<build>ui:/{nm}.igz'))
    tdep_pairs.sort(key=lambda kv: kv[0].lower())
    dom.fixups['TDEP'] = pack_tdep(tdep_pairs)

    sref_off = 0x68
    old_cnt = dom.u32(sref_off + 0x10)
    old_arr = dom.u64(sref_off + 0x20)
    old_refs = [dom.string(dom.u64(old_arr + i * 8)) for i in range(old_cnt)]
    for i in range(old_cnt):
        dom.offset_sets['RSTT'].discard(old_arr + i * 8)

    existing_refs = set(old_refs)
    all_refs = list(old_refs)
    for nm in ui_names:
        ref = f'UI/{nm}.igz'
        if ref not in existing_refs:
            all_refs.append(ref)
            existing_refs.add(ref)

    new_cnt = len(all_refs)
    new_arr = dom.alloc(new_cnt * 8, align=16)
    struct.pack_into('<IIII', *dom._loc(sref_off + 0x10), new_cnt, new_cnt, new_cnt * 8, 0x01100000)
    dom.set_ptr(sref_off + 0x20, new_arr)
    for i, ref in enumerate(all_refs):
        dom.set_string_ref(new_arr + i * 8, ref)

    # 2. Update packages/generated/UI/Domains/juicedomain_permanent_pkg.igz
    pkg = IgzDoc(perm_pkg_raw)
    chk_off = 0x30
    old_cnt_p = pkg.u32(chk_off + 0x28)
    old_arr_p = pkg.u64(chk_off + 0x38)
    old_pairs = []
    for i in range(old_cnt_p):
        t_s = pkg.string(pkg.u64(old_arr_p + i * 16))
        p_s = pkg.string(pkg.u64(old_arr_p + i * 16 + 8))
        old_pairs.append((t_s, p_s))
        pkg.offset_sets['RSTT'].discard(old_arr_p + i * 16)
        pkg.offset_sets['RSTT'].discard(old_arr_p + i * 16 + 8)

    existing_pkg = set(old_pairs)
    # Keep trailing ('igx_file', 'ui/domains/juicedomain_permanent.igz') at end if present
    tail_items = []
    if old_pairs and old_pairs[-1][0] == 'igx_file':
        tail_items = [old_pairs[-1]]
        all_pairs = list(old_pairs[:-1])
    else:
        all_pairs = list(old_pairs)
    for nm in ui_names:
        low = nm.lower()
        for entry_pair in (('gui_project', f'ui/{low}.igz'), ('lang_file', f'ui/{low}_en.lng')):
            if entry_pair not in existing_pkg:
                all_pairs.append(entry_pair)
                existing_pkg.add(entry_pair)
    all_pairs.extend(tail_items)

    new_cnt_p = len(all_pairs)
    new_arr_p = pkg.alloc(new_cnt_p * 16, align=16)
    struct.pack_into('<QII', *pkg._loc(chk_off + 0x28), new_cnt_p, new_cnt_p * 16, 0x01100000)
    pkg.set_ptr(chk_off + 0x38, new_arr_p)
    for i, (t_s, p_s) in enumerate(all_pairs):
        pkg.set_string_ref(new_arr_p + i * 16, t_s)
        pkg.set_string_ref(new_arr_p + i * 16 + 8, p_s)

    return dom.to_bytes(), pkg.to_bytes()


def build_cutscene_subtitle_entries(
    game_archives_dir: str,
    cutscene_specs: list[dict],
    font_name: str = 'GeekSpeak_Outline',
    scale: float = 0.45,
    y_pos: float = 375.0,
    wrap_width: int = 54,
) -> tuple[dict[str, bytes], set[int]]:
    """
    Generate all update.pak entries for a list of cutscene subtitle specifications.

    Each item in cutscene_specs:
      {
        'shot_ui_logical': 'cutscene/.../Crash1_Intro_Cinematic_Shot01_ui.igz',
        'shot_tag': 'C1IntroS01',
        'cues': [
          {'id': 'Sub_C1_Intro_01', 't_local': 1.65, 'dur': 6.70, 'ar': '...'},
          ...
        ]
      }
    """
    with IgaArchiveV11(os.path.join(game_archives_dir, 'juicedomain_permanent.pak')) as jp:
        base_ct_igz = jp.read('ui/Cinematic_Text.igz')
        base_ct_lng = jp.read('ui/Cinematic_Text_en.lng')
        perm_igz = jp.read('UI/Domains/juicedomain_permanent.igz')
        perm_pkg = jp.read('packages/generated/UI/Domains/juicedomain_permanent_pkg.igz')

    with IgaArchiveV11(os.path.join(game_archives_dir, 'Crash2_Intro_Cinematic.pak')) as c2p:
        base_shot02_ui = c2p.read('cutscene/2017/Crash2/Crash2_Intro_Cinematic/Crash2_Intro_Cinematic_Shot02_ui.igz')

    out_entries: dict[str, bytes] = {}
    ui_names: list[str] = []
    emitted_cps: set[int] = set()

    for shot in cutscene_specs:
        shot_cues = list(shot.get('extra_cues', ()))
        for cue in shot['cues']:
            ui_name = cue['id']
            dur_s = float(cue['dur'])
            shaped = shape_arabic_text(cue['ar'], wrap_width=wrap_width)
            for ch in shaped:
                cp = ord(ch)
                if cp not in (0x0A, 0x0D, 0x20):
                    emitted_cps.add(cp)

            ui_bytes = build_subtitle_ui_igz(
                base_ct_igz,
                ui_name=ui_name,
                dur_s=dur_s,
                font_name=font_name,
                scale=scale,
                y_pos=y_pos,
            )
            lng_bytes = build_subtitle_lng_igz(base_ct_lng, ui_name=ui_name, shaped_ar=shaped)

            # Verify every generated IGZ parses cleanly right away
            IgzDoc(ui_bytes)
            IgzDoc(lng_bytes)

            out_entries[f'ui/{ui_name}.igz'] = ui_bytes
            out_entries[f'ui/{ui_name}_en.lng'] = lng_bytes
            ui_names.append(ui_name)
            shot_cues.append((float(cue['t_local']), ui_name))

        shot_ui_bytes = build_shot_ui_igz(base_shot02_ui, shot_cues, shot_tag=shot['shot_tag'])
        IgzDoc(shot_ui_bytes)
        out_entries[shot['shot_ui_logical']] = shot_ui_bytes

    new_perm_igz, new_perm_pkg = register_ui_in_permanent_domain(perm_igz, perm_pkg, ui_names)
    IgzDoc(new_perm_igz)
    IgzDoc(new_perm_pkg)
    out_entries['UI/Domains/juicedomain_permanent.igz'] = new_perm_igz
    out_entries['packages/generated/UI/Domains/juicedomain_permanent_pkg.igz'] = new_perm_pkg

    return out_entries, emitted_cps
