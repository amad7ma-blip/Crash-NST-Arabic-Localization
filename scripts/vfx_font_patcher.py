"""Patch Crash NST 3D VFX floating font (Vfx_Text_Character_Infos.igz + VFX_TEXT_LG* textures)."""
import math
import os
import struct
import subprocess
import tempfile
import freetype
from PIL import Image, ImageFilter, ImageOps

from nst_alchemy import IgzDoc

FONT_DIR = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic\workspace\tools\fonts'
TEXCONV = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic\workspace\tools\texconv.exe'
TTF_PATH = os.path.join(FONT_DIR, 'Changa-ExtraBold-Fixed.ttf')

# All Arabic Presentation Forms-B + punctuation needed for 3D VFX text
VFX_ARABIC_CPS = (
    [0x060C, 0x061B, 0x061F, 0x0640, 0x066A]
    + list(range(0xFE80, 0xFEFD))
    + [0x00AB, 0x00BB]
)


def render_vfx_cell(face: freetype.Face, stroker, cp: int):
    """Render a 64x64 glyph cell matching VFX_TEXT_LG style.

    Returns (img_outlined_rgba, img_white_rgba, height_gray_L, char_width_adj).
    """
    gid = face.get_char_index(cp)
    if gid == 0:
        raise ValueError(f'Missing glyph U+{cp:04X}')
    face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
    slot = face.glyph
    adv_x = slot.metrics.horiAdvance / 64.0
    fb = slot.bitmap
    fw, fh = fb.width, fb.rows
    fl, ft = slot.bitmap_left, slot.bitmap_top
    fbuf = bytes(fb.buffer)

    sw = sh = sl = st = 0
    sbuf = b''
    if fw > 0 and fh > 0:
        face.load_glyph(gid, freetype.FT_LOAD_NO_BITMAP)
        g = face.glyph.get_glyph()
        g.stroke(stroker, True)
        b = g.to_bitmap(freetype.FT_RENDER_MODE_NORMAL, freetype.Vector(0, 0), True)
        sb = b.bitmap
        sw, sh = sb.width, sb.rows
        sl, st = b.left, b.top
        sbuf = bytes(sb.buffer)

    # Center horizontally inside 64x64 cell; baseline y = 44
    cell = 64
    base_y = 44
    # Horizontal placement: center the advance box [0, adv_x] inside 64px cell
    ox = int(round((cell - adv_x) / 2.0))
    # Clamp if glyph + stroke sticks outside [1, 63]
    if sw > 0:
        if ox + sl < 1:
            ox = 1 - sl
        elif ox + sl + sw > cell - 1:
            ox = (cell - 1) - (sl + sw)

    adj_base = base_y
    if sh > 0:
        if adj_base - st < 1:
            adj_base = 1 + st
        elif adj_base + (sh - st) > cell - 1:
            adj_base = (cell - 1) - (sh - st)

    fill_l = Image.new('L', (cell, cell), 0)
    if fw > 0 and fh > 0:
        fill_l.paste(Image.frombytes('L', (fw, fh), fbuf), (ox + fl, adj_base - ft))

    stroke_l = Image.new('L', (cell, cell), 0)
    if sw > 0 and sh > 0:
        stroke_l.paste(Image.frombytes('L', (sw, sh), sbuf), (ox + sl, adj_base - st))

    # 1. Outlined RGBA (white fill over black outline)
    black = Image.new('RGBA', (cell, cell), (0, 0, 0, 0))
    black.putalpha(stroke_l)
    white = Image.new('RGBA', (cell, cell), (255, 255, 255, 0))
    white.putalpha(fill_l)
    outlined = Image.alpha_composite(black, white)

    # 2. White-only RGBA (fill_l or stroke_l? Earlier VFX_TEXT_LG_White had white fill with black transparent bg)
    white_only = white

    # 3. Heightmap for bevel normal: smooth blurred stroke+fill
    height_img = stroke_l.filter(ImageFilter.GaussianBlur(radius=1.5))

    # Width adjustment relative to default ~38px cell step in VFX_Text_Letter_Sub_Font
    width_adj = float(round(adv_x - 38.0))
    return outlined, white_only, height_img, width_adj


