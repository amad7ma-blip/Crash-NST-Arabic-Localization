"""Safe Arabic shaping, placeholder guarding, and .lng patching for Crash NST."""
import re
import struct
import arabic_reshaper
from bidi.algorithm import get_display

from nst_alchemy import IgzDoc

# Configure arabic_reshaper: standard Presentation Forms-B, strip combining harakat so bitmap cursor won't advance on marks
_RESHAPER = arabic_reshaper.ArabicReshaper(configuration={
    'delete_harakat': True,
    'delete_tatweel': False,
    'support_ligatures': True,
    'use_unshaped_instead_of_isolated': False,
})

# Tokens that must stay intact (never reversed by BiDi or reshaped):
# - printf placeholders: %%, %s, %d, %.2f, %c, etc.
# - brace placeholders: {0}, {1}, ...
# - PUA controller/button icons: \uE000-\uF8FF
_TOKEN_RE = re.compile(
    r'(%[0-9.]*[lh]*[sdifcxu]+\s+%%|(?:%[0-9.]*[lh]*[sdifcxu]){2,}|\{[0-9]+\}|%[0-9.]*[lh]*[sdifcxu%]|[\uE000-\uF8FF])'
)

# Hebrew block guards (strong RTL characters, never emitted by Arabic text)
_GUARD_START = 0x05D0


def shape_line_rtl(line: str) -> str:
    """Shape one logical Arabic line into visual LTR order for LTR bitmap font rendering."""
    if not line:
        return line
    # Only apply RTL reshaping/bidi if line contains Arabic characters
    if not any('\u0600' <= ch <= '\u06FF' or '\uFB50' <= ch <= '\uFEFF' for ch in line):
        return line

    tokens = []

    def _repl(m):
        idx = len(tokens)
        if idx >= 27:
            # Fallback if >27 placeholders on a single line
            return m.group(0)
        tokens.append(m.group(0))
        return chr(_GUARD_START + idx)

    guarded = _TOKEN_RE.sub(_repl, line)
    reshaped = _RESHAPER.reshape(guarded)
    visual = get_display(reshaped, base_dir='R')
    for idx, tok in enumerate(tokens):
        visual = visual.replace(chr(_GUARD_START + idx), tok)
    return visual


def shape_arabic_text(logical_ar: str, wrap_width: int = 0) -> str:
    """Shape a potentially pipe-delimited and/or multi-line Arabic string."""
    # Preserve exact pipe segments (e.g. dropdown tooltips in guisystemdata)
    if '|' in logical_ar:
        parts = logical_ar.split('|')
        return '|'.join(shape_arabic_text(p, wrap_width=wrap_width) for p in parts)

    # Preserve exact line break style (\r\n vs \n)
    sep = '\r\n' if '\r\n' in logical_ar else '\n'
    lines = logical_ar.split(sep)
    out_lines = []
    for ln in lines:
        if wrap_width > 0 and len(ln) > wrap_width:
            # Wrap logically at word boundaries BEFORE BiDi!
            words = ln.split(' ')
            cur = ''
            wrapped = []
            for w in words:
                cand = (cur + ' ' + w) if cur else w
                if len(cand) > wrap_width and cur:
                    wrapped.append(cur)
                    cur = w
                else:
                    cur = cand
            if cur:
                wrapped.append(cur)
            for wl in wrapped:
                out_lines.append(shape_line_rtl(wl))
        else:
            out_lines.append(shape_line_rtl(ln))
    return sep.join(out_lines)


def patch_lng_bytes(raw_lng: bytes, replacements: dict[str, str]) -> tuple[bytes, int]:
    """Replace localized string slots in a .lng (IGZ) file while preserving ONAM/EXNM."""
    doc = IgzDoc(raw_lng)
    # Identify ONAM name strings so we NEVER accidentally replace object names
    onam_rstt = set()
    if doc.names_offset is not None:
        cnt = doc.u32(doc.names_offset + 0x0C)
        arr = doc.u64(doc.names_offset + 0x20)
        for i in range(cnt):
            onam_rstt.add(arr + i * 16)

    changed = 0
    for r_off in sorted(doc.offset_sets.get('RSTT', ())):
        if r_off in onam_rstt:
            continue
        str_idx = doc.u64(r_off)
        orig = doc.string(str_idx)
        if orig in replacements:
            doc.set_string_ref(r_off, replacements[orig])
            changed += 1
    return doc.to_bytes(), changed
