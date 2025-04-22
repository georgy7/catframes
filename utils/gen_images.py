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

PINWHEEL_OBTUSE_ANGLE = math.atan(2/1)


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
Segment = Tuple[FPoint, FPoint]


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


def approx_intersects(a: Segment, b: Segment) -> bool:

    a_left = min(a[0][0], a[1][0])
    b_left = min(b[0][0], b[1][0])

    a_right = max(a[0][0], a[1][0])
    b_right = max(b[0][0], b[1][0])

    if not ((a_right >= b_left) and (a_left <= b_right)):
        return False

    a_top = min(a[0][1], a[1][1])
    b_top = min(b[0][1], b[1][1])

    a_bottom = max(a[0][1], a[1][1])
    b_bottom = max(b[0][1], b[1][1])

    if not ((a_bottom >= b_top) and (a_top <= b_bottom)):
        return False

    return True


def approx_have_intersections(a: List[Segment], b: List[Segment]) -> bool:
    for x in a:
        for y in b:
            if approx_intersects(x, y):
                return True
    return False


def is_on_screen(ctx, p: FPoint):
    return (0 <= p[0] < ctx.get_target().get_width()) and (0 <= p[1] < ctx.get_target().get_height())


def get_triangle_area(p: List[FPoint]) -> float:
    return abs((
        p[0][0]*(p[1][1]-p[2][1]) +
        p[1][0]*(p[2][1]-p[0][1]) +
        p[2][0]*(p[0][1]-p[1][1])
    )/2)


def is_in_the_triangle(p: FPoint, vertices: List[FPoint]):
    assert len(vertices) == 3
    triangle_area: float = get_triangle_area(vertices)
    a: float = get_triangle_area([vertices[0], vertices[1], p])
    b: float = get_triangle_area([vertices[1], vertices[2], p])
    c: float = get_triangle_area([vertices[2], vertices[0], p])
    return ((a+b+c) - triangle_area) / triangle_area < 0.001


def draw_one_two_right_triangle(ctx: Context,
                                corner: FPoint,
                                length: float,
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


def draw_pinwheel_tiling_step(ctx: Context,
                              corner: FPoint,
                              length: float,
                              angle: float,
                              flip: bool,
                              depth: int):

    # Checking if the triangle is on the screen...
    far: FPoint = construct_angle(corner, angle, length)
    near: FPoint = construct_perpendicular(corner, angle, 0.5*length, flip)

    screen_corners: List[FPoint] = [
        (0, 0),
        (0, ctx.get_target().get_height()-1),
        (ctx.get_target().get_width()-1, ctx.get_target().get_height()-1),
        (ctx.get_target().get_width()-1, 0)
    ]

    screen_borders: List[Segment] = [
        (screen_corners[0], screen_corners[1]),
        (screen_corners[1], screen_corners[2]),
        (screen_corners[2], screen_corners[3]),
        (screen_corners[3], screen_corners[0]),
    ]

    screen_center: FPoint = (ctx.get_target().get_width()/2, ctx.get_target().get_height()/2)

    if not is_on_screen(ctx, corner) and not is_on_screen(ctx, far) and not is_on_screen(ctx, near) \
            and not is_in_the_triangle(screen_center, [corner, far, near]) \
            and not approx_have_intersections([(corner, near), (corner, far), (near, far)], screen_borders):
        return

    # new_small_side = (length / 2) / Math.sqrt(5)
    # new_small_side = length * 0.5 / Math.sqrt(5)
    new_small_side: float = length * 0.22360679774997896
    new_long_side: float = 2 * new_small_side

    c2_angle: float = angle - PINWHEEL_OBTUSE_ANGLE if flip \
        else angle + PINWHEEL_OBTUSE_ANGLE

    c2: FPoint = construct_angle(corner, c2_angle, new_small_side)
    c1: FPoint = construct_angle(corner, c2_angle, 2 * new_small_side)
    c3: FPoint = construct_angle(c2, angle, 0.5 * length)

    c2_long_side_angle = c2_angle + math.tau/4 if flip \
        else c2_angle - math.tau/4

    if depth > 8:
        style: Style = Style(fill=to_srgb('#888'), outline=None, width=1, shader=make_scale_shader(0.85))

        draw_one_two_right_triangle(ctx, c2, new_long_side, c2_long_side_angle, style, flip)
        draw_one_two_right_triangle(ctx, c2, new_long_side, c2_long_side_angle, style, not flip)

        draw_one_two_right_triangle(ctx, c1, new_long_side, c2_angle+math.pi, style, not flip)

        draw_one_two_right_triangle(ctx, c3, new_long_side, c2_long_side_angle, style, not flip)
        draw_one_two_right_triangle(ctx, c3, new_long_side, c2_long_side_angle+math.pi, style, flip)

    elif depth > 0:
        draw_pinwheel_tiling_step(ctx, c2, new_long_side, c2_long_side_angle, flip, depth+1)
        draw_pinwheel_tiling_step(ctx, c2, new_long_side, c2_long_side_angle, not flip, depth+1)

        draw_pinwheel_tiling_step(ctx, c1, new_long_side, c2_angle+math.pi, not flip, depth+1)

        draw_pinwheel_tiling_step(ctx, c3, new_long_side, c2_long_side_angle, not flip, depth+1)
        draw_pinwheel_tiling_step(ctx, c3, new_long_side, c2_long_side_angle+math.pi, flip, depth+1)


def draw_pinwheel_tiling(ctx: Context,
                         radius: float,
                         position_angle: float):
    """In order not to get stuck with the peculiarities of the relative arrangement
    of triangles, I decided to go from larger to smaller. I recursively split a huge
    triangle, discarding parts that do not fall within the visible area.
    To get a smooth, continuous movement, we will circle inside this giant triangle
    along a reduced inscribed circle.
    To simplify this, let the long side of the triangle be strictly vertical,
    with the right angle at the bottom and the short side on the left.
    """
    assert ctx.get_target().get_width() < radius
    center: FPoint = (
        ctx.get_target().get_width() - radius,
        ctx.get_target().get_height() / 2
    )
    top_level_corner: FPoint = construct_angle(
        center,
        -(position_angle + math.tau/8),
        math.sqrt(2) * radius
    )

    # short_side = radius + radius / math.tan(math.atan(2/1) / 2)
    # short_side = radius + radius / 0.6180339887498948
    # short_side = radius + radius * (1 / 0.6180339887498948)
    # short_side = radius + radius * 1.618033988749895
    # short_side = 2.618033988749895 * radius
    # long_side = 2 * short_side

    long_side = 2 * 2.618033988749895 * radius

    draw_pinwheel_tiling_step(ctx, top_level_corner, long_side, math.tau/4 - position_angle, False, 1)


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

    target_image_size: Tuple[int, int] = (426, 240)
    render_size: Tuple[int, int] = target_image_size

    step_angle: float = math.tau / 2000

    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, *render_size)
    ctx = cairo.Context(surface)

    for i in range(20):
        clear(ctx, to_srgb('#fff'))
        print(f'{i}.png')

        draw_pinwheel_tiling(ctx, 42600, i*step_angle)

        surface.write_to_png(str(cli.destination / f'{i}.png'))

    print('TODO generate images')


if __name__ == "__main__":
    start_time = monotonic()
    main()
    print(monotonic() - start_time)
