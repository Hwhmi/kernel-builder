#!/usr/bin/env python3
"""把单个 dtb 打包成 Android DTBO image（mkdtboimg.py 的最小实现，无外部依赖）。

用法: python3 pack_dtbo.py <input.dtb> <output.dtbo.img>
"""
import struct
import sys


def main():
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <input.dtb> <output.dtbo.img>")
        sys.exit(1)

    dtb_path, out_path = sys.argv[1], sys.argv[2]
    with open(dtb_path, "rb") as f:
        dtb = f.read()

    # 校验 FDT magic (0xD00DFEED)
    magic = struct.unpack(">I", dtb[:4])[0]
    if magic != 0xD00DFEED:
        print(f"错误: {dtb_path} 不是有效的 dtb (magic={magic:#x})")
        sys.exit(1)

    page_size = 4096
    header_size = 32
    entry_size = 32
    entries_off = header_size
    pad = (page_size - (header_size + entry_size) % page_size) % page_size
    dt_offset = header_size + entry_size + pad
    total = dt_offset + len(dtb)
    total_padded = ((total + page_size - 1) // page_size) * page_size

    hdr = struct.pack(
        ">8I",
        0xD7B7AB1E,      # DTBO magic
        total_padded,    # total size
        header_size,
        entry_size,
        1,               # dt entry count
        entries_off,
        page_size,
        0,               # version
    )
    ent = struct.pack(
        ">8I",
        len(dtb),        # dt_size
        dt_offset,       # dt_offset
        0,               # id
        0,               # rev
        0, 0, 0, 0,      # custom
    )

    with open(out_path, "wb") as f:
        f.write(hdr)
        f.write(ent)
        f.write(b"\x00" * pad)
        f.write(dtb)
        f.write(b"\x00" * (total_padded - total))

    print(f"OK: {out_path} = {total_padded} bytes (dtb {len(dtb)} bytes)")


if __name__ == "__main__":
    main()