def height_to_normal_rg(height_img: Image.Image) -> Image.Image:
    """Convert 8-bit heightmap L image to tangent-space RG normal map (matching VFX_TEXT_LG_BW_NRM)."""
    w, h = height_img.size
    src = height_img.load()
    out = Image.new('RGB', (w, h), (127, 127, 0))
    dst = out.load()
    strength = 0.08
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            # Sobel gradient; note upright image vs DX normal orientation:
            # Earlier observed 'O': right edge R>128 (bright red), bottom edge G>128 (bright green)
            gx = (
                (src[x + 1, y - 1] + 2 * src[x + 1, y] + src[x + 1, y + 1])
                - (src[x - 1, y - 1] + 2 * src[x - 1, y] + src[x - 1, y + 1])
            ) * strength
            gy = (
                (src[x - 1, y + 1] + 2 * src[x, y + 1] + src[x + 1, y + 1])
                - (src[x - 1, y - 1] + 2 * src[x, y - 1] + src[x + 1, y - 1])
            ) * strength
            nz = 1.0
            inv = 1.0 / math.sqrt(gx * gx + gy * gy + nz * nz)
            nx = -gx * inv
            ny = gy * inv
            r = max(0, min(255, int(round((nx * 0.5 + 0.5) * 255.0))))
            g = max(0, min(255, int(round((ny * 0.5 + 0.5) * 255.0))))
            dst[x, y] = (r, g, 0)
    return out


def encode_with_texconv(im_upright: Image.Image, fmt: str, mips: int = 9) -> bytes:
    """Flip upright image for Alchemy UV convention, compress with texconv.exe, return raw mip bytes."""
    flipped = ImageOps.flip(im_upright)
    with tempfile.TemporaryDirectory() as tmp:
        src_tga = os.path.join(tmp, 'tex.png')
        flipped.save(src_tga)
        cmd = [
            TEXCONV, '-nologo', '-y',
            '-f', fmt, '-m', str(mips),
            '-o', tmp, src_tga,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f'texconv failed: {res.stdout}\n{res.stderr}')
        dds_path = os.path.join(tmp, 'tex.dds')
        with open(dds_path, 'rb') as f:
            dds = f.read()
        assert dds[:4] == b'DDS '
        # Check if DX10 header is present (pixelFormat dwFourCC at offset 84 == b'DX10')
        hdr_size = 148 if dds[84:88] == b'DX10' else 128
        return dds[hdr_size:]


