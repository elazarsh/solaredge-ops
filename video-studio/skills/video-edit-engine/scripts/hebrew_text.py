#!/usr/bin/env python3
"""Hebrew-safe text rendering for video frames (Pillow + RAQM).

Why this exists: OpenCV's cv2.putText cannot shape right-to-left text, so Hebrew comes out
mirrored or as boxes. Pillow with the RAQM layout engine (libraqm + fribidi) shapes RTL correctly
and keeps an English word inside a Hebrew line as one left-to-right unit.

This module FAILS LOUDLY when RAQM is missing, because silently falling back to basic layout
produces reversed Hebrew that looks plausible until a native reader sees it.

    from hebrew_text import render_text
    img = render_text("שלום Falafel Pro Max", "Heebo-Bold.ttf", 96, max_width=900)
    frame.alpha_composite(img, (x, y))        # frame: PIL RGBA image
"""
from __future__ import annotations

import argparse
from typing import Optional, Sequence

from PIL import Image, ImageDraw, ImageFont, features


def require_raqm() -> None:
    if not features.check("raqm"):
        raise RuntimeError(
            "Pillow was built without RAQM, so Hebrew would render reversed. Install libraqm "
            "(apt: libraqm0 / brew: libraqm) and reinstall Pillow: pip install --force-reinstall pillow"
        )


def load_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    require_raqm()
    return ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)


def wrap_lines(text: str, font: ImageFont.FreeTypeFont, max_width: Optional[int], direction: str) -> list[str]:
    """Greedy word wrap in LOGICAL order (first word first), which is correct for RTL as well."""
    if not max_width:
        return text.split("\n")
    lines: list[str] = []
    for para in text.split("\n"):
        current = ""
        for word in para.split():
            trial = f"{current} {word}".strip()
            if current and font.getlength(trial, direction=direction, language="he") > max_width:
                lines.append(current)
                current = word
            else:
                current = trial
        lines.append(current)
    return lines


def render_text(
    text: str,
    font_path: str,
    size: int,
    fill: Sequence[int] = (255, 255, 255, 255),
    stroke_width: int = 0,
    stroke_fill: Sequence[int] = (0, 0, 0, 255),
    direction: str = "rtl",
    align: str = "center",
    max_width: Optional[int] = None,
    line_spacing: float = 1.15,
    padding: int = 8,
) -> Image.Image:
    """Return a tight RGBA image of ``text``. ``direction`` is 'rtl' for Hebrew/Arabic, else 'ltr'."""
    if direction not in ("rtl", "ltr"):
        raise ValueError("direction must be 'rtl' or 'ltr'")
    font = load_font(font_path, size)
    lines = wrap_lines(text, font, max_width, direction)
    widths = [font.getlength(ln, direction=direction, language="he" if direction == "rtl" else "en") for ln in lines]
    line_h = int(size * line_spacing)
    box_w = int(max(widths, default=0)) + 2 * (padding + stroke_width)
    box_h = line_h * len(lines) + 2 * (padding + stroke_width)
    img = Image.new("RGBA", (max(box_w, 1), max(box_h, 1)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for i, (ln, w) in enumerate(zip(lines, widths)):
        if align == "center":
            x = (box_w - w) / 2
        elif align == "right":
            x = box_w - w - padding - stroke_width
        else:
            x = padding + stroke_width
        draw.text(
            (x, padding + stroke_width + i * line_h),
            ln,
            font=font,
            fill=tuple(fill),
            direction=direction,
            language="he" if direction == "rtl" else "en",
            stroke_width=stroke_width,
            stroke_fill=tuple(stroke_fill),
        )
    return img


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Render a Hebrew text sample to a PNG (sanity check)")
    ap.add_argument("text")
    ap.add_argument("--font", required=True)
    ap.add_argument("--size", type=int, default=96)
    ap.add_argument("--out", default="hebrew_sample.png")
    ap.add_argument("--direction", default="rtl", choices=["rtl", "ltr"])
    ap.add_argument("--max-width", type=int, default=None)
    args = ap.parse_args(argv)
    render_text(args.text, args.font, args.size, direction=args.direction, max_width=args.max_width).save(args.out)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
