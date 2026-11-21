import json, os

WS = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic'
lng = json.load(open(os.path.join(WS, 'workspace', 'logs', 'en_lng_scan.json'), encoding='utf-8'))
nl = json.load(open(os.path.join(WS, 'workspace', 'logs', 'non_lng_unique.json'), encoding='utf-8'))

lng_texts = set(e['text'] for f in lng['files'] for e in f['entries'])
print('Total unique _en.lng texts:', len(lng_texts))

# Check what non_lng items have texts NOT in lng_texts and not obviously debug/placeholder
extra = []
for item in nl:
    ln = item['logical'].lower()
    if ln.startswith(('vsc/', 'renderer/', 'license/')):
        continue
    unseen = [t for t in item['texts'] if t not in lng_texts]
    if unseen:
        extra.append({'pak': item['pak'], 'logical': item['logical'], 'unseen': unseen})

with open(os.path.join(WS, 'workspace', 'logs', 'non_lng_extra.json'), 'w', encoding='utf-8') as f:
    json.dump(extra, f, indent=2, ensure_ascii=False)
print('Non-lng files with unseen texts:', len(extra))
for x in extra:
    print(f"  [{x['pak']}] {x['logical']}: {x['unseen'][:8]}")

# Also save deduplicated unique _en.lng strings list (excluding igLocalized* object names)
# Wait: check which entries are object names vs actual localized text!
real_entries = []
obj_name_entries = []
for f in lng['files']:
    for e in f['entries']:
        if e['owner'] == 'mem' and e['text'].startswith(('igLocalized', 'igObject')):
            obj_name_entries.append(e['text'])
        else:
            real_entries.append((f['pak'], f['logical'], e['owner'], e['field'], e['text']))

unique_real = sorted(set(x[4] for x in real_entries))
print('Real localized entries:', len(real_entries), 'Unique real strings:', len(unique_real))
print('Skipped ONAM object name entries:', set(obj_name_entries))
with open(os.path.join(WS, 'workspace', 'extracted', 'unique_en_strings.json'), 'w', encoding='utf-8') as f:
    json.dump([{'id': i, 'en': s} for i, s in enumerate(unique_real)], f, indent=2, ensure_ascii=False)