def patch_vfx_font_and_textures(
    raw_char_infos: bytes,
    raw_tex_lg: bytes,
    raw_tex_white: bytes,
    raw_tex_nrm: bytes,
    preview_dir: str | None = None,
) -> dict[str, bytes]:
    doc = IgzDoc(raw_char_infos)
    ht = next(o for o, t in doc.objects.items() if t == 'CCharacterInfoHashTable')
    val_sz, val_ptr = doc.u32(ht + 0x10), doc.u64(ht + 0x18)
    key_sz, key_ptr = doc.u32(ht + 0x20), doc.u64(ht + 0x28)
    nbuckets = key_sz // 2
    assert nbuckets == 760

    keys = list(struct.unpack_from(f'<{nbuckets}H', doc.data[key_ptr >> 27], key_ptr & 0x7FFFFFF))
    vals = list(struct.unpack_from(f'<{nbuckets}Q', doc.data[val_ptr >> 27], val_ptr & 0x7FFFFFF))

    # Separate keep entries vs Japanese entries (>= 0x3000) we can replace
    keep_items = []
    jp_items = []
    for k, v in zip(keys, vals):
        if v == 0:
            continue
        if k >= 0x3000:
            jp_items.append((k, v))
        else:
            keep_items.append((k, v))
    jp_items.sort(key=lambda kv: doc.u32(kv[1] + 0x10))

    existing_cps = {k for k, _ in keep_items}
    add_cps = [cp for cp in VFX_ARABIC_CPS if cp not in existing_cps]
    assert len(add_cps) <= len(jp_items), f'Need {len(add_cps)} slots, only {len(jp_items)} Japanese slots available'

    # Decode original 2048x1024 VFX_TEXT_LG, VFX_TEXT_LG_White, VFX_TEXT_LG_BW_NRM (mip 0 = 2048*1024 bytes)
    def decode_tex(raw_igz, bcn_mode):
        d = IgzDoc(raw_igz)
        off = next(o for o, t in d.objects.items() if t == 'igImage2')
        ptr = d.u64(off + 0x40)
        buf = bytes(d.data[ptr >> 27][(ptr & 0x7FFFFFF):(ptr & 0x7FFFFFF) + 2048 * 1024])
        mode = 'RGBA' if bcn_mode == 3 else 'RGB'
        return d, ImageOps.flip(Image.frombytes(mode, (2048, 1024), buf, 'bcn', bcn_mode))

    doc_lg, im_lg = decode_tex(raw_tex_lg, 3)
    doc_wh, im_wh = decode_tex(raw_tex_white, 3)
    doc_nm, im_nm = decode_tex(raw_tex_nrm, 5)

    # Render Arabic glyphs & overwrite the reassigned Japanese cell slots
    face = freetype.Face(TTF_PATH)
    face.set_pixel_sizes(0, 38)
    stroker = freetype.Stroker()
    stroker.set(int(round(2.8 * 64.0)), freetype.FT_STROKER_LINECAP_ROUND, freetype.FT_STROKER_LINEJOIN_ROUND, 0)

    reassigned = []
    for cp, (_old_k, cinfo_off) in zip(add_cps, jp_items):
        sprite_idx = doc.u32(cinfo_off + 0x10)
        # Note: in upright 32x16 grid, idx=0 is top-left! (col = idx % 32, row = idx // 32)
        col = sprite_idx % 32
        row = sprite_idx // 32
        x0, y0 = col * 64, row * 64

        cell_lg, cell_wh, h_img, w_adj = render_vfx_cell(face, stroker, cp)
        cell_nm = height_to_normal_rg(h_img)

        im_lg.paste(cell_lg, (x0, y0))
        im_wh.paste(cell_wh, (x0, y0))
        im_nm.paste(cell_nm, (x0, y0))

        # Update CCharacterInfo width adjustment (+0x14 = f32) and zero other fields
        sec, so = cinfo_off >> 27, cinfo_off & 0x7FFFFFF
        struct.pack_into('<I7f', doc.data[sec], so + 0x10, sprite_idx, w_adj, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        reassigned.append((cp, cinfo_off))

    # Keep remaining unused Japanese items as-is so count stays 380, or rebuild table with keep + reassigned + leftover jp
    final_items = keep_items + reassigned + jp_items[len(add_cps):]
    assert len(final_items) == doc.u32(ht + 0x30)

    # Rebuild linear-probing hash table (nbuckets=760)
    new_keys = [0] * nbuckets
    new_vals = [0] * nbuckets
    for k, v in final_items:
        b = k % nbuckets
        while new_vals[b] != 0:
            b = (b + 1) % nbuckets
        new_keys[b] = k
        new_vals[b] = v

    # Clear old ROFS marks on val_ptr array, write new keys and vals with ROFS marks
    for i in range(nbuckets):
        doc._mark('ROFS', val_ptr + i * 8, False)
    struct.pack_into(f'<{nbuckets}H', doc.data[key_ptr >> 27], key_ptr & 0x7FFFFFF, *new_keys)
    for i, v in enumerate(new_vals):
        doc.set_ptr(val_ptr + i * 8, v if v != 0 else None)

    if preview_dir:
        bg = Image.new('RGBA', (2048, 1024), (32, 40, 54, 255))
        bg.alpha_composite(im_lg)
        bg.save(os.path.join(preview_dir, 'VFX_TEXT_LG_with_arabic.png'))

    # Compress updated textures via texconv and inject into igImage2 section 2
    def update_tex_igz(d_tex: IgzDoc, im_u: Image.Image, fmt: str) -> bytes:
        mips_bytes = encode_with_texconv(im_u, fmt, mips=9)
        off = next(o for o, t in d_tex.objects.items() if t == 'igImage2')
        exp_sz = d_tex.u32(off + 0x38)
        assert len(mips_bytes) == exp_sz, f'{fmt}: got {len(mips_bytes)} != expected {exp_sz}'
        ptr = d_tex.u64(off + 0x40)
        psec, poff = ptr >> 27, ptr & 0x7FFFFFF
        d_tex.data[psec][poff:poff + exp_sz] = mips_bytes
        return d_tex.to_bytes()

    return {
        'vfxFonts/Vfx_Text_Character_Infos.igz': doc.to_bytes(),
        'textures/ColorMap,textures@!ui!Crash!VFX_TEXT_LG`png,111.igz': update_tex_igz(doc_lg, im_lg, 'BC3_UNORM'),
        'textures/ColorMap,textures@!ui!Crash!VFX_TEXT_LG_White`png,111.igz': update_tex_igz(doc_wh, im_wh, 'BC3_UNORM'),
        'textures/NormalMap,textures@!ui!Crash!VFX_TEXT_LG_BW_NRM`png,111.igz': update_tex_igz(doc_nm, im_nm.convert('RGBA'), 'BC5_UNORM'),
    }
