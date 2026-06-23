from pathlib import Path

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
