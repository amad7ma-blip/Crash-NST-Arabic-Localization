"""Build Arabic bitmap glyph strips and inject them into Crash NST igBitmapFont (.igz) files."""
import math
import os
import struct
import freetype
from PIL import Image

from nst_alchemy import IgzDoc

FONT_DIR = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic\workspace\tools\fonts'

# Per-font visual specifications measured directly from the original atlases
FONT_SPECS = {
    'fonts/ProximaNova-Info.igz': {
        'ttf': os.path.join(FONT_DIR, 'Cairo-Bold-Fixed.ttf'),
        'cell_h': 65,
        'baseline_y': 47,
        'px_size': 44,
        'outline': 0.0,
    },
    'fonts/ProximaNova-Title.igz': {
        'ttf': os.path.join(FONT_DIR, 'Cairo-Bold-Fixed.ttf'),
        'cell_h': 107,
        'baseline_y': 78,
        'px_size': 74,
        'outline': 0.0,
    },
    'fonts/GeekSpeak.igz': {
        'ttf': os.path.join(FONT_DIR, 'Changa-Bold-Fixed.ttf'),
        'cell_h': 106,
        'baseline_y': 78,
        'px_size': 62,
        'outline': 0.0,
    },
    'fonts/GeekSpeak4K.igz': {
        'ttf': os.path.join(FONT_DIR, 'Changa-Bold-Fixed.ttf'),
        'cell_h': 106,
        'baseline_y': 78,
        'px_size': 62,
        'outline': 0.0,
    },
    'fonts/GeekSpeak_Outline.igz': {
        'ttf': os.path.join(FONT_DIR, 'Changa-Bold-Fixed.ttf'),
        'cell_h': 106,
        'baseline_y': 78,
        'px_size': 62,
        'outline': 3.5,
    },
    'fonts/GeekSpeak_Outline4K.igz': {
        'ttf': os.path.join(FONT_DIR, 'Changa-Bold-Fixed.ttf'),
        'cell_h': 106,
        'baseline_y': 78,
        'px_size': 62,
        'outline': 3.5,
    },
    'fonts/zoinks.igz': {
        'ttf': os.path.join(FONT_DIR, 'Changa-ExtraBold-Fixed.ttf'),
        'cell_h': 104,
        'baseline_y': 76,
        'px_size': 65,
        'outline': 3.8,
    },
    'fonts/Zoinks_Outline.igz': {
        'ttf': os.path.join(FONT_DIR, 'Changa-ExtraBold-Fixed.ttf'),
        'cell_h': 104,
        'baseline_y': 76,
        'px_size': 65,
        'outline': 4.5,
    },
    'fonts/Zoinks_Outline4K.igz': {
        'ttf': os.path.join(FONT_DIR, 'Changa-ExtraBold-Fixed.ttf'),
        'cell_h': 104,
        'baseline_y': 76,
        'px_size': 65,
        'outline': 4.5,
    },
    'fonts/zoinksXL.igz': {
        'ttf': os.path.join(FONT_DIR, 'Changa-ExtraBold-Fixed.ttf'),
        'cell_h': 258,
        'baseline_y': 190,
        'px_size': 164,
        'outline': 0.0,
    },
    'fonts/ZoinksXL_Outline.igz': {
        'ttf': os.path.join(FONT_DIR, 'Changa-ExtraBold-Fixed.ttf'),
        'cell_h': 258,
        'baseline_y': 190,
        'px_size': 164,
        'outline': 8.0,
    },
}

ARABIC_CODEPOINTS = (
    [0x060C, 0x061B, 0x061F, 0x0640, 0x066A]
    + list(range(0x0621, 0x063B))
    + list(range(0x0641, 0x064B))
    + list(range(0x0660, 0x066A))
    + list(range(0xFE80, 0xFEFD))
    + [0x002C, 0x003D, 0x007B, 0x007D, 0x00A9, 0x00AB, 0x00BB, 0x2013, 0x2014, 0x2026]
)


