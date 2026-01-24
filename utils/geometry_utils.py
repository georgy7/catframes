from typing import Callable, List, Tuple
import math


FPoint = Tuple[float, float]
VertexShader = Callable[[List[FPoint]], List[FPoint]]
Segment = Tuple[FPoint, FPoint]


def sum_points(a: FPoint, b: FPoint) -> FPoint:
    return (a[0]+b[0], a[1]+b[1])


def construct_angle_diff(angle: float, distance: float) -> FPoint:
    return (
        math.cos(angle)*distance,
        -math.sin(angle)*distance
    )


def construct_angle(center: FPoint, angle: float, distance: float) -> FPoint:
    """Returns the coordinates of a point obtained by rotating
    a horizontal segment counterclockwise in radians.
    """
    diff: FPoint = construct_angle_diff(angle, distance)
    return (
        center[0] + diff[0],
        center[1] + diff[1]
    )


def get_distance(a: FPoint, b: FPoint) -> float:
    return math.sqrt(
        math.pow(a[0]-b[0], 2) +
        math.pow(a[1]-b[1], 2)
    )


def get_angle(center: FPoint, rotating: FPoint) -> float:
    xdelta: float = rotating[0] - center[0]
    angle: float = math.acos(xdelta / get_distance(center, rotating))
    return angle if rotating[1] <= center[1] else math.tau-angle


def get_center(vertices: List[FPoint]) -> FPoint:
    cx: float = sum(x[0] for x in vertices) / len(vertices)
    cy: float = sum(x[1] for x in vertices) / len(vertices)
    return (cx, cy)


def get_perpendicular_angle(angle: float, flip: bool) -> float:
    return angle-math.pi/2 if flip else angle+math.pi/2


def construct_perpendicular(corner: FPoint, angle: float, distance: float, flip: bool) -> FPoint:
    angle90: float = get_perpendicular_angle(angle, flip)
    return construct_angle(corner, angle90, distance)


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


def make_shift_shader(shift: FPoint) -> VertexShader:
    def shift_shader(vertices: List[FPoint]) -> List[FPoint]:
        x: List[float] = [(v[0] + shift[0]) for v in vertices]
        y: List[float] = [(v[1] + shift[1]) for v in vertices]
        return list(zip(x, y))
    return shift_shader

