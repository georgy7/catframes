#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Георгий Устинов
License: zlib/libpng
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from enum import Enum
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Sequence, Tuple, Union
from dataclasses import dataclass
from PIL import Image, ImageColor, ImageDraw
import math


TITLE = "gen_images.py"

DESCRIPTION = """
  Test data generator for Catframes.

  This script is a part of Catframes repository.
  https://github.com/georgy7/catframes
"""


class ConsoleInterface:
    __slots__ = ('destination',)

    def __init__(self):
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


VertexShader = Callable[[List[Tuple[int, int]]], List[Tuple[int, int]]]


@dataclass(frozen=True)
class Style:
    fill: Union[str, None]
    outline: Union[str, None]
    width: int
    shader: Union[VertexShader, None] = None

    def __post_init__(self):
        assert bool(self.fill) or (bool(self.outline) and (self.width > 0))
        assert self.fill != ''
        assert self.outline != ''
        assert self.width >= 0


def draw_one_two_right_triangle(draw: ImageDraw.ImageDraw,
                                corner: Tuple[int, int],
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
    far: Tuple[int, int] = (
        corner[0] + round(math.cos(angle)*length),
        corner[1] - round(math.sin(angle)*length)
    )

    perpendicular: float = \
        angle-math.pi/2 if flip \
        else angle+math.pi/2

    near: Tuple[int, int] = (
        corner[0] + round(math.cos(perpendicular)*0.5*length),
        corner[1] - round(math.sin(perpendicular)*0.5*length)
    )

    points: List[Tuple[int, int]] = [corner, far, near]

    if style.shader:
        points = style.shader(points)

    draw.polygon(points,
        fill=style.fill, outline=style.outline,
        width=style.width)


def make_scale_shader(scale: float) -> VertexShader:
    def scale_shader(vertices: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        cx: float = sum(x[0] for x in vertices) / len(vertices)
        cy: float = sum(x[1] for x in vertices) / len(vertices)
        x: List[int] = [round(((v[0]-cx)*scale)+cx) for v in vertices]
        y: List[int] = [round(((v[1]-cy)*scale)+cy) for v in vertices]
        return list(zip(x, y))
    return scale_shader


def main() -> None:
    cli = ConsoleInterface()
    cli.destination.mkdir(exist_ok=True)

    render_factor: int = 3

    style: Style = Style(fill='#888', outline=None, width=1, shader=make_scale_shader(0.85))

    target_image_size: Tuple[int, int] = (640, 480)
    render_size: Tuple[int, int] = (target_image_size[0]*render_factor, target_image_size[1]*render_factor)

    step_angle: float = math.tau / 10
    render_center: Tuple[int, int] = (render_size[0]/2, render_size[1]/2)
    radius: int = round(render_size[0] * 0.078125)

    for i in range(20):
        image: Image.Image = Image.new("RGB", render_size, '#fff')
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)

        draw_one_two_right_triangle(draw, render_center, radius, i*step_angle, style, True)
        draw_one_two_right_triangle(draw, render_center, radius, i*step_angle, style, False)

        image.resize(target_image_size, Image.Resampling.BILINEAR).save(cli.destination / f'{i}.png')

    print('TODO generate images')


if __name__ == "__main__":
    main()