def render_glyph_rgba(face: freetype.Face, stroker, cp: int, cell_h: int, baseline_y: int, outline_r: float):
    """Render one glyph into an RGBA Image of height cell_h.

    Returns (pil_image, kern_left, kern_right, advance_x).
    """
    gid = face.get_char_index(cp)
    if gid == 0:
        raise ValueError(f'Missing glyph for U+{cp:04X}')

    # Measure advance and filled bitmap
    face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
    slot = face.glyph
    adv_x = slot.metrics.horiAdvance / 64.0
    fill_bmp = slot.bitmap
    f_w, f_h = fill_bmp.width, fill_bmp.rows
    f_left, f_top = slot.bitmap_left, slot.bitmap_top
    f_buf = bytes(fill_bmp.buffer)

    if outline_r > 0.0 and f_w > 0 and f_h > 0:
        face.load_glyph(gid, freetype.FT_LOAD_NO_BITMAP)
        g_obj = face.glyph.get_glyph()
        g_obj.stroke(stroker, True)
        b_obj = g_obj.to_bitmap(freetype.FT_RENDER_MODE_NORMAL, freetype.Vector(0, 0), True)
        s_bmp = b_obj.bitmap
        s_w, s_h = s_bmp.width, s_bmp.rows
        s_left, s_top = b_obj.left, b_obj.top
        s_buf = bytes(s_bmp.buffer)
    else:
        s_w = s_h = s_left = s_top = 0
        s_buf = b''

    # Determine bounding box inside cell
    min_x = min(0, f_left, s_left if s_w else 0)
    max_x = max(math.ceil(adv_x), f_left + f_w, (s_left + s_w) if s_w else 0)
    pad_l = max(1, int(math.ceil(outline_r)) + 1)
    pad_r = max(1, int(math.ceil(outline_r)) + 1)
    origin_x = pad_l - min_x
    cell_w = max(1, (max_x - min_x) + pad_l + pad_r)

    # Check vertical fit and clamp baseline shift only if extreme glyph exceeds bounds
    top_y = baseline_y - max(f_top if f_h else 0, s_top if s_h else 0)
    bot_y = baseline_y + max((f_h - f_top) if f_h else 0, (s_h - s_top) if s_h else 0)
    adj_base = baseline_y
    if top_y < 0:
        adj_base += -top_y
    elif bot_y > cell_h:
        adj_base -= (bot_y - cell_h)

    # Composite into cell RGBA buffer
    # Build grayscale layers for stroke and fill
    fill_layer = Image.new('L', (cell_w, cell_h), 0)
    if f_w > 0 and f_h > 0:
        f_img = Image.frombytes('L', (f_w, f_h), f_buf)
        fill_layer.paste(f_img, (origin_x + f_left, adj_base - f_top))

    if s_w > 0 and s_h > 0:
        stroke_layer = Image.new('L', (cell_w, cell_h), 0)
        s_img = Image.frombytes('L', (s_w, s_h), s_buf)
        stroke_layer.paste(s_img, (origin_x + s_left, adj_base - s_top))
        # Alpha composite white (255,255,255, fill) over black (0,0,0, stroke)
        black = Image.new('RGBA', (cell_w, cell_h), (0, 0, 0, 0))
        black.putalpha(stroke_layer)
        white = Image.new('RGBA', (cell_w, cell_h), (255, 255, 255, 0))
        white.putalpha(fill_layer)
        cell_img = Image.alpha_composite(black, white)
    else:
        cell_img = Image.new('RGBA', (cell_w, cell_h), (255, 255, 255, 0))
        cell_img.putalpha(fill_layer)

    # kernLeft shifts draw X by -origin_x so ink origin sits at pen_x
    # kernRight ensures kernLeft + cell_w + kernRight == adv_x!
    kern_left = float(-origin_x)
    kern_right = float(adv_x - (cell_w - origin_x))
    return cell_img, kern_left, kern_right, float(cell_w)


