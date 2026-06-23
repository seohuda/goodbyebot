from pathlib import Path
from io import BytesIO

from PIL import Image

import image_generator


def test_load_korean_font_uses_first_existing_candidate(monkeypatch, tmp_path) -> None:
    first_candidate = tmp_path / "missing.ttf"
    second_candidate = tmp_path / "present.ttf"
    second_candidate.write_bytes(b"")

    monkeypatch.setattr(
        image_generator,
        "FONT_CANDIDATES",
        ((first_candidate, 0), (second_candidate, 2)),
    )

    calls: list[tuple[Path, int, int]] = []

    def fake_truetype(
        font: str | Path,
        size: int,
        index: int = 0,
    ) -> tuple[str, str, int, int]:
        calls.append((Path(font), size, index))
        return ("font", Path(font).name, size, index)

    monkeypatch.setattr(image_generator.ImageFont, "truetype", fake_truetype)

    font = image_generator.load_korean_font(60)

    assert font == ("font", "present.ttf", 60, 2)
    assert calls == [(second_candidate, 60, 2)]


def test_generate_funeral_image_renders_avatar(monkeypatch) -> None:
    def fake_font(size: int) -> image_generator.ImageFont.ImageFont:
        return image_generator.ImageFont.load_default(size=size)

    monkeypatch.setattr(image_generator, "load_korean_font", fake_font)

    avatar = Image.new("RGBA", (32, 32), (255, 0, 0, 255))
    buffer = BytesIO()
    avatar.save(buffer, format="PNG")

    canvas = image_generator.generate_funeral_image(
        "장례식봇",
        "테스트 한글 메시지입니다",
        avatar_bytes=buffer.getvalue(),
    )

    assert canvas.getpixel((400, 320)) != (20, 20, 20)
