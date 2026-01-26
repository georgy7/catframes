from pathlib import Path
import cairo
import math
from random import Random
from typing import List, Tuple

from render_utils import clear, to_srgb, mix_srgb, draw_scanlines
from geometry_utils import FPoint

# Цвета
BLACK = to_srgb('#000')
DARK_GRAY = to_srgb('#1a1a1a')
MID_GRAY = to_srgb('#222')
CRT_GLOW = to_srgb('#000818')
SIGNAL_BLUE = to_srgb('#00aaff')
SIGNAL_FADE = to_srgb('#004488')
STATIC_DARK = to_srgb('#001122')
HIGHLIGHT = to_srgb('#003366')
CHANNEL_GREEN = to_srgb('#33cc33')  # Салатовый, как на старых CRT

# Размеры
RENDER_WIDTH, RENDER_HEIGHT = 3840, 2160
TV_ASPECT = 4 / 3
TV_BASE_WIDTH = 2400
TV_BASE_HEIGHT = TV_BASE_WIDTH / TV_ASPECT
TV_X_CENTER = RENDER_WIDTH / 2
TV_Y_CENTER = RENDER_HEIGHT / 2
TV_LINES = 360

SCREEN_MARGIN = 180
SCREEN_BASE_W = TV_BASE_WIDTH - 2 * SCREEN_MARGIN
SCREEN_BASE_H = TV_BASE_HEIGHT - 2 * SCREEN_MARGIN

TOTAL_FRAMES = 1175
CRT_DEFORM_FRAMES = 30
CHANNEL_FRAME_DURATION = 60  # 1 секунда
NOISE_START = 300
PATTERN_START = 400
SIGNAL_START = 500
ZOOM_START = 600
TITLE_FRAME = 900
END_OF_POWER_ON_FLASH_PROGRESS = 0.025

NOISE_SOURCE = Random(1)


def ease_in(t: float) -> float:
    return t * t

def ease_out(t: float) -> float:
    return 1 - (1 - t) * (1 - t)

def ease_in_out(t: float) -> float:
    return t * t * (3 - 2 * t)

def noise(x: float, y: float, t: float, freq: float = 1.0) -> float:
    return (
        math.sin(x * 0.001 * freq + t * 0.1) * 0.5 +
        math.sin(y * 0.0015 * freq + t * 0.12) * 0.3 +
        math.sin(x * 0.0005 * freq + y * 0.0005 * freq + t * 0.08) * 0.2
    )

def hsv_pattern(t: float, x: float, y: float) -> Tuple[float, float, float]:
    """Что-то вроде лава-лампы"""
    h = (0.6 + 0.05 * math.sin(t * 0.3 + x * 0.001) + 0.03 * math.sin(t * 0.2 + y * 0.001)) % 1.0
    s = 0.05 + 0.05 * noise(x, y, t, 1.0)
    v = max(0, min(1, 0.1 + 0.3 * noise(x, y, t * 0.5, 2.0)))
    return h, s, v

def hsv_noise() -> Tuple[float, float, float]:
    h = NOISE_SOURCE.random()
    s = 0.4 * NOISE_SOURCE.random()
    v = 0.04 + 0.9 * NOISE_SOURCE.random()
    return h, s, v

def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[float, float, float]:
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i %= 6

    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q

    assert 0 <= r <= 1
    assert 0 <= g <= 1
    assert 0 <= b <= 1

    return to_srgb((r, g, b))


def draw_tv_body(ctx: cairo.Context, scale: float):
    w = TV_BASE_WIDTH * scale
    h = TV_BASE_HEIGHT * scale
    x = TV_X_CENTER - w / 2
    y = TV_Y_CENTER - h / 2

    gradient = cairo.LinearGradient(x, y, x, y + h * 0.7)
    gradient.add_color_stop_rgb(0, *MID_GRAY)
    gradient.add_color_stop_rgb(0.3, *DARK_GRAY)
    gradient.add_color_stop_rgb(1, *BLACK)
    ctx.set_source(gradient)
    ctx.rectangle(x, y, w, h)
    ctx.fill()

    shadow = cairo.LinearGradient(x + 50, y + h, x + 50, y + h + 100)
    shadow.add_color_stop_rgba(0, 0, 0, 0, 0.6 * scale)
    shadow.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(shadow)
    ctx.rectangle(x + 50, y + h, w - 100, 100)
    ctx.fill()


