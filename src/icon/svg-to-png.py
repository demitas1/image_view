import sys
import cairosvg


"""
Setup:
    pip install cairosvg
"""


def convert_svg_to_png(svg_path, output_prefix):
    sizes = [16, 32, 48, 64, 128, 256]

    for size in sizes:
        output_path = f"{output_prefix}_{size}.png"
        cairosvg.svg2png(
            url=svg_path,
            write_to=output_path,
            output_width=size,
            output_height=size
        )
        print(f"Generated: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python svg_to_png.py input.svg output_prefix")
        sys.exit(1)

    svg_path = sys.argv[1]
    output_prefix = sys.argv[2]
    convert_svg_to_png(svg_path, output_prefix)
