#!/usr/bin/env python3
"""news-image-20261123 entrypoint: copy entry.png to the output directory.

Standard library only, no network. Validates the PNG before copying:
signature, IHDR size 1024x1024, the 1 MiB cap, every chunk's CRC, and a
complete IEND. Then verifies the copy hashes exactly like the source.
Both runs write the same bytes.
"""
import hashlib
import os
import struct
import sys
import zlib

MAX_BYTES = 1_048_576
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def validate_png(data):
    """Check the PNG is whole and matches the competition limits."""
    if len(data) > MAX_BYTES:
        fail(f"entry.png is {len(data)} bytes, over the {MAX_BYTES} cap")
    if len(data) < 8 or data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("entry.png is not a PNG (bad signature)")
    pos = 8
    seen_ihdr = False
    seen_iend = False
    while pos < len(data):
        if pos + 8 > len(data):
            fail("truncated chunk header")
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        chunk_end = pos + 12 + length
        if chunk_end > len(data):
            fail(f"truncated {ctype.decode('latin1')} chunk")
        stored_crc = struct.unpack(">I", data[chunk_end - 4:chunk_end])[0]
        actual_crc = zlib.crc32(data[pos + 4:chunk_end - 4]) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            fail(f"bad CRC in {ctype.decode('latin1')} chunk")
        if ctype == b"IHDR":
            if length != 13:
                fail(f"IHDR is {length} bytes, expected 13")
            width, height = struct.unpack(">II", data[pos + 8:pos + 16])
            if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
                fail(f"IHDR is {width}x{height}, expected "
                     f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}")
            seen_ihdr = True
        if ctype == b"IEND":
            seen_iend = True
            if chunk_end != len(data):
                fail("trailing bytes after IEND")
            break
        pos = chunk_end
    if not seen_ihdr:
        fail("no IHDR chunk")
    if not seen_iend:
        fail("no IEND chunk")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(out_dir, "entry.png")
    with open(source, "rb") as fh:
        data = fh.read()
    validate_png(data)
    os.makedirs(out_dir, exist_ok=True)
    with open(target, "wb") as fh:
        fh.write(data)
    with open(target, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(data).hexdigest():
        fail("output hash does not match source")
    print(f"wrote {target} ({len(data)} bytes, "
          f"sha256 {hashlib.sha256(data).hexdigest()})")


if __name__ == "__main__":
    main()
