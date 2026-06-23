from io import BytesIO
from pathlib import Path
from typing import Final, TypeAlias

from PIL import Image, ImageDraw, ImageFont, ImageOps

from text_utils import wrap_text

FontCandidate: TypeAlias = tuple[Path, int]
Point: TypeAlias = tuple[int, int]

FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
FONT_CANDIDATES: Final[tuple[FontCandidate, ...]] = (
    (FONT_DIR / "malgun.ttf", 0),
    (Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"), 0),
    (Path("/Library/Fonts/Malgun.ttf"), 0),
    (Path.home() / "Library/Fonts/Malgun.ttf", 0),
)
CANVAS_SIZE: Final[tuple[int, int]] = (800, 1200)
PANEL_LEFT: Final[int] = 95
PANEL_TOP: Final[int] = 70
PANEL_RIGHT: Final[int] = 705
PANEL_BOTTOM: Final[int] = 1000
OUTER_BORDER_WIDTH: Final[int] = 42
INNER_BORDER_WIDTH: Final[int] = 10
RIBBON_WIDTH: Final[int] = 48
PHOTO_WIDTH: Final[int] = 290
PHOTO_HEIGHT: Final[int] = 360
PHOTO_TOP: Final[int] = 250
PHOTO_LEFT: Final[int] = (CANVAS_SIZE[0] - PHOTO_WIDTH) // 2
ID_Y: Final[int] = 680
MESSAGE_Y: Final[int] = 770
ID_WIDTH: Final[int] = 620
MESSAGE_WIDTH: Final[int] = 620
ID_MAX_SIZE: Final[int] = 52
ID_MIN_SIZE: Final[int] = 24
NAME_SIZE_STEP: Final[int] = 2
NAME_COLOR: Final[tuple[int, int, int]] = (34, 34, 230)
MESSAGE_COLOR: Final[tuple[int, int, int]] = (36, 36, 36)
BACKGROUND_COLOR: Final[tuple[int, int, int]] = (20, 20, 20)
FRAME_COLOR: Final[tuple[int, int, int]] = (18, 18, 18)
FRAME_HIGHLIGHT: Final[tuple[int, int, int]] = (56, 56, 56)
PANEL_COLOR: Final[tuple[int, int, int]] = (246, 246, 246)
PANEL_EDGE: Final[tuple[int, int, int]] = (225, 225, 225)
PLACEHOLDER_COLOR: Final[tuple[int, int, int]] = (232, 232, 232)
TOP_RIBBON_APEX: Final[Point] = (CANVAS_SIZE[0] // 2, PANEL_TOP - 24)
TOP_RIBBON_LEFT_BASE: Final[Point] = (PANEL_LEFT + RIBBON_WIDTH // 2, PANEL_TOP + 150)
TOP_RIBBON_RIGHT_BASE: Final[Point] = (PANEL_RIGHT - RIBBON_WIDTH // 2, PANEL_TOP + 150)


def load_korean_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path, index in FONT_CANDIDATES:
        if not font_path.exists():
            continue

        try:
            return ImageFont.truetype(font_path.as_posix(), size, index=index)
        except OSError:
            continue

    return ImageFont.load_default(size=size)


def fit_font_to_width(
    text: str,
    max_width: int,
    initial_size: int,
    minimum_size: int,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for size in range(initial_size, minimum_size - 1, -NAME_SIZE_STEP):
        font = load_korean_font(size)
        if font.getlength(text) <= max_width:
            return font

    return load_korean_font(minimum_size)


def wrap_centered_text(
    text: str,
    max_width: int,
    initial_size: int,
    minimum_size: int,
) -> tuple[list[str], ImageFont.FreeTypeFont | ImageFont.ImageFont]:
    for size in range(initial_size, minimum_size - 1, -NAME_SIZE_STEP):
        font = load_korean_font(size)
        lines = wrap_text(text, font, max_width)
        if len(lines) <= 2:
            return lines, font

    fallback_font = load_korean_font(minimum_size)
    return wrap_text(text, fallback_font, max_width), fallback_font


def load_avatar_image(avatar_bytes: bytes | None) -> Image.Image | None:
    if avatar_bytes is None:
        return None

    return Image.open(BytesIO(avatar_bytes)).convert("RGBA")


def paste_memorial_photo(
    canvas: Image.Image,
    avatar_image: Image.Image | None,
) -> None:
    draw = ImageDraw.Draw(canvas)
    photo_box = (
        PHOTO_LEFT,
        PHOTO_TOP,
        PHOTO_LEFT + PHOTO_WIDTH,
        PHOTO_TOP + PHOTO_HEIGHT,
    )
    outer_box = (
        PHOTO_LEFT - 10,
        PHOTO_TOP - 10,
        PHOTO_LEFT + PHOTO_WIDTH + 10,
        PHOTO_TOP + PHOTO_HEIGHT + 10,
    )
    draw.rectangle(outer_box, fill=(24, 24, 24))
    draw.rectangle(photo_box, fill=PLACEHOLDER_COLOR)

    if avatar_image is None:
        return

    photo = ImageOps.fit(avatar_image, (PHOTO_WIDTH, PHOTO_HEIGHT), centering=(0.5, 0.35))
    canvas.paste(photo, (PHOTO_LEFT, PHOTO_TOP))


def draw_top_ribbon(draw: ImageDraw.ImageDraw) -> None:
    ribbon_points = (TOP_RIBBON_LEFT_BASE, TOP_RIBBON_APEX, TOP_RIBBON_RIGHT_BASE)
    draw.line(ribbon_points, fill=FRAME_COLOR, width=RIBBON_WIDTH, joint="curve")
    draw.line(ribbon_points, fill=FRAME_HIGHLIGHT, width=3, joint="curve")


def draw_memorial_frame(draw: ImageDraw.ImageDraw) -> None:
    draw.rounded_rectangle(
        (PANEL_LEFT - OUTER_BORDER_WIDTH, PANEL_TOP - OUTER_BORDER_WIDTH, PANEL_RIGHT + OUTER_BORDER_WIDTH, PANEL_BOTTOM + OUTER_BORDER_WIDTH),
        radius=16,
        fill=FRAME_COLOR,
    )
    draw.rounded_rectangle(
        (PANEL_LEFT - INNER_BORDER_WIDTH, PANEL_TOP - INNER_BORDER_WIDTH, PANEL_RIGHT + INNER_BORDER_WIDTH, PANEL_BOTTOM + INNER_BORDER_WIDTH),
        radius=8,
        outline=FRAME_HIGHLIGHT,
        width=INNER_BORDER_WIDTH,
    )
    draw.rectangle((PANEL_LEFT, PANEL_TOP, PANEL_RIGHT, PANEL_BOTTOM), fill=PANEL_COLOR)
    draw.rectangle((PANEL_LEFT, PANEL_TOP, PANEL_RIGHT, PANEL_BOTTOM), outline=PANEL_EDGE, width=2)
    draw_top_ribbon(draw)
    draw.rounded_rectangle((42, 300, 76, 690), radius=18, fill=(30, 30, 30))
    draw.rounded_rectangle((724, 300, 758, 690), radius=18, fill=(30, 30, 30))


def generate_funeral_image(
    author_name: str,
    message_content: str,
    avatar_bytes: bytes | None = None,
) -> Image.Image:
    canvas = Image.new("RGB", CANVAS_SIZE, BACKGROUND_COLOR)
    draw = ImageDraw.Draw(canvas)

    draw_memorial_frame(draw)

    id_lines, font_name = wrap_centered_text(author_name, ID_WIDTH, ID_MAX_SIZE, ID_MIN_SIZE)
    message_lines, font_content = wrap_centered_text(
        f'"{message_content}"',
        MESSAGE_WIDTH,
        42,
        28,
    )

    avatar_image = load_avatar_image(avatar_bytes)
    paste_memorial_photo(canvas, avatar_image)

    y_offset = ID_Y
    for line in id_lines:
        draw.text((400, y_offset), line, fill=NAME_COLOR, font=font_name, anchor="mm")
        y_offset += 54

    message_y = max(MESSAGE_Y, y_offset + 32)
    for line in message_lines:
        draw.text((400, message_y), line, fill=MESSAGE_COLOR, font=font_content, anchor="mm")
        message_y += 56

    return canvas
