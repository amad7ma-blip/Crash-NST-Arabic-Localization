"""Generate package/manifest.json from verified build and original SHA-256 baseline."""
import json
import os

WS = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic'
BACKUPS_JSON = os.path.join(WS, 'backups', 'original_hashes.json')
VERIF_JSON = os.path.join(WS, 'workspace', 'logs', 'build_verification.json')
PKG_MANIFEST = os.path.join(WS, 'package', 'manifest.json')

CORE_FILES = [
    'CrashBandicootNSaneTrilogy.exe',
    'build.xml',
    'archives/languagestartup.pak',
    'archives/legal.pak',
    'archives/permanent.pak',
    'archives/permanent_pc.pak',
    'archives/juicedomain_permanent.pak',
    'archives/LooseFiles.pak',
    'archives/essentialui.pak',
    'archives/4ktextures_essentialui.pak',
    'archives/LoadingScreen_Crash.pak',
    'archives/JuiceDomain_Story.pak',
    'archives/C1_StartScreen.pak',
    'archives/L200_Hub.pak',
]


def main():
    orig = json.load(open(BACKUPS_JSON, encoding='utf-8'))
    verif = json.load(open(VERIF_JSON, encoding='utf-8'))

    assert verif['readback_mismatches'] == 0
    assert verif['igz_parse_errors'] == 0
    assert verif['untranslated_slots_remaining'] == 0
    assert not verif['missing_glyphs_by_font'], verif['missing_glyphs_by_font']

    core_hashes = {}
    for rel in CORE_FILES:
        assert rel in orig['files'], f'Missing baseline hash for {rel}'
        core_hashes[rel] = orig['files'][rel]['sha256']

    manifest = {
        'name': 'Crash Bandicoot N. Sane Trilogy - Arabic Localization',
        'version': '1.0.0',
        'author': 'V7dt1 / axxx503',
        'target_exe': 'CrashBandicootNSaneTrilogy.exe',
        'override_relpath': 'archives\\update.pak',
        'update_pak_size': verif['pak_size_bytes'],
        'update_pak_sha256': verif['pak_sha256'],
        'baseline_file_count': orig['file_count'],
        'core_original_hashes': core_hashes,
        'fonts_used': [
            {'name': 'Cairo', 'license': 'SIL Open Font License 1.1'},
            {'name': 'Changa', 'license': 'SIL Open Font License 1.1'},
        ],
    }
    with open(PKG_MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f'Wrote {PKG_MANIFEST} ({len(core_hashes)} core hashes, pak sha256={verif["pak_sha256"][:16]}...)')


if __name__ == '__main__':
    main()
