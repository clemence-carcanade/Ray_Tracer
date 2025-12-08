import math
from PIL import Image

from scene import Scene
from config import *

# Vector math operations
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def add(a, b):
    return tuple(x + y for x, y in zip(a, b))

def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))

def multiply(v, k):
    return tuple(x * k for x in v)

def length(v):
    return math.sqrt(dot(v, v))

def normalize(v):
    l = length(v)
    return tuple(x / l for x in v)

def negate(v):
    return tuple(-x for x in v)

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

def ComputeLighting(P, N, V, s, scene):
    intensity = 0.0

    for light in scene.lights:
        if light.type == "ambient":
            intensity += light.intensity
        else:
            if light.type == "point":
                L = subtract(light.position, P)
            else:
                L = light.direction

            n_dot_l = dot(N, L)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (length(N) * length(L))

            if s != -1:
                R = subtract(multiply(N, 2 * dot(N, L)), L)
                r_dot_v = dot(R, V)
                if r_dot_v > 0:
                    intensity += light.intensity * pow(r_dot_v / (length(R) * length(V)), s)

    return intensity

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

    P = add(O, multiply(D, closest_t))
    N = normalize(subtract(P, closest_sphere.center))
    lighting = ComputeLighting(P, N, negate(D), closest_sphere.specular, scene)
    r = int(closest_sphere.color[0] * lighting)
    g = int(closest_sphere.color[1] * lighting)
    b = int(closest_sphere.color[2] * lighting)
    return (r, g, b)

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

    image.save("output3.png")
    print("Completed Rendering : output3.png")

if __name__ == "__main__":
    main()