def patch_font_igz(raw_igz: bytes, logical_name: str, preview_path: str | None = None) -> tuple[bytes, dict]:
    spec = FONT_SPECS[logical_name]
    doc = IgzDoc(raw_igz)

    # Find igBitmapFont, igImage2 list, igCharMetricsList #0
    font_off = next(off for off, t in sorted(doc.objects.items()) if t == 'igBitmapFont')
    img_offs = [off for off, t in sorted(doc.objects.items()) if t == 'igImage2']
    img0_off = img_offs[0]
    img1_off = img_offs[1] if len(img_offs) > 1 else None

    cm_list0_off = doc.u64(font_off + 0x50)
    assert doc.objects[cm_list0_off] == 'igCharMetricsList'

    old_w, old_h = struct.unpack_from('<HH', doc.data[img0_off >> 27], (img0_off & 0x7FFFFFF) + 0x18)
    old_sz0 = doc.u32(img0_off + 0x38)
    assert old_sz0 == old_w * old_h * 4

    # Read existing char metrics in list #0
    old_cnt = doc.u32(cm_list0_off + 0x10)
    old_arr_ptr = doc.u64(cm_list0_off + 0x20)
    old_arr_sec, old_arr_off = old_arr_ptr >> 27, old_arr_ptr & 0x7FFFFFF
    existing_cm_ptrs = list(struct.unpack_from(f'<{old_cnt}Q', doc.data[old_arr_sec], old_arr_off))
    existing_cps = {doc.u32(p + 0x10) for p in existing_cm_ptrs}

    # Render new Arabic glyphs
    face = freetype.Face(spec['ttf'])
    face.set_pixel_sizes(0, spec['px_size'])
    stroker = None
    if spec['outline'] > 0.0:
        stroker = freetype.Stroker()
        stroker.set(int(round(spec['outline'] * 64.0)), freetype.FT_STROKER_LINECAP_ROUND, freetype.FT_STROKER_LINEJOIN_ROUND, 0)

    to_add = [cp for cp in ARABIC_CODEPOINTS if cp not in existing_cps]
    rendered = []
    cell_h = spec['cell_h']
    for cp in to_add:
        img, kl, kr, cw = render_glyph_rgba(face, stroker, cp, cell_h, spec['baseline_y'], spec['outline'])
        rendered.append((cp, img, kl, kr, cw))

    # Pack rendered glyphs into rows of width old_w (1px horizontal gap between cells)
    rows = []
    cur_x = 0
    cur_y = 0
    placements = []
    for cp, img, kl, kr, cw in rendered:
        cw_i = int(cw)
        if cur_x + cw_i > old_w:
            cur_x = 0
            cur_y += cell_h + 2
        placements.append((cp, img, kl, kr, cw, cur_x, cur_y))
        cur_x += cw_i + 1

    extra_h = cur_y + cell_h + 2
    new_h = old_h + extra_h
    strip = Image.new('RGBA', (old_w, extra_h), (0, 0, 0, 0))
    for cp, img, kl, kr, cw, px, py in placements:
        strip.paste(img, (px, py))

    if preview_path:
        bg = Image.new('RGBA', strip.size, (32, 40, 54, 255))
        bg.alpha_composite(strip)
        bg.save(preview_path)

    # 1. Update section 2 (data[1]) pixel buffers
    strip_bytes = strip.tobytes()
    extra_bytes_len = len(strip_bytes)
    assert extra_bytes_len == old_w * extra_h * 4
    sec2 = doc.data[1]
    img0_bytes = bytes(sec2[:old_sz0])
    rest_bytes = bytes(sec2[old_sz0:])
    doc.data[1] = bytearray(img0_bytes + strip_bytes + rest_bytes)

    # Update igImage2 #0 height and byte size
    new_sz0 = old_sz0 + extra_bytes_len
    struct.pack_into('<H', doc.data[img0_off >> 27], (img0_off & 0x7FFFFFF) + 0x1A, new_h)
    struct.pack_into('<I', doc.data[img0_off >> 27], (img0_off & 0x7FFFFFF) + 0x38, new_sz0)

    # Shift igImage2 #1 data pointer if present
    if img1_off is not None:
        old_p1 = doc.u64(img1_off + 0x40)
        new_p1 = old_p1 + extra_bytes_len
        struct.pack_into('<Q', doc.data[img1_off >> 27], (img1_off & 0x7FFFFFF) + 0x40, new_p1)

    # 2. Rescale v0 and v1 of existing igCharMetrics in list #0
    v_scale = old_h / float(new_h)
    for cm_off in existing_cm_ptrs:
        sec, so = cm_off >> 27, cm_off & 0x7FFFFFF
        v0 = struct.unpack_from('<f', doc.data[sec], so + 0x34)[0]
        v1 = struct.unpack_from('<f', doc.data[sec], so + 0x3C)[0]
        struct.pack_into('<f', doc.data[sec], so + 0x34, v0 * v_scale)
        struct.pack_into('<f', doc.data[sec], so + 0x3C, v1 * v_scale)

    # 3. Allocate new igCharMetrics objects
    new_cm_ptrs = []
    for cp, img, kl, kr, cw, px, py in placements:
        cm_off = doc.new_object('igCharMetrics', align=16)
        sec, so = cm_off >> 27, cm_off & 0x7FFFFFF
        u0 = px / float(old_w)
        v0 = (old_h + py) / float(new_h)
        u1 = (px + int(cw)) / float(old_w)
        v1 = (old_h + py + cell_h) / float(new_h)
        struct.pack_into(
            '<I11f', doc.data[sec], so + 0x10,
            cp, kl, kr, cw, 0.0, 0.0, cw, float(cell_h), u0, v0, u1, v1
        )
        new_cm_ptrs.append(cm_off)

    # 4. Build sorted combined igCharMetrics pointer array in data[0]
    combined = existing_cm_ptrs + new_cm_ptrs
    combined.sort(key=lambda off: doc.u32(off + 0x10))
    new_cnt = len(combined)

    # Unmark old pointer array ROFS entries
    for i in range(old_cnt):
        doc._mark('ROFS', old_arr_ptr + i * 8, False)

    new_arr_ptr = doc.alloc(new_cnt * 8, align=16)
    for i, ptr in enumerate(combined):
        doc.set_ptr(new_arr_ptr + i * 8, ptr)

    struct.pack_into('<II', doc.data[cm_list0_off >> 27], (cm_list0_off & 0x7FFFFFF) + 0x10, new_cnt, new_cnt)
    struct.pack_into('<I', doc.data[cm_list0_off >> 27], (cm_list0_off & 0x7FFFFFF) + 0x18, new_cnt * 8)
    doc.set_ptr(cm_list0_off + 0x20, new_arr_ptr)

    stats = {
        'font': logical_name,
        'old_dim': (old_w, old_h),
        'new_dim': (old_w, new_h),
        'old_glyphs': old_cnt,
        'added_glyphs': len(new_cm_ptrs),
        'total_glyphs': new_cnt,
    }
    return doc.to_bytes(), stats
