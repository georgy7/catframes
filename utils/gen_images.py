#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Георгий Устинов
License: zlib/libpng
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from typing import Callable, List, Tuple, Union
from dataclasses import dataclass
import math
import re
from time import monotonic
import cairo


TITLE = "gen_images.py"

DESCRIPTION = """
  Test data generator for Catframes.

  This script is a part of Catframes repository.
  https://github.com/georgy7/catframes
"""


class ConsoleInterface:
    __slots__ = ('destination',)

    def __init__(self) -> None:
        self.destination: Path = Path()

        parser = ArgumentParser(prog=TITLE, description=DESCRIPTION,
            formatter_class=RawDescriptionHelpFormatter)

        parser.add_argument('destination', metavar='DESTINATION', nargs=1,
            help="The output folder path. It doesn't have to exist.")

        args = parser.parse_args()

        p: Path = Path(args.destination[0]).expanduser().absolute()

        if p.is_dir() or (p.parent.is_dir() and not p.exists()):
            self.destination = p
        elif p.is_file():
            parser.error('The destination must be a folder, not a file.')
        elif not p.parent.is_dir():
            parser.error('A parent folder of the destination folder must exist.')
        else:
            parser.error('Something wrong with the destination path.')


Context = cairo.Context
FPoint = Tuple[float, float]
VertexShader = Callable[[List[FPoint]], List[FPoint]]
RGB = Tuple[float, float, float]


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


def construct_angle(center: FPoint, angle: float, distance: float) -> FPoint:
    """Returns the coordinates of a point obtained by rotating
    a horizontal segment counterclockwise in radians.
    """
    return (
        center[0] + math.cos(angle)*distance,
        center[1] - math.sin(angle)*distance
    )


def get_distance(a: FPoint, b: FPoint) -> float:
    return math.sqrt(
        math.pow(a[0]-b[0], 2) +
        math.pow(a[1]-b[1], 2)
    )


def get_center(vertices: List[FPoint]) -> FPoint:
    cx: float = sum(x[0] for x in vertices) / len(vertices)
    cy: float = sum(x[1] for x in vertices) / len(vertices)
    return (cx, cy)


def construct_perpendicular(corner: FPoint, angle: float, distance: float, flip: bool) -> FPoint:
    angle90: float = \
        angle-math.pi/2 if flip \
        else angle+math.pi/2

    return construct_angle(corner, angle90, distance)


def draw_one_two_right_triangle(ctx: Context,
                                corner: FPoint,
                                length: int,
                                angle: float,
                                style: Style,
                                flip: bool = False):
    """To draw a right-angled triangle based on the coordinates of the right angle,
    the length of the largest side, and the angle of its rotation in radians (counterclockwise).
    The ratio of its catheti is two to one.
    The short side is counterclockwise relative to the larger one.
    The flip parameter does it clockwise.
    """
    far: FPoint = construct_angle(corner, angle, length)
    near: FPoint = construct_perpendicular(corner, angle, 0.5*length, flip)

    points: List[FPoint] = [corner, far, near]

    if style.shader:
        points = style.shader(points)

    ctx.move_to(points[0][0], points[0][1])
    ctx.line_to(points[1][0], points[1][1])
    ctx.line_to(points[2][0], points[2][1])
    ctx.close_path()

    will_stroke: bool = (style.width > 0) and bool(style.outline)

    if style.fill:
        ctx.set_source_rgb(*style.fill)
        if will_stroke:
            ctx.fill_preserve()
        else:
            ctx.fill()

    if will_stroke:
        ctx.set_line_width(style.width*2)
        ctx.set_source_rgb(*style.outline)
        ctx.clip_preserve()
        ctx.stroke()
        ctx.reset_clip()


def make_scale_shader(scale: float) -> VertexShader:
    def scale_shader(vertices: List[FPoint]) -> List[FPoint]:
        cx, cy = get_center(vertices)
        x: List[float] = [((v[0]-cx)*scale)+cx for v in vertices]
        y: List[float] = [((v[1]-cy)*scale)+cy for v in vertices]
        return list(zip(x, y))
    return scale_shader


def clear(ctx: Context, color: RGB) -> None:
    ctx.rectangle(0, 0, ctx.get_target().get_width(), ctx.get_target().get_height())
    ctx.set_source_rgb(*color)
    ctx.fill()


def main() -> None:
    cli = ConsoleInterface()
    cli.destination.mkdir(exist_ok=True)

    style: Style = Style(fill=to_srgb('#888'), outline=None, width=1, shader=make_scale_shader(0.85))

    target_image_size: Tuple[int, int] = (640, 480)
    render_size: Tuple[int, int] = target_image_size

    step_angle: float = math.tau / 10
    render_center: FPoint = (round(render_size[0]/2), round(render_size[1]/2))
    radius: int = round(render_size[0] * 0.078125)

    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, *render_size)
    ctx = cairo.Context(surface)

    for i in range(20):
        clear(ctx, to_srgb('#fff'))
        print(f'{i}.png')

        draw_one_two_right_triangle(ctx, render_center, radius, i*step_angle, style, True)
        draw_one_two_right_triangle(ctx, render_center, radius, i*step_angle, style, False)

        surface.write_to_png(str(cli.destination / f'{i}.png'))

    print('TODO generate images')


if __name__ == "__main__":
    start_time = monotonic()
    main()
    print(monotonic() - start_time)
