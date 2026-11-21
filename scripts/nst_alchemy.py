"""Crash Bandicoot N. Sane Trilogy - Alchemy IGA v11 & IGZ v10 (UTF-8) library."""
import bisect
import collections
import lzma
import os
import struct

IGA_MAGIC = b'IGA\x1a'
IGZ_MAGIC = 0x49475A01
BLOCK_SIZE = 0x8000
TYPE_LZMA = 2
TYPE_NONE = 0xF
FULL_PREFIX = 'temporary/mack/data/win64/output/'

COMPRESSED_FIXUPS = ('RVTB', 'RSTT', 'ROFS', 'RPID', 'RHND', 'RNEX', 'REXT', 'RSTR')
FIXUP_ORDER = (
    'TDEP', 'TSTR', 'TMET', 'MTSZ', 'EXID', 'EXNM',
    'RVTB', 'RSTT', 'ROFS', 'RPID', 'RHND', 'RNEX',
    'REXT', 'RSTR', 'ROOT', 'ONAM',
)
PAIR_FIXUPS = ('EXID', 'EXNM')


def fnv1a_lower(s: str) -> int:
    h = 0x811C9DC5
    for c in s.lower().encode('utf-8'):
        h = ((h ^ c) * 0x01000193) & 0xFFFFFFFF
    return h


class IgaEntry:
    __slots__ = ('index', 'name', 'logical_name', 'offset', 'ordinal', 'size', 'ctype', 'block_index', 'name_hash')

    def __init__(self, index, name, logical_name, offset, ordinal, size, ctype, block_index, name_hash):
        self.index = index
        self.name = name
        self.logical_name = logical_name
        self.offset = offset
        self.ordinal = ordinal
        self.size = size
        self.ctype = ctype
        self.block_index = block_index
        self.name_hash = name_hash


class IgaArchiveV11:
    def __init__(self, path):
        self.path = path
        self.f = open(path, 'rb')
        hdr = self.f.read(0x38)
        (
            magic, self.version, toc_size, n, self.sector, self.hash_div, self.hash_slop,
            nl, nm, ns, name_off, name_size, self.flags
        ) = struct.unpack('<4sIIIIIIIIIQII', hdr)
        if magic != IGA_MAGIC:
            raise ValueError(f'{path}: not an IGA archive')
        if self.version != 11:
            raise ValueError(f'{path}: expected IGA v11, got v{self.version}')
        self.f.seek(0)
        toc = self.f.read(0x38 + toc_size)
        hashes = struct.unpack_from(f'<{n}I', toc, 0x38)
        eo = 0x38 + n * 4
        bo = eo + n * 16
        self.large = struct.unpack_from(f'<{nl}I', toc, bo)
        bo += nl * 4
        self.medium = struct.unpack_from(f'<{nm}H', toc, bo)
        bo += nm * 2
        self.small = toc[bo:bo + ns]

        self.f.seek(name_off)
        names = self.f.read(name_size)
        name_offs = struct.unpack_from(f'<{n}I', names, 0)

        def cstr(o):
            return names[o:names.index(b'\0', o)].decode('utf-8', 'replace')

        self.entries = []
        self.by_logical = {}
        for i in range(n):
            a, b, size, blk = struct.unpack_from('<IIII', toc, eo + i * 16)
            full = cstr(name_offs[i])
            logical = cstr(name_offs[i] + len(full.encode('utf-8')) + 1)
            ent = IgaEntry(
                i, full, logical or full,
                a | ((b & 0xFF) << 32), b >> 8,
                size, blk >> 28, blk & 0x0FFFFFFF, hashes[i]
            )
            self.entries.append(ent)
            self.by_logical[ent.logical_name.lower()] = ent

    def close(self):
        if self.f and not self.f.closed:
            self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def block_table(self, e):
        sectors = (e.size + self.sector - 1) // self.sector
        if sectors <= 0x7F:
            return self.small, 0x7F, 0x80
        if sectors <= 0x7FFF:
            return self.medium, 0x7FFF, 0x8000
        return self.large, 0x7FFFFFFF, 0x80000000

    def read_entry(self, e: IgaEntry) -> bytes:
        if e.ctype == TYPE_NONE:
            self.f.seek(e.offset)
            return self.f.read(e.size)
        if e.ctype != TYPE_LZMA:
            raise NotImplementedError(f'{e.logical_name}: unsupported compression type {e.ctype}')
        table, mask, cflag = self.block_table(e)
        nblocks = (e.size + BLOCK_SIZE - 1) // BLOCK_SIZE
        out = bytearray()
        for k in range(nblocks):
            ent = table[e.block_index + k]
            nxt = table[e.block_index + k + 1] & mask
            start = e.offset + (ent & mask) * self.sector
            want = min(BLOCK_SIZE, e.size - k * BLOCK_SIZE)
            self.f.seek(start)
            if ent & cflag:
                raw = self.f.read((nxt - (ent & mask)) * self.sector)
                csize = struct.unpack_from('<H', raw)[0]
                flt = lzma._decode_filter_properties(lzma.FILTER_LZMA1, raw[2:7])
                dec = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[flt])
                blk = dec.decompress(raw[7:7 + csize], max_length=want)
            else:
                blk = self.f.read(want)
            if len(blk) != want:
                raise IOError(f'{e.logical_name}: block {k} got {len(blk)}, expected {want}')
            out += blk
        return bytes(out)

    def read(self, logical_name: str) -> bytes:
        e = self.by_logical.get(logical_name.lower())
        if e is None:
            raise KeyError(f'{logical_name} not found in {self.path}')
        return self.read_entry(e)


