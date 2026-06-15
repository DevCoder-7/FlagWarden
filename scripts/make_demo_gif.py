from __future__ import annotations

from pathlib import Path

SCREENSHOT_DIR = Path("docs/screenshots")
OUTPUT_PATH = Path("docs/demo/flagwarden-demo.gif")
ORDERED_SCREENSHOTS = [
    "start.png",
    "challenge.png",
    "answer-correct.png",
    "score.png",
    "safety-policy.png",
]


def main() -> int:
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("Missing optional dependency: Pillow")
        print("Install it with: python -m pip install pillow")
        return 1

    paths = [SCREENSHOT_DIR / name for name in ORDERED_SCREENSHOTS]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        print("Missing screenshot files:")
        for path in missing:
            print(f"- {path}")
        print("Capture real Telegram screenshots first. See docs/screenshots/README.md.")
        return 1

    frames = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((900, 900))
        canvas = Image.new("RGB", (900, 900), "#0f172a")
        framed = ImageOps.contain(image, (840, 840))
        x = (900 - framed.width) // 2
        y = (900 - framed.height) // 2
        canvas.paste(framed, (x, y))
        frames.append(canvas)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=1400,
        loop=0,
        optimize=True,
    )
    print(f"Created {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
