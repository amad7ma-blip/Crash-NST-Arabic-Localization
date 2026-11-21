import json, os, re, sys

WS = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic'
sys.path.insert(0, os.path.join(WS, 'workspace', 'scripts'))
from translations_part1 import KEEP_EXACT, TRANS_PART1
from translations_part2 import TRANS_PART2

inv = json.load(open(os.path.join(WS, 'workspace', 'extracted', 'master_inventory.json'), encoding='utf-8'))['items']

all_trans = {}
all_trans.update(TRANS_PART1)
all_trans.update(TRANS_PART2)

missing = []
ph_mismatch = []
PLACEHOLDER_RE = re.compile(r'(\{[0-9]+\}|%[0-9.]*[sdifcx%]|%llu|[\uE000-\uF8FF])')

for it in inv:
    en = it['en']
    if en in KEEP_EXACT:
        continue
    if en not in all_trans:
        missing.append({'id': it['id'], 'cat': it['category'], 'en': en, 'ctx': it['occurrences'][0]['logical']})
    else:
        ar = all_trans[en]
        en_ph = sorted(PLACEHOLDER_RE.findall(en))
        ar_ph = sorted(PLACEHOLDER_RE.findall(ar))
        if en_ph != ar_ph:
            ph_mismatch.append({'id': it['id'], 'en': en, 'ar': ar, 'en_ph': en_ph, 'ar_ph': ar_ph})

print(f'Total items: {len(inv)}, KEEP_EXACT hit: {sum(1 for i in inv if i["en"] in KEEP_EXACT)}, Translated: {sum(1 for i in inv if i["en"] in all_trans)}, Missing: {len(missing)}, PH mismatch: {len(ph_mismatch)}')
if missing:
    print('MISSING:', json.dumps(missing[:30], indent=2, ensure_ascii=False))
if ph_mismatch:
    print('PH MISMATCH:', json.dumps(ph_mismatch, indent=2, ensure_ascii=False))
