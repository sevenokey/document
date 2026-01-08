#!/usr/bin/env python3
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


@dataclass(frozen=True)
class Segment:
    duration: float
    height: float


def clamp(value: float, lo: float, hi: float) -> float:
    return lo if value < lo else hi if value > hi else value


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_in_out_cubic(t: float) -> float:
    t = clamp(t, 0.0, 1.0)
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - pow(-2.0 * t + 2.0, 3.0) / 2.0


def build_bounce_segments(total_duration: float) -> list[Segment]:
    segments: list[Segment] = []
    height = 120.0
    base_duration = 0.55
    restitution = 0.62

    remaining = total_duration
    while remaining > 0.06:
        duration = min(base_duration * math.sqrt(max(height, 1.0) / 120.0), remaining)
        segments.append(Segment(duration=duration, height=height))
        remaining -= duration
        height *= restitution
        base_duration *= 0.82

        if height < 10.0:
            break

    if remaining > 0:
        segments.append(Segment(duration=remaining, height=max(height, 6.0)))

    return segments


def bounce_center_y(t: float, segments: list[Segment], ground_y: float, radius: float) -> float:
    t = clamp(t, 0.0, 1.0)
    total = sum(s.duration for s in segments)
    time = t * total
    cursor = 0.0

    for segment in segments:
        if cursor + segment.duration >= time:
            local = (time - cursor) / max(segment.duration, 1e-9)
            local = ease_in_out_cubic(local)
            parabola = 1.0 - (2.0 * local - 1.0) ** 2  # 0 at ends, 1 at mid
            return (ground_y - radius) - segment.height * parabola
        cursor += segment.duration

    return ground_y - radius


def render_frame(
    size: tuple[int, int],
    radius: float,
    x: float,
    center_y_no_squish: float,
    ground_y: float,
    contact: float,
) -> Image.Image:
    width, height = size
    bg = Image.new("RGBA", (width, height), (248, 250, 252, 255))

    draw = ImageDraw.Draw(bg)

    # Ground line
    draw.line([(0, ground_y + 0.5), (width, ground_y + 0.5)], fill=(220, 224, 230, 255), width=2)

    # Shadow (bigger & darker near contact)
    shadow_max_w = radius * 2.2
    shadow_min_w = radius * 1.0
    shadow_w = lerp(shadow_min_w, shadow_max_w, contact)
    shadow_h = lerp(radius * 0.22, radius * 0.34, contact)
    shadow_alpha = int(lerp(30, 90, contact))
    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_box = (
        x - shadow_w / 2.0,
        ground_y - shadow_h / 2.0,
        x + shadow_w / 2.0,
        ground_y + shadow_h / 2.0,
    )
    shadow_draw.ellipse(shadow_box, fill=(0, 0, 0, shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=2))
    bg.alpha_composite(shadow)

    # Ball squish
    xscale = 1.0 + 0.25 * contact
    yscale = 1.0 - 0.25 * contact
    rx = radius * xscale
    ry = radius * yscale
    center_y = center_y_no_squish + (radius - ry) * contact

    ball = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ball_draw = ImageDraw.Draw(ball)
    ball_box = (x - rx, center_y - ry, x + rx, center_y + ry)
    ball_color = (255, 59, 48, 255)
    ball_draw.ellipse(ball_box, fill=ball_color)

    # Highlight
    hx = x - rx * 0.28
    hy = center_y - ry * 0.35
    highlight_box = (hx - rx * 0.35, hy - ry * 0.35, hx + rx * 0.05, hy + ry * 0.05)
    ball_draw.ellipse(highlight_box, fill=(255, 255, 255, 120))

    # Soft shading
    shade = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    shade_box = (x - rx * 0.95, center_y - ry * 0.95, x + rx * 0.95, center_y + ry * 0.95)
    shade_draw.ellipse(shade_box, outline=(0, 0, 0, 40), width=3)
    shade = shade.filter(ImageFilter.GaussianBlur(radius=1))
    ball.alpha_composite(shade)

    bg.alpha_composite(ball)
    return bg.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)


def main() -> None:
    out_path = Path("dist/bouncing_ball.gif")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    size = (256, 256)
    radius = 28.0
    ground_y = 210.0
    x = size[0] / 2.0

    fps = 50
    seconds = 2.2
    frame_count = max(1, int(fps * seconds))

    segments = build_bounce_segments(total_duration=seconds)
    frames: list[Image.Image] = []

    min_center_y = ground_y - radius
    contact_zone = radius * 0.65

    for i in range(frame_count):
        t = i / (frame_count - 1) if frame_count > 1 else 0.0
        center_y_no_squish = bounce_center_y(t, segments, ground_y=ground_y, radius=radius)
        dist_to_ground = max(0.0, min_center_y - center_y_no_squish)
        contact = clamp(1.0 - dist_to_ground / max(contact_zone, 1e-9), 0.0, 1.0)
        frames.append(
            render_frame(
                size=size,
                radius=radius,
                x=x,
                center_y_no_squish=center_y_no_squish,
                ground_y=ground_y,
                contact=contact,
            )
        )

    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(out_path)


if __name__ == "__main__":
    main()