def draw_screen_frame(ctx: cairo.Context, scale: float):
    w = TV_BASE_WIDTH * scale
    h = TV_BASE_HEIGHT * scale
    x = TV_X_CENTER - w / 2
    y = TV_Y_CENTER - h / 2
    screen_w = SCREEN_BASE_W * scale
    screen_h = SCREEN_BASE_H * scale
    screen_x = x + SCREEN_MARGIN * scale
    screen_y = y + SCREEN_MARGIN * scale

    ctx.set_source_rgb(*to_srgb('#0a0a0a'))
    ctx.rectangle(screen_x, screen_y, screen_w, screen_h)
    ctx.fill()

    inner_shadow = cairo.RadialGradient(
        screen_x + screen_w / 2, screen_y + screen_h / 2, 0,
        screen_x + screen_w / 2, screen_y + screen_h / 2, screen_w / 2
    )
    inner_shadow.add_color_stop_rgba(0.8, 0, 0, 0, 0)
    inner_shadow.add_color_stop_rgba(1, 0, 0, 0, 0.4)
    ctx.set_source(inner_shadow)
    ctx.rectangle(screen_x, screen_y, screen_w, screen_h)
    ctx.fill()


def crt_deformation(frame_in_scene: int):
    """У CRT-экранов картинка никогда не доходит до краёв - всегда есть чёрный зазор.
    Эта функция возвращает её масштаб по горизонтали и вертикали относительно экрана.
    """
    start_frame = math.floor(TOTAL_FRAMES * END_OF_POWER_ON_FLASH_PROGRESS)
    end_frame = start_frame + CRT_DEFORM_FRAMES

    w_factor = 1.0
    h_factor = 1.0

    if start_frame <= frame_in_scene <= end_frame:
        easing = ease_in((end_frame - frame_in_scene) / (end_frame - start_frame))
        w_factor = 1.0 - 0.02 * easing
        h_factor = 1.0 + 0.21 * easing

    return (0.96 * w_factor, 0.945 * h_factor)


def draw_power_on_flash(ctx: cairo.Context, t: float, progress: float, scale: float):
    if progress >= END_OF_POWER_ON_FLASH_PROGRESS:
        return

    cx = TV_X_CENTER
    cy = TV_Y_CENTER

    if progress < 0.01:
        radius = 0
    elif progress < END_OF_POWER_ON_FLASH_PROGRESS - 0.00265:
        t_local = (progress - 0.01) / 0.015
        radius = 5 + 600 * ease_in(t_local)
        alpha = 0.3 + 0.7 * ease_in(t_local)

        r1 = cairo.RadialGradient(cx, cy, radius / 2, cx, cy, radius)
        r1.add_color_stop_rgba(0, 0.8, 0.8, 0.8, alpha)
        r1.add_color_stop_rgba(1, 0.8, 0.8, 0.8, 0)

        ctx.set_source(r1)
        ctx.arc(cx, cy, radius, 0, 2 * math.pi)
        ctx.fill()
    elif progress < END_OF_POWER_ON_FLASH_PROGRESS:
        end_frame = math.floor(TOTAL_FRAMES * END_OF_POWER_ON_FLASH_PROGRESS) + 1
        image_def_end = crt_deformation(end_frame)

        t_local = 1 - (END_OF_POWER_ON_FLASH_PROGRESS - progress) / 0.00265
        image_w = SCREEN_BASE_W * scale * image_def_end[0]
        image_h = SCREEN_BASE_H * scale * image_def_end[1] * 0.85 * (0.33 + 0.67 * t_local)

        image_x = TV_X_CENTER - image_w / 2
        image_y = TV_Y_CENTER - image_h / 2

        ctx.set_source_rgba(0.7, 0.7, 0.7, 0.9 - 0.6 * t_local)
        ctx.rectangle(image_x, image_y, image_w, image_h)
        ctx.fill()