def _compress_iga_entry(blob: bytes, sector: int) -> tuple[int, bytes, list[int] | None, str]:
    """Try LZMA1 block compression for an IGA v11 entry; return (ctype, payload, block_entries, table_kind)."""
    if len(blob) <= sector:
        return TYPE_NONE, blob, None, ''

    uncomp_sectors = (len(blob) + sector - 1) // sector
    if uncomp_sectors <= 0x7F:
        kind, cflag = 'small', 0x80
    elif uncomp_sectors <= 0x7FFF:
        kind, cflag = 'medium', 0x8000
    else:
        kind, cflag = 'large', 0x80000000

    flt = [{'id': lzma.FILTER_LZMA1, 'dict_size': 0x800000, 'lc': 3, 'lp': 0, 'pb': 2}]
    props = b'\x5d\x00\x80\x00\x00'
    chunks = []
    any_comp = False
    for off in range(0, len(blob), BLOCK_SIZE):
        raw_chunk = blob[off:off + BLOCK_SIZE]
        r_secs = (len(raw_chunk) + sector - 1) // sector
        comp = lzma.compress(raw_chunk, format=lzma.FORMAT_RAW, filters=flt)
        if len(comp) <= 0xFFFF:
            cblk = struct.pack('<H', len(comp)) + props + comp
            c_secs = (len(cblk) + sector - 1) // sector
            if c_secs < r_secs:
                chunks.append((True, cblk, c_secs))
                any_comp = True
                continue
        chunks.append((False, raw_chunk, r_secs))

    if not any_comp:
        return TYPE_NONE, blob, None, ''

    payload = bytearray()
    tbl_entries = []
    cur_sec = 0
    for is_comp, data, secs in chunks:
        tbl_entries.append(cur_sec | (cflag if is_comp else 0))
        payload.extend(data)
        pad = secs * sector - len(data)
        if pad:
            payload.extend(b'\0' * pad)
        cur_sec += secs
    tbl_entries.append(cur_sec)
    return TYPE_LZMA, bytes(payload), tbl_entries, kind


