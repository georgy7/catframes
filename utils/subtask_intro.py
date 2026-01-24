from render_utils import *
from geometry_utils import *


def render_intro(folder: Path) -> None:
    """Makes a short bright video to check compression artifacts.
    """
    render_size: ImageSize = (3840, 2160)

    step_angle: float = math.tau / 300000
    disc_radius_px = 50000 / 360 * render_size[1]

    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, *render_size)
    ctx = cairo.Context(surface)

    for i in range(100):
        clear(ctx, to_srgb('#fff'), render_size)

        # TODO Something pretty

        if i % 30 == 0:
            print(f'{i}.png')

        surface.write_to_png(str(folder / f'{i}.png'))

