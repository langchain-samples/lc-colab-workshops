#!/usr/bin/env python3
"""Print the `<img width=...>` to use for each screenshot.

Retina captures are 2x, so embedding them at natural size renders them at double
size — blown up and soft. Half the pixel width is the true logical size.

    python3 tools/screenshot_widths.py
"""

import pathlib
import struct
import sys

REPO = "langchain-samples/lc-colab-workshops"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/assets/screenshots"


def png_size(path: pathlib.Path) -> tuple[int, int]:
    """Read width/height straight from the IHDR chunk."""
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", header[16:24])


def main() -> int:
    folder = pathlib.Path("assets/screenshots")
    pngs = sorted(folder.glob("*.png"))
    if not pngs:
        print(f"No PNGs in {folder}/")
        return 0

    for path in pngs:
        width, height = png_size(path)
        print(f"{path.name:34} {width:>5}x{height:<5}  width=\"{width // 2}\"")

    print("\nEmbed with:")
    example = pngs[0]
    print(f'<img src="{RAW}/{example.name}"\n'
          f'     alt="..." width="{png_size(example)[0] // 2}">')
    return 0


if __name__ == "__main__":
    sys.exit(main())
