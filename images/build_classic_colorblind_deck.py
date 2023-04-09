"""
Script to build the classic colorblind deck from the classic deck.

Requires imagemagick to be installed and in the path.
"""


from pathlib import Path
from shutil import copyfile
from subprocess import run

IMAGES_DIR = Path(__file__).resolve().parent
CLASSIC_DIR = IMAGES_DIR / "classic"
COLORBLIND_DIR = IMAGES_DIR / "classic_colorblind"
COLORBLIND_OVERLAY_DIR = IMAGES_DIR / "colorblind_overlay"

COLORS = ["r", "g", "b", "y"]
NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "draw", "reverse", "skip"]
SPECIALS = ["colorchooser", "draw_four"]


def overlay_image(color, number):
    base = CLASSIC_DIR / "png" / f"{color}_{number}.png"
    overlay = COLORBLIND_OVERLAY_DIR / f"{color}.png"
    out = COLORBLIND_DIR / "png" / f"{color}_{number}.png"
    run(["magick", "convert", str(base), str(overlay), "-composite", str(out)])


def create_not_playable(card):
    base = COLORBLIND_DIR / "png" / f"{card}.png"
    overlay = COLORBLIND_OVERLAY_DIR / "not_playable.png"
    out = COLORBLIND_DIR / "png_not_playable" / f"{card}.png"

    run(
        [
            "magick",
            "convert",
            str(base),
            "-modulate",
            "75,20",
            "-brightness-contrast",
            "0x10",
            str(overlay),
            "-composite",
            str(out),
        ]
    )


def convert_png_to_webp(suffix):
    for color in COLORS:
        for number in NUMBERS:
            card = f"{color}_{number}"
            png = COLORBLIND_DIR / f"png{suffix}" / f"{card}.png"
            webp = COLORBLIND_DIR / f"webp{suffix}" / f"{card}.webp"
            run(["magick", "convert", str(png), "-define", "webp:lossless=true", str(webp)])

    for special in SPECIALS:
        png = COLORBLIND_DIR / f"png{suffix}" / f"{special}.png"
        webp = COLORBLIND_DIR / f"webp{suffix}" / f"{special}.webp"
        run(["magick", "convert", str(png), "-define", "webp:lossless=true", str(webp)])


def main():
    (COLORBLIND_DIR / "png").mkdir(parents=True, exist_ok=True)
    (COLORBLIND_DIR / "png_not_playable").mkdir(parents=True, exist_ok=True)
    (COLORBLIND_DIR / "webp").mkdir(parents=True, exist_ok=True)
    (COLORBLIND_DIR / "webp_not_playable").mkdir(parents=True, exist_ok=True)

    for color in COLORS:
        for number in NUMBERS:
            overlay_image(color, number)

    for special in SPECIALS:
        copyfile(
            CLASSIC_DIR / "png" / f"{special}.png",
            COLORBLIND_DIR / "png" / f"{special}.png",
        )

    for color in COLORS:
        for number in NUMBERS:
            create_not_playable(f"{color}_{number}")

    for special in SPECIALS:
        create_not_playable(special)

    convert_png_to_webp("")
    convert_png_to_webp("_not_playable")


if __name__ == "__main__":
    main()