def draw_channel_number(ctx: cairo.Context, frame_in_scene: int, scale: float):
    start_frame = math.floor(TOTAL_FRAMES * END_OF_POWER_ON_FLASH_PROGRESS) + 1
    end_frame = start_frame + CHANNEL_FRAME_DURATION

    if frame_in_scene < start_frame or frame_in_scene >= end_frame:
        return

    image_def = crt_deformation(frame_in_scene)
    image_def_end = crt_deformation(end_frame)

    w = TV_BASE_WIDTH * scale
    h = TV_BASE_HEIGHT * scale
    x = TV_X_CENTER - w / 2
    y = TV_Y_CENTER - h / 2

    image_w = SCREEN_BASE_W * scale * image_def[0]
    image_h = SCREEN_BASE_H * scale * image_def[1]
    image_x = x + (w - image_w) / 2
    image_y = y + (h - image_h) / 2

    screen_w = SCREEN_BASE_W * scale * image_def_end[0]
    screen_h = SCREEN_BASE_H * scale * image_def_end[1]
    screen_x = x + (w - screen_w) / 2
    screen_y = y + (h - screen_h) / 2

    x_margin = 95 * scale
    y_margin = 85 * scale

    channel_number_string = "0"

    ctx.save()
    ctx.rectangle(screen_x, screen_y, screen_w, screen_h)
    ctx.clip()

    ctx.select_font_face("DejaVu Sans Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(96 * scale)
    te = ctx.text_extents(channel_number_string)

    tx = image_x + image_w - x_margin - te.width
    ty = image_y + y_margin + te.height

    ctx.set_source_rgb(*CHANNEL_GREEN)
    ctx.move_to(tx, ty)
    ctx.show_text(channel_number_string)
    ctx.restore()


def draw_analog_pattern(ctx: cairo.Context, t: float, frame_in_scene: int, scale: float):
    if frame_in_scene < PATTERN_START:
        return

    image_def = crt_deformation(frame_in_scene)

    w = TV_BASE_WIDTH * scale
    h = TV_BASE_HEIGHT * scale
    x = TV_X_CENTER - w / 2
    y = TV_Y_CENTER - h / 2
    screen_w = SCREEN_BASE_W * scale * image_def[0]
    screen_h = SCREEN_BASE_H * scale * image_def[1]
    screen_x = x + (w - screen_w) / 2
    screen_y = y + (h - screen_h) / 2

    ctx.save()
    ctx.rectangle(screen_x, screen_y, screen_w + 1, screen_h + 1)
    ctx.clip()

    pixel_size = 4
    for px in range(0, math.ceil(screen_w), pixel_size):
        for py in range(0, math.ceil(screen_h), pixel_size):
            nx = screen_x + px
            ny = screen_y + py
            r, g, b = hsv_to_rgb(*hsv_pattern(t, nx, ny))
            alpha = 0.93 * (frame_in_scene - PATTERN_START) / (SIGNAL_START - PATTERN_START)
            ctx.set_source_rgba(r, g, b, alpha)
            ctx.rectangle(nx, ny, pixel_size, pixel_size)
            ctx.fill()

    ctx.restore()


def draw_analog_noise(ctx: cairo.Context, t: float, frame_in_scene: int, scale: float):
    after_flash = math.floor(TOTAL_FRAMES * END_OF_POWER_ON_FLASH_PROGRESS) + 1
    if (frame_in_scene < NOISE_START) \
            and not (after_flash + CRT_DEFORM_FRAMES + 20 <= frame_in_scene <= after_flash + CRT_DEFORM_FRAMES + 160):
        return

    image_def = crt_deformation(frame_in_scene)

    w = TV_BASE_WIDTH * scale
    h = TV_BASE_HEIGHT * scale
    x = TV_X_CENTER - w / 2
    y = TV_Y_CENTER - h / 2
    screen_w = SCREEN_BASE_W * scale * image_def[0]
    screen_h = SCREEN_BASE_H * scale * image_def[1]
    screen_x = x + (w - screen_w) / 2
    screen_y = y + (h - screen_h) / 2

    ctx.save()
    if frame_in_scene >= after_flash + CRT_DEFORM_FRAMES:
        ctx.rectangle(screen_x, screen_y, screen_w, screen_h)
        ctx.clip()
    else:
        image_def_end = crt_deformation(after_flash + CRT_DEFORM_FRAMES)
        screen_h_end = SCREEN_BASE_H * scale * image_def_end[1]
        screen_y_end = y + (h - screen_h_end) / 2
        ctx.rectangle(screen_x, screen_y_end, screen_w, screen_h_end)
        ctx.clip()

    pixel_height = math.floor(screen_h / TV_LINES)
    pixel_width = 7

    prev_line_colors: List[Tuple[RGB, RGB]] = [None] * math.ceil(int(screen_w) / pixel_width)
    prev_rgb = hsv_to_rgb(*hsv_noise())

    for py in range(0, int(screen_h), pixel_height):
        for px in range(0, int(screen_w), pixel_width):
            nx = screen_x + px
            ny = screen_y + py
            rgb = hsv_to_rgb(*hsv_noise())

            # У CRT-телевизоров нет пикселей по горизонтали.
            # По вертикали граница между строками тоже размыта.

            gradient = cairo.LinearGradient(nx, ny, nx + pixel_width, ny)
            gradient.add_color_stop_rgb(0.0, *prev_rgb)
            gradient.add_color_stop_rgb(1.0, *rgb)

            ctx.set_source(gradient)
            ctx.rectangle(nx, ny, pixel_width, pixel_height * 2)
            ctx.fill()

            if py > 0:
                blur_height = 0.2 * pixel_height
                blur_y = ny - blur_height
                alpha = 0.5

                top_colors = prev_line_colors[px // pixel_width]

                mixed_gradient = cairo.LinearGradient(nx, blur_y, nx + pixel_width, blur_y)
                mixed_gradient.add_color_stop_rgb(0.0, *mix_srgb(prev_rgb, top_colors[0], alpha))
                mixed_gradient.add_color_stop_rgb(1.0, *mix_srgb(rgb, top_colors[1], alpha))

                ctx.set_source(mixed_gradient)
                ctx.rectangle(nx, blur_y, pixel_width, blur_height)
                ctx.fill()

            prev_line_colors[px // pixel_width] = (prev_rgb, rgb)
            prev_rgb = rgb

    ctx.restore()


def draw_moire_pattern(ctx: cairo.Context, t: float, frame_in_scene: int, scale: float):
    if frame_in_scene < PATTERN_START:
        return

    image_def = crt_deformation(frame_in_scene)

    w = TV_BASE_WIDTH * scale
    h = TV_BASE_HEIGHT * scale
    x = TV_X_CENTER - w / 2
    y = TV_Y_CENTER - h / 2
    screen_w = SCREEN_BASE_W * scale * image_def[0]
    screen_h = SCREEN_BASE_H * scale * image_def[1]
    cx = x + w / 2
    cy = y + h / 2
    rx = screen_w / 2
    ry = screen_h / 2

    ctx.save()
    ctx.translate(cx, cy)

    alpha_factor = (frame_in_scene - PATTERN_START) / (SIGNAL_START - PATTERN_START)

    # Муар: пересечение двух сеток
    ctx.set_line_width(1.2)
    for i in range(-20, 21):
        offset = i * 12 + t * 8
        alpha = 0.3 + 0.2 * math.sin(t * 0.5 + i * 0.3)
        ctx.set_source_rgba(*SIGNAL_BLUE, alpha * alpha_factor)
        ctx.move_to(-rx, offset)
        ctx.line_to(rx, offset)
        ctx.stroke()

        ctx.move_to(offset, -ry)
        ctx.line_to(offset, ry)
        ctx.stroke()

    # Тор (wireframe)
    for r in [80, 120, 160]:
        for a in range(0, 360, 15):
            angle = math.radians(a + t * 20)
            x1 = (r + 40 * math.cos(angle * 3)) * math.cos(angle)
            y1 = (r + 40 * math.cos(angle * 3)) * math.sin(angle)
            x2 = (r + 40 * math.cos(angle * 3 + 0.1)) * math.cos(angle + 0.1)
            y2 = (r + 40 * math.cos(angle * 3 + 0.1)) * math.sin(angle + 0.1)
            ctx.set_source_rgba(*SIGNAL_BLUE, 0.5 * alpha_factor)
            ctx.move_to(x1, y1)
            ctx.line_to(x2, y2)
            ctx.stroke()

    ctx.restore()


def draw_title_signal(ctx: cairo.Context, t: float, frame_in_scene: int, scale: float):
    if frame_in_scene < TITLE_FRAME:
        return

    image_def = crt_deformation(frame_in_scene)

    ctx.save()
    w = TV_BASE_WIDTH * scale
    h = TV_BASE_HEIGHT * scale
    x = TV_X_CENTER - w / 2
    y = TV_Y_CENTER - h / 2
    screen_w = SCREEN_BASE_W * scale * image_def[0]
    screen_h = SCREEN_BASE_H * scale * image_def[1]

    title = "SIGNAL MEMORY"
    font_size = int(48 * scale)
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(font_size)
    te = ctx.text_extents(title)

    tx = x + w / 2 - te.width / 2
    ty = y + h - 100 * scale

    progress = (frame_in_scene - TITLE_FRAME) / 60.0
    if progress > 1.0:
        alpha = 1.0
    else:
        alpha = ease_in_out(progress)

    scan_y = ty - 200 * (1 - ease_out(progress)) + noise(0, t * 10, t) * 20

    ctx.set_source_rgba(*SIGNAL_BLUE, alpha * 0.9)
    ctx.move_to(tx, ty)
    ctx.text_path(title)
    ctx.fill()

    ctx.set_source_rgba(1, 1, 1, 0.6)
    ctx.rectangle(tx - 20, scan_y, screen_w, 4)
    ctx.fill()

    ctx.restore()


def render_scene1(total_frame: int, duration: int, frame_in_scene: int, render_size: Tuple[int, int], output_path: Path):
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, *render_size)
    ctx = cairo.Context(surface)
    t = frame_in_scene / 60.0
    progress = frame_in_scene / TOTAL_FRAMES

    clear(ctx, CRT_GLOW, render_size)

    zoom_factor = 1.0
    if frame_in_scene >= ZOOM_START:
        zoom_t = (frame_in_scene - ZOOM_START) / (TOTAL_FRAMES - ZOOM_START)
        zoom_factor = 1.0 + 0.15 * ease_in_out(zoom_t)

    draw_tv_body(ctx, zoom_factor)
    draw_screen_frame(ctx, zoom_factor)
    draw_power_on_flash(ctx, t, progress, zoom_factor)
    draw_analog_noise(ctx, t, frame_in_scene, zoom_factor)
    draw_analog_pattern(ctx, t, frame_in_scene, zoom_factor)
    draw_moire_pattern(ctx, t, frame_in_scene, zoom_factor)

    draw_channel_number(ctx, frame_in_scene, zoom_factor)
    draw_title_signal(ctx, t, frame_in_scene, zoom_factor)

    scan_alpha = 0.18 + noise(0, t * 8, t) * 0.05
    draw_scanlines(ctx, render_size, alpha=scan_alpha, line_height=2)

    surface.write_to_png(str(output_path))
    surface.finish()

