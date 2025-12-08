import math
from PIL import Image

from scene import Scene
from config import *

# Vector math operations
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))

# Implementation of pseudo-code
def CanvasToViewport(x, y):
    return (
        x * VIEWPORT_WIDTH / CANVAS_WIDTH,
        y * VIEWPORT_HEIGHT / CANVAS_HEIGHT,
        PROJECTION_PLANE_D
    )

def IntersectRaySphere(O, D, sphere):
    r = sphere.radius
    CO = subtract(O, sphere.center)

    a = dot(D, D)
    b = 2 * dot(CO, D)
    c = dot(CO, CO) - r * r

    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return math.inf, math.inf

    sqrt_disc = math.sqrt(discriminant)
    t1 = (-b + sqrt_disc) / (2 * a)
    t2 = (-b - sqrt_disc) / (2 * a)

    return t1, t2

def TraceRay(O, D, t_min, t_max, scene):
    closest_t = math.inf
    closest_sphere = None

    for sphere in scene.spheres:
        t1, t2 = IntersectRaySphere(O, D, sphere)

        if t_min <= t1 <= t_max and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere

        if t_min <= t2 <= t_max and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere

    if closest_sphere is None:
        return BACKGROUND_COLOR

    return closest_sphere.color

def main():
    print("Start Ray Tracing...")
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT))
    pixels = image.load()

    scene = Scene()
    O = (0, 0, 0)

    for x in range(-CANVAS_WIDTH // 2, CANVAS_WIDTH // 2):
        for y in range(-CANVAS_HEIGHT // 2, CANVAS_HEIGHT // 2):
            D = CanvasToViewport(x, y)
            color = TraceRay(O, D, 1, math.inf, scene)
            px = x + CANVAS_WIDTH // 2
            py = CANVAS_HEIGHT // 2 - y - 1
            pixels[px, py] = color

    image.save("output.png")
    print("Completed Rendering : output.png")


if __name__ == "__main__":
    main()