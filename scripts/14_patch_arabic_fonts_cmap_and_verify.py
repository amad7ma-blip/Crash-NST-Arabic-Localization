import os
import freetype
import arabic_reshaper
from bidi.algorithm import get_display
from fontTools.ttLib import TTFont
from PIL import Image

FONT_DIR = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic\workspace\tools\fonts'
OUT_DIR = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic\workspace\logs\font_previews'

# Exact 36 isolated Presentation Forms-B -> Basic Arabic U+0621..U+064A mapping
ISOLATED_MAP = {
    0xFE80: 0x0621,  # ء HAMZA
    0xFE81: 0x0622,  # آ ALEF WITH MADDA ABOVE
    0xFE83: 0x0623,  # أ ALEF WITH HAMZA ABOVE
    0xFE85: 0x0624,  # ؤ WAW WITH HAMZA ABOVE
    0xFE87: 0x0625,  # إ ALEF WITH HAMZA BELOW
    0xFE89: 0x0626,  # ئ YEH WITH HAMZA ABOVE
    0xFE8D: 0x0627,  # ا ALEF
    0xFE8F: 0x0628,  # ب BEH
    0xFE93: 0x0629,  # ة TEH MARBUTA
    0xFE95: 0x062A,  # ت TEH
    0xFE99: 0x062B,  # ث THEH
    0xFE9D: 0x062C,  # ج JEEM
    0xFEA1: 0x062D,  # ح HAH
    0xFEA5: 0x062E,  # خ KHAH
    0xFEA9: 0x062F,  # د DAL
    0xFEAB: 0x0630,  # ذ THAL
    0xFEAD: 0x0631,  # ر REH
    0xFEAF: 0x0632,  # ز ZAIN
    0xFEB1: 0x0633,  # س SEEN
    0xFEB5: 0x0634,  # ش SHEEN
    0xFEB9: 0x0635,  # ص SAD
    0xFEBD: 0x0636,  # ض DAD
    0xFEC1: 0x0637,  # ط TAH
    0xFEC5: 0x0638,  # ظ ZAH
    0xFEC9: 0x0639,  # ع AIN
    0xFECD: 0x063A,  # غ GHAIN
    0xFED1: 0x0641,  # ف FEH
    0xFED5: 0x0642,  # ق QAF
    0xFED9: 0x0643,  # ك KAF
    0xFEDD: 0x0644,  # ل LAM
    0xFEE1: 0x0645,  # م MEEM
    0xFEE5: 0x0646,  # ن NOON
    0xFEE9: 0x0647,  # ه HEH
    0xFEED: 0x0648,  # و WAW
    0xFEEF: 0x0649,  # ى ALEF MAKSURA
    0xFEF1: 0x064A,  # ي YEH
}

# Every Arabic codepoint we want in our bitmap atlases:
# - U+060C (،), U+061B (؛), U+061F (؟), U+0640 (ـ), U+066A (٪)
# - U+0621..U+063A, U+0641..U+064A (logical base forms just in case)
# - U+FE80..U+FEFC (all 125 Presentation Forms-B except non-standard 0xFEF3/0xFEF4? No, include all that exist!)
REQUIRED_CPS = (
    [0x060C, 0x061B, 0x061F, 0x0640, 0x066A]
    + list(range(0x0621, 0x063B))
    + list(range(0x0641, 0x064B))
    + [cp for cp in range(0xFE80, 0xFEFD)]
)

for fn in ['Cairo-SemiBold.ttf', 'Cairo-Bold.ttf', 'Cairo-ExtraBold.ttf', 'Changa-Bold.ttf', 'Changa-ExtraBold.ttf']:
    p = os.path.join(FONT_DIR, fn)
    tt = TTFont(p)
    best = tt.getBestCmap()
    for table in tt['cmap'].tables:
        if table.isUnicode():
            for pfb, base in ISOLATED_MAP.items():
                if pfb not in table.cmap and base in best:
                    table.cmap[pfb] = best[base]
    out_p = os.path.join(FONT_DIR, fn.replace('.ttf', '-Fixed.ttf'))
    tt.save(out_p)

    # FreeType deterministic verification
    face = freetype.Face(out_p)
    missing = [hex(cp) for cp in REQUIRED_CPS if face.get_char_index(cp) == 0]
    print(f'{os.path.basename(out_p)}: missing_glyphs={len(missing)} -> {missing}')

# Visual verification: reshape + render test Arabic text with FreeType using Changa-ExtraBold-Fixed & Cairo-Bold-Fixed
sample = 'مرحباً بكم في كراش بانديكوت! لا، لأ، لإ، لآ — أ إ آ ؤ ئ ء — 123'
reshaped = arabic_reshaper.reshape(sample)
disp = get_display(reshaped, base_dir='R')
print('Sample reshaped codepoints:', [hex(ord(c)) for c in disp[:15]])

canvas = Image.new('RGBA', (1100, 180), (25, 32, 45, 255))
for row_idx, fn in enumerate(['Cairo-Bold-Fixed.ttf', 'Changa-ExtraBold-Fixed.ttf']):
    face = freetype.Face(os.path.join(FONT_DIR, fn))
    face.set_pixel_sizes(0, 44)
    pen_x = 40
    baseline_y = 60 + row_idx * 80
    for ch in disp:
        face.load_char(ch, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
        slot = face.glyph
        bmp = slot.bitmap
        if bmp.width > 0 and bmp.rows > 0:
            g_img = Image.frombytes('L', (bmp.width, bmp.rows), bytes(bmp.buffer))
            rgba = Image.new('RGBA', g_img.size, (255, 255, 255, 0))
            rgba.putalpha(g_img)
            canvas.alpha_composite(rgba, (pen_x + slot.bitmap_left, baseline_y - slot.bitmap_top))
        pen_x += slot.advance.x >> 6
canvas.save(os.path.join(OUT_DIR, 'arabic_freetype_test.png'))
print('Saved arabic_freetype_test.png')
