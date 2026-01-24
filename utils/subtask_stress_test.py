from pathlib import Path
from typing import Callable, List, Tuple, Union
from dataclasses import replace
import math
import cairo
import gzip
import io

from render_utils import *
from geometry_utils import *


PINWHEEL_OBTUSE_ANGLE = math.atan(2/1)


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
                              image_size: ImageSize,
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
        (0, image_size[1]-1),
        (image_size[0]-1, image_size[1]-1),
        (image_size[0]-1, 0)
    ]

    screen_borders: List[Segment] = [
        (screen_corners[0], screen_corners[1]),
        (screen_corners[1], screen_corners[2]),
        (screen_corners[2], screen_corners[3]),
        (screen_corners[3], screen_corners[0]),
    ]

    screen_center: FPoint = (image_size[0]/2, image_size[1]/2)

    if not is_on_screen(image_size, corner) and not is_on_screen(image_size, far) and not is_on_screen(image_size, near) \
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

    if depth > 9:
        scale = 0.85        # 85%

        # В вертушке отношения катетов - один к двум,
        # а отношение короткого катета к гипотенузе - один к корню из пяти,
        # и это соотношение продолжается рекурсивно.

        # Когда мы уменьшаем длинный катет на N, короткий катет уменьшается на N/2,
        # а гипотенуза приближается к прямому углу на (N/2) / sqrt(5) * 2.

        scaled_long_size: float = scale * new_long_side

        diff_n: float = new_long_side - scaled_long_size

        # При этом, нетрудно сообразить, что если мы сдвинем весь треугольник
        # от прямого угла вдоль длинного катета на величину K, отступ гипотенузы уменьшится на K/sqrt(5),
        # а если мы сдвинем треугольник вдоль короткого катета на L, уменьшится на 2L/sqrt(5).

        # Поскольку мы хотим, чтобы все отступы были одинаковыми, K = L.
        # Назовём эту величину просто X. Тогда отступ гипотенузы (M) уменьшится
        # на X/sqrt(5) и на 2X/sqrt(5).

        # M = (N/2) / sqrt(5) * 2 - (X + 2X) / sqrt(5)
        # M = N / sqrt(5) - 3X / sqrt(5)
        # M = (N - 3X) / sqrt(5)

        # Поскольку мы хотим, чтобы все отступы были одинаковыми, M = X.

        # X = N / sqrt(5) - 3X / sqrt(5)
        # X + 3X / sqrt(5) = N / sqrt(5)
        # X + X * 3 / sqrt(5) = N / sqrt(5)

        # 2.34164 * X = N / sqrt(5)
        # X = N / sqrt(5) / 2.34164
        # X = N * 0.1909830697715951

        x: float = diff_n * 0.1909830697715951

        style: Style = Style(fill=to_srgb('#888'), outline=None, width=1)

        def tune(angle: float, flipped: bool) -> Style:
            long_shift: FPoint = construct_angle_diff(angle, x)
            short_shift: FPoint = construct_angle_diff(get_perpendicular_angle(angle, flipped), x)
            shift: FPoint = sum_points(long_shift, short_shift)
            return replace(style, shader=make_shift_shader(shift), fill=to_srgb('#088'))

        def draw_shortcut(c: FPoint, l: float, a: float, f: bool):
            draw_one_two_right_triangle(ctx, c, l, a, tune(a, f), f)

        draw_shortcut(c2, scaled_long_size, c2_long_side_angle, flip)
        draw_shortcut(c2, scaled_long_size, c2_long_side_angle, not flip)

        draw_shortcut(c1, scaled_long_size, c2_angle+math.pi, not flip)

        draw_shortcut(c3, scaled_long_size, c2_long_side_angle, not flip)
        draw_shortcut(c3, scaled_long_size, c2_long_side_angle+math.pi, flip)

    elif depth > 0:
        draw_pinwheel_tiling_step(ctx, image_size, c2, new_long_side, c2_long_side_angle, flip, depth+1)
        draw_pinwheel_tiling_step(ctx, image_size, c2, new_long_side, c2_long_side_angle, not flip, depth+1)

        draw_pinwheel_tiling_step(ctx, image_size, c1, new_long_side, c2_angle+math.pi, not flip, depth+1)

        draw_pinwheel_tiling_step(ctx, image_size, c3, new_long_side, c2_long_side_angle, not flip, depth+1)
        draw_pinwheel_tiling_step(ctx, image_size, c3, new_long_side, c2_long_side_angle+math.pi, flip, depth+1)


def draw_pinwheel_tiling(ctx: Context,
                         image_size: ImageSize,
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
    assert image_size[0] < radius
    center: FPoint = (
        image_size[0] - radius,
        image_size[1] / 2
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

    draw_pinwheel_tiling_step(ctx, image_size, top_level_corner, long_side, math.tau/4 - position_angle, False, 1)


def a_lot_of_frames(folder: Path) -> None:
    """Makes hundreds of thousands of compressed SVG frames for memory usage test.
    If Catframes accumulates file metadata in RAM, and not in the smartest way, it will
    eat up a gigabyte before it reaches the fifty thousandth frame. If the memory limits
    are exceeded, the test will fail.
    """
    render_size: ImageSize = (1920, 1080)

    # Here we are spinning a huge circle in fact.
    # And this angle determines the rotation speed.
    step_angle: float = math.tau / 300000
    disc_radius_px = 50000 / 360 * render_size[1]

    # TODO colors

    for i in range(1000):
        buffer = io.BytesIO()

        sfc = cairo.SVGSurface(buffer, render_size[0], render_size[1])
        ctx = cairo.Context(sfc)

        clear(ctx, to_srgb('#fff'), render_size)

        draw_pinwheel_tiling(ctx, render_size, disc_radius_px, i*step_angle)

        sfc.finish()
        sfc.flush()

        if i % 100 == 0:
            print(f'{i}.svgz')
        dest_file: Path = folder / f'{i}.svgz'

        with gzip.open(dest_file, "wb") as f:
            f.write(buffer.getvalue())


