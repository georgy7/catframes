from render_utils import *
from geometry_utils import *

from intro.scene1_tv import render_scene1


RENDER_SIZE: ImageSize = (3840, 2160)

BPM = 190
FPS = 60


def render_intro(folder: Path) -> None:
    scenes = [
        (render_scene1, 1175),  # 19.5 секунд
        # (render_scene2, 16),
        # (render_scene3, 12),
        # (render_scene4, 4),
        # (render_scene5, 12),
    ]
    frame_index = 0
    for render_func, duration in scenes:
        for i in range(duration):
            frame_path = folder / f"{frame_index:04d}.png"
            render_func(frame_index, duration, i, RENDER_SIZE, frame_path)
            if frame_index % 100 == 0:
                print(f"\nFrame {frame_path.name} ", end='')
            elif frame_index % 10 == 0:
                print(".", end='', flush=True)
            frame_index += 1

    print(f"Intro: {frame_index} frames generated.")