def build_iga_v11(files: dict[str, bytes], dst_path: str, sector: int = 0x800, flags: int = 1, compress: bool = False):
    """Build a standalone clean IGA v11 archive from {logical_name: bytes}."""
    n = len(files)
    if n == 0:
        raise ValueError('Cannot build empty IGA archive')

    large_tbl: list[int] = []
    medium_tbl: list[int] = []
    small_tbl: list[int] = []
    rows = []
    for ord_idx, (logical, blob) in enumerate(sorted(files.items(), key=lambda kv: kv[0].lower())):
        h = fnv1a_lower(logical)
        full = FULL_PREFIX + logical
        if compress:
            ctype, payload, blk_entries, kind = _compress_iga_entry(blob, sector)
            if blk_entries is not None:
                if kind == 'small':
                    blk_idx = len(small_tbl)
                    small_tbl.extend(blk_entries)
                elif kind == 'medium':
                    blk_idx = len(medium_tbl)
                    medium_tbl.extend(blk_entries)
                else:
                    blk_idx = len(large_tbl)
                    large_tbl.extend(blk_entries)
            else:
                blk_idx = 0x0FFFFFFF
        else:
            ctype, payload, blk_idx = TYPE_NONE, blob, 0x0FFFFFFF
        rows.append((h, ord_idx, full, logical, len(blob), ctype, blk_idx, payload))
    rows.sort(key=lambda r: r[0])

    nl, nm, ns = len(large_tbl), len(medium_tbl), len(small_tbl)
    toc_size = n * 20 + nl * 4 + nm * 2 + ns
    data_start = 0x38 + toc_size
    data_start += (-data_start) % sector

    buf = bytearray(data_start)
    entry_bytes = bytearray()
    hash_bytes = bytearray()
    strings = bytearray()
    name_offs = []

    pos = data_start
    for h, ord_idx, full, logical, uncomp_size, ctype, blk_idx, payload in rows:
        pos_pad = pos + ((-pos) % sector)
        if pos_pad > len(buf):
            buf.extend(b'\0' * (pos_pad - len(buf)))
        buf.extend(payload)
        rem = (-len(buf)) % sector
        if rem:
            buf.extend(b'\0' * rem)
        pos = len(buf)

        off_start = pos_pad
        entry_bytes += struct.pack(
            '<IIII',
            off_start & 0xFFFFFFFF,
            ((off_start >> 32) & 0xFF) | (ord_idx << 8),
            uncomp_size,
            (ctype << 28) | (blk_idx & 0x0FFFFFFF),
        )
        hash_bytes += struct.pack('<I', h)
        name_offs.append(n * 4 + len(strings))
        strings += full.encode('utf-8') + b'\0' + logical.encode('utf-8') + b'\0'

    block_bytes = bytearray()
    if nl:
        block_bytes += struct.pack(f'<{nl}I', *large_tbl)
    if nm:
        block_bytes += struct.pack(f'<{nm}H', *medium_tbl)
    if ns:
        block_bytes += bytes(small_tbl)

    names_blob = struct.pack(f'<{n}I', *name_offs) + bytes(strings)
    rem16 = (-len(buf)) % 16
    if rem16:
        buf.extend(b'\0' * rem16)
    name_off = len(buf)
    buf.extend(names_blob)

    div = min(0xFFFFFFFF, max(1, (1 << 32) // n))
    slop = max(abs(i - r[0] // div) for i, r in enumerate(rows)) + 1

    hdr = struct.pack(
        '<4sIIIIIIIIIQII',
        IGA_MAGIC, 11, toc_size, n, sector, div, slop,
        nl, nm, ns, name_off, len(names_blob), flags
    )
    buf[0:0x38] = hdr
    ho = 0x38
    buf[ho:ho + len(hash_bytes)] = hash_bytes
    eo = ho + len(hash_bytes)
    buf[eo:eo + len(entry_bytes)] = entry_bytes
    bo = eo + len(entry_bytes)
    buf[bo:bo + len(block_bytes)] = block_bytes

    os.makedirs(os.path.dirname(os.path.abspath(dst_path)), exist_ok=True)
    with open(dst_path, 'wb') as f:
        f.write(buf)


def unpack_offsets(count: int, data: bytes) -> list[int]:
    out, prev, pos, hi = [], 0, 0, False

    def nib():
        nonlocal pos, hi
        if not hi:
            hi = True
            return data[pos] & 0xF
        hi = False
        pos += 1
        return data[pos - 1] >> 4

    for _ in range(count):
        c = nib()
        val, sh = c & 7, 3
        while c & 8:
            c = nib()
            val |= (c & 7) << sh
            sh += 3
        prev += val * 4
        out.append(prev)
    return out


def pack_offsets(offsets: list[int]) -> bytes:
    nibbles, prev = [], 0
    for o in sorted(offsets):
        val = (o - prev) // 4
        prev = o
        while True:
            n = val & 7
            val >>= 3
            nibbles.append(n | (8 if val else 0))
            if not val:
                break
    if len(nibbles) & 1:
        nibbles.append(0)
    return bytes(nibbles[i] | (nibbles[i + 1] << 4) for i in range(0, len(nibbles), 2))


def encode_strings_utf8(strings: list[str]) -> bytes:
    out = bytearray()
    for s in strings:
        out += s.encode('utf-8') + b'\0'
        if len(out) & 1:
            out += b'\0'
    return bytes(out)


class IgzDoc:
    """Crash NST IGZ v10 parser/editor with UTF-8 TSTR support."""

    def __init__(self, raw: bytes):
        self.raw = raw
        magic, self.version, self.type_hash = struct.unpack_from('<III', raw, 0)
        if magic != IGZ_MAGIC:
            raise ValueError('Not an IGZ file')
        self.sections = []
        self.section_meta = []
        for i in range(32):
            off, size, align, unk = struct.unpack_from('<IIII', raw, 0x18 + i * 16)
            if off == 0 and size == 0:
                break
            self.sections.append((off, size))
            self.section_meta.append((align, unk))
        self.fixups = {}
        self.fixup_layout = []
        fo, fs = self.sections[0]
        p = fo
        while p < fo + fs:
            m, cnt, size, start = struct.unpack_from('<4sIII', raw, p)
            key = m.decode('latin1')
            self.fixups[key] = (cnt, raw[p + start:p + size])
            self.fixup_layout.append((key, raw[p + 16:p + start]))
            if size == 0:
                break
            p += size
        self.data = [bytearray(raw[o:o + s]) for o, s in self.sections[1:]]
        self.strings = self._parse_strings('TSTR')
        self.types = self._parse_strings('TMET')
        cnt, body = self.fixups.get('MTSZ', (0, b''))
        self.type_sizes = list(struct.unpack_from(f'<{cnt}I', body))
        cnt, body = self.fixups.get('EXNM', (0, b''))
        self._exnm_raw = list(struct.iter_unpack('<II', body[:cnt * 8]))
        self.ext_names = [(self.string(a), self.string(c & 0x7FFFFFFF)) for a, c in self._exnm_raw]
        self.offset_sets = {}
        for k in COMPRESSED_FIXUPS:
            if k in self.fixups:
                self.offset_sets[k] = set(unpack_offsets(*self.fixups[k]))
        self.objects = {}
        for off in sorted(self.offset_sets.get('RVTB', ())):
            t = struct.unpack_from('<Q', *self._loc(off))[0]
            self.objects[off] = self.types[t]
        root_cnt, root = self.fixups.get('ROOT', (0, b''))
        self.root_offset = struct.unpack_from('<I', root)[0] if root_cnt else None
        onam_cnt, onam = self.fixups.get('ONAM', (0, b''))
        self.names_offset = struct.unpack_from('<I', onam)[0] if onam_cnt else None

    def _parse_strings(self, key: str) -> list[str]:
        cnt, body = self.fixups.get(key, (0, b''))
        out, o = [], 0
        for _ in range(cnt):
            e = body.index(b'\0', o)
            out.append(body[o:e].decode('utf-8'))
            o = e + 1
            if o & 1:
                o += 1
        return out

    def string(self, i: int):
        return self.strings[i] if 0 <= i < len(self.strings) else None

    def _loc(self, off: int):
        return self.data[off >> 27], off & 0x7FFFFFF

    def u32(self, off: int) -> int:
        return struct.unpack_from('<I', *self._loc(off))[0]

    def u64(self, off: int) -> int:
        return struct.unpack_from('<Q', *self._loc(off))[0]

    def f32(self, off: int) -> float:
        return struct.unpack_from('<f', *self._loc(off))[0]

    def alloc(self, size: int, align: int = 16, sec: int = 0) -> int:
        buf = self.data[sec]
        buf.extend(b'\0' * (-len(buf) % align))
        off = len(buf)
        buf.extend(b'\0' * size)
        return (sec << 27) | off

    def add_string(self, s: str) -> int:
        idx = self.__dict__.get('_string_index')
        if idx is None or self.__dict__.get('_string_count') != len(self.strings):
            idx = self._string_index = {}
            for i, v in enumerate(self.strings):
                idx.setdefault(v, i)
            self._string_count = len(self.strings)
        i = idx.get(s)
        if i is None:
            i = idx[s] = len(self.strings)
            self.strings.append(s)
            self._string_count += 1
        return i

    def _mark(self, kind: str, off: int, on: bool = True):
        s = self.offset_sets.setdefault(kind, set())
        if on:
            s.add(off)
        else:
            s.discard(off)

    def set_ptr(self, off: int, target: int | None):
        struct.pack_into('<Q', *self._loc(off), target or 0)
        self._mark('ROFS', off, target is not None)

    def set_string_ref(self, off: int, s: str | None):
        struct.pack_into('<Q', *self._loc(off), self.add_string(s) if s is not None else 0)
        self._mark('RSTT', off, s is not None)

    def new_object(self, type_name: str, align: int = 16) -> int:
        t_idx = self.types.index(type_name)
        size = self.type_sizes[t_idx]
        off = self.alloc(size, align)
        struct.pack_into('<QI', *self._loc(off), t_idx, 1)
        self._mark('RVTB', off, True)
        self.objects[off] = type_name
        return off

    def to_bytes(self) -> bytes:
        fix = bytearray()
        for magic, gap in self.fixup_layout:
            cnt, body = self.fixups[magic]
            if magic == 'TSTR':
                cnt, body = len(self.strings), encode_strings_utf8(self.strings)
            elif magic == 'TMET':
                cnt, body = len(self.types), encode_strings_utf8(self.types)
            elif magic == 'MTSZ':
                cnt, body = len(self.type_sizes), struct.pack(f'<{len(self.type_sizes)}I', *self.type_sizes)
            elif magic == 'EXNM':
                cnt = len(self.ext_names)
                raw_ex = self._exnm_raw + [
                    (self.strings.index(n), self.strings.index(ns) | 0x80000000)
                    for n, ns in self.ext_names[len(self._exnm_raw):]
                ]
                body = b''.join(struct.pack('<II', a, c) for a, c in raw_ex)
            elif magic in COMPRESSED_FIXUPS:
                offs = sorted(self.offset_sets[magic])
                cnt, body = len(offs), pack_offsets(offs)
            if gap is None:
                gap = b'\0' * (-(len(fix) + 16) % 8 if magic in PAIR_FIXUPS else 0)
            start = 16 + len(gap)
            size = start + len(body)
            size += -size & 3
            fix += struct.pack('<4sIII', magic.encode('latin1'), cnt, size, start) + gap + body
            fix += b'\0' * (size - start - len(body))

        blobs = [bytes(fix)] + [bytes(d) for d in self.data]
        out = bytearray(self.raw[:self.sections[0][0]])
        struct.pack_into('<I', out, 0x10, len(self.fixup_layout))
        pos = self.sections[0][0]
        layout = []
        for i, blob in enumerate(blobs):
            align = self.section_meta[i][0]
            layout.append((pos, len(blob)))
            struct.pack_into('<IIII', out, 0x18 + i * 16, pos, len(blob), align, self.section_meta[i][1])
            pos += len(blob)
        for (p, _), blob in zip(layout, blobs):
            out += b'\0' * (p - len(out)) + blob
        return bytes(out)
