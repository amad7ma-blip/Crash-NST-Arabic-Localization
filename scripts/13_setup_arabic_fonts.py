import json, os, urllib.request
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONT_DIR = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic\workspace\tools\fonts'
os.makedirs(FONT_DIR, exist_ok=True)

files = {
    'Cairo[slnt,wght].ttf': 'https://raw.githubusercontent.com/google/fonts/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf',
    'Changa[wght].ttf': 'https://raw.githubusercontent.com/google/fonts/main/ofl/changa/Changa%5Bwght%5D.ttf',
}

for fn, url in files.items():
    dst = os.path.join(FONT_DIR, fn)
    if not os.path.exists(dst) or os.path.getsize(dst) == 0:
        urllib.request.urlretrieve(url, dst)
    print(fn, os.path.getsize(dst))

# Instantiate static weights!
# Cairo: slnt=0, wght=700 (Bold) & wght=800 (ExtraBold) & wght=600 (SemiBold)
cairo_var = TTFont(os.path.join(FONT_DIR, 'Cairo[slnt,wght].ttf'))
print('Cairo axes:', [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in cairo_var['fvar'].axes])
for w, name in [(600, 'Cairo-SemiBold.ttf'), (700, 'Cairo-Bold.ttf'), (800, 'Cairo-ExtraBold.ttf')]:
    inst = instancer.instantiateVariableFont(cairo_var, {'wght': w, 'slnt': 0})
    inst.save(os.path.join(FONT_DIR, name))

# Changa: wght=700 (Bold) & wght=800 (ExtraBold)
changa_var = TTFont(os.path.join(FONT_DIR, 'Changa[wght].ttf'))
print('Changa axes:', [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in changa_var['fvar'].axes])
for w, name in [(700, 'Changa-Bold.ttf'), (800, 'Changa-ExtraBold.ttf')]:
    inst = instancer.instantiateVariableFont(changa_var, {'wght': w})
    inst.save(os.path.join(FONT_DIR, name))

# Check Arabic + Presentation Forms-B cmap coverage in Cairo-Bold & Changa-ExtraBold
for fn in ['Cairo-Bold.ttf', 'Changa-ExtraBold.ttf']:
    tt = TTFont(os.path.join(FONT_DIR, fn))
    cmap = tt.getBestCmap()
    ar_base = [cp for cp in range(0x0621, 0x064B) if cp in cmap]
    ar_pfb = [cp for cp in range(0xFE80, 0xFEFD) if cp in cmap]
    ar_punct = [hex(cp) for cp in (0x060C, 0x061B, 0x061F, 0x0640) if cp in cmap]
    print(f'{fn}: upm={tt["head"].unitsPerEm}, base(0621..064A)={len(ar_base)}/42, pfb(FE80..FEFC)={len(ar_pfb)}/125, punct={ar_punct}')
    missing_pfb = [hex(cp) for cp in range(0xFE80, 0xFEFD) if cp not in cmap and cp not in (0xFEF3, 0xFEF4)]
    print(f'  missing in FE80..FEFC ({len(missing_pfb)}):', missing_pfb[:20])
