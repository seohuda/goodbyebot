from pathlib import Path
from typing import Final, TypeAlias

from PIL import Image, ImageDraw, ImageFont

from text_utils import wrap_text

FontCandidate: TypeAlias = tuple[Path, int]

FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
FONT_CANDIDATES: Final[tuple[FontCandidate, ...]] = (
    (FONT_DIR / "malgun.ttf", 0),
    (Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"), 0),
    (Path("/Library/Fonts/Malgun.ttf"), 0),
    (Path.home() / "Library/Fonts/Malgun.ttf", 0),
)


def load_korean_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path, index in FONT_CANDIDATES:
        if not font_path.exists():
            continue

        try:
            return ImageFont.truetype(font_path.as_posix(), size, index=index)
        except OSError:
            continue

    return ImageFont.load_default(size=size)


def generate_funeral_image(author_name: str, message_content: str) -> Image.Image:
    canvas = Image.new("RGB", (800, 1000), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)

    draw.rectangle([(20, 20), (780, 980)], outline=(100, 100, 100), width=10)

    draw.polygon([(20, 20), (120, 20), (20, 120)], fill=(0, 0, 0))
    draw.polygon([(780, 20), (680, 20), (780, 120)], fill=(0, 0, 0))

    font_title = load_korean_font(60)
    font_content = load_korean_font(45)
    font_bottom = load_korean_font(40)

    draw.text((400, 150), f"故 {author_name}", fill=(255, 255, 255), font=font_title, anchor="mm")
    draw.text((400, 900), "삼가 고인의 명복을 빕니다", fill=(200, 200, 200), font=font_bottom, anchor="mm")

    wrapped_lines = wrap_text(f'"{message_content}"', font_content, 700)

    total_text_height = len(wrapped_lines) * 60
    y_offset = (1000 - total_text_height) // 2

    for line in wrapped_lines:
        draw.text((400, y_offset), line, fill=(255, 255, 255), font=font_content, anchor="mm")
        y_offset += 60

    return canvas
