from pathlib import Path
import cairo
from typing import Callable, List, Tuple, Union
from dataclasses import dataclass
import math
import re

from geometry_utils import FPoint, VertexShader


Context = cairo.Context

ImageSize = Tuple[int, int]
RGB = Tuple[float, float, float]


def is_on_screen(image_size: ImageSize, p: FPoint):
    return (0 <= p[0] < image_size[0]) and (0 <= p[1] < image_size[1])


def clear(ctx: Context, color: RGB, render_size: ImageSize) -> None:
    w, h = render_size
    ctx.save()
    ctx.set_source_rgb(*color)
    ctx.rectangle(0, 0, w, h)
    ctx.fill()
    ctx.restore()


def to_srgb(x: Union[str, RGB]) -> RGB:
    if isinstance(x, tuple):
        return x

    assert x[0] == '#'
    assert len(x) in (4, 7)

    parts: List[str]
    channels: List[int]

    if len(x) == 4:
        parts = re.findall('.', x[1:])
        channels = [int(p+p, 16) for p in parts]
    else:
        parts = re.findall('..', x[1:])
        channels = [int(p, 16) for p in parts]

    return (channels[0]/255, channels[1]/255, channels[2]/255)


@dataclass(frozen=True)
class Style:
    fill: Union[RGB, None]
    outline: Union[RGB, None]
    width: int
    shader: Union[VertexShader, None] = None

    def __post_init__(self):
        assert bool(self.fill) or (bool(self.outline) and (self.width > 0))
        assert self.fill != ''
        assert self.outline != ''
        assert self.width >= 0


def draw_scanlines(ctx: cairo.Context, size: ImageSize, alpha: float = 0.05, line_height = 1) -> None:
    _, h = size
    ctx.save()
    ctx.set_source_rgba(0, 0, 0, alpha)
    for y in range(0, h, 2):
        ctx.move_to(0, y)
        ctx.line_to(size[0], y)
    ctx.set_line_width(line_height)
    ctx.stroke()
    ctx.restore()


def draw_curved_line(ctx: cairo.Context, x1, y1, x2, y2, curve: float):
    """Рисует линию с изгибом (для human-like feel)"""
    midx = (x1 + x2) / 2
    midy = (y1 + y2) / 2
    ctx.move_to(x1, y1)
    ctx.curve_to(midx - curve, midy, midx + curve, midy, x2, y2)

