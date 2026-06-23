from io import BytesIO
from pathlib import Path
from typing import Final, TypeAlias

from PIL import Image, ImageDraw, ImageFont, ImageOps

from text_utils import wrap_text

FontCandidate: TypeAlias = tuple[Path, int]

FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
FONT_CANDIDATES: Final[tuple[FontCandidate, ...]] = (
    (FONT_DIR / "malgun.ttf", 0),
    (Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"), 0),
    (Path("/Library/Fonts/Malgun.ttf"), 0),
    (Path.home() / "Library/Fonts/Malgun.ttf", 0),
)
CANVAS_SIZE: Final[tuple[int, int]] = (800, 1200)
AVATAR_SIZE: Final[int] = 260
AVATAR_TOP: Final[int] = 190
CONTENT_TOP: Final[int] = 540
BOTTOM_TEXT_Y: Final[int] = 1120
CONTENT_WIDTH: Final[int] = 680


def load_korean_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path, index in FONT_CANDIDATES:
        if not font_path.exists():
            continue

        try:
            return ImageFont.truetype(font_path.as_posix(), size, index=index)
        except OSError:
            continue

    return ImageFont.load_default(size=size)


def load_avatar_image(avatar_bytes: bytes | None) -> Image.Image | None:
    if avatar_bytes is None:
        return None

    return Image.open(BytesIO(avatar_bytes)).convert("RGBA")


def paste_circular_avatar(
    canvas: Image.Image,
    avatar_image: Image.Image | None,
    left: int,
    top: int,
) -> None:
    draw = ImageDraw.Draw(canvas)
    border_box = (left - 8, top - 8, left + AVATAR_SIZE + 8, top + AVATAR_SIZE + 8)
    draw.ellipse(border_box, outline=(120, 120, 120), width=6)

    if avatar_image is None:
        draw.ellipse((left, top, left + AVATAR_SIZE, top + AVATAR_SIZE), fill=(60, 60, 60))
        return

    avatar = ImageOps.fit(avatar_image, (AVATAR_SIZE, AVATAR_SIZE), centering=(0.5, 0.5))
    mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, AVATAR_SIZE - 1, AVATAR_SIZE - 1), fill=255)
    canvas.paste(avatar, (left, top), mask)


def generate_funeral_image(
    author_name: str,
    message_content: str,
    avatar_bytes: bytes | None = None,
) -> Image.Image:
    canvas = Image.new("RGB", CANVAS_SIZE, (20, 20, 20))
    draw = ImageDraw.Draw(canvas)

    draw.rectangle([(20, 20), (780, 1180)], outline=(100, 100, 100), width=10)

    draw.polygon([(20, 20), (120, 20), (20, 120)], fill=(0, 0, 0))
    draw.polygon([(780, 20), (680, 20), (780, 120)], fill=(0, 0, 0))

    font_title = load_korean_font(60)
    font_content = load_korean_font(42)
    font_bottom = load_korean_font(36)

    avatar_image = load_avatar_image(avatar_bytes)
    paste_circular_avatar(canvas, avatar_image, 270, AVATAR_TOP)

    draw.text((400, 130), f"故 {author_name}", fill=(255, 255, 255), font=font_title, anchor="mm")
    draw.text((400, BOTTOM_TEXT_Y), "삼가 고인의 명복을 빕니다", fill=(200, 200, 200), font=font_bottom, anchor="mm")

    wrapped_lines = wrap_text(f'"{message_content}"', font_content, CONTENT_WIDTH)

    y_offset = CONTENT_TOP

    for line in wrapped_lines:
        draw.text((400, y_offset), line, fill=(255, 255, 255), font=font_content, anchor="mm")
        y_offset += 56

    return canvas
