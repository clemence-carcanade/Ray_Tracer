import math
from PIL import Image

from scene import Scene, Sphere, Wall, Triangle
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

def multiply_matrix_vector(M, v):
    return (dot(M[0], v), dot(M[1], v), dot(M[2], v))

def cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    )

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

def IntersectRayWall(O, D, wall):
    norm = dot(wall.normal, D)
    if abs(norm) < EPSILON:
        return math.inf
    t = dot(subtract(wall.center, O), wall.normal) / norm
    if t < 0: return math.inf
    P = add(O, multiply(D, t))
    
    if abs(wall.normal[0]) < EPSILON and abs(wall.normal[1]) < EPSILON:
        tangent = (0, 1, 0)
    else:
        tangent = (0, 0, 1)
    
    axis1 = normalize(cross(wall.normal, tangent))
    axis2 = cross(axis1, wall.normal)
    
    diff = subtract(P, wall.center)
    u = dot(diff, axis1)
    v = dot(diff, axis2)
    
    if abs(u) > wall.width/2 or abs(v) > wall.height/2:
        return math.inf
    
    return t

def IntersectRayTriangle(O, D, tri):
    edge1 = subtract(tri.vertex1, tri.vertex0)
    edge2 = subtract(tri.vertex2, tri.vertex0)

    h = cross(D, edge2)
    a = dot(edge1, h)

    if abs(a) < EPSILON:
        return math.inf

    f = 1.0 / a
    s = subtract(O, tri.vertex0)
    u = f * dot(s, h)
    if u < 0.0 or u > 1.0:
        return math.inf

    q = cross(s, edge1)
    v = f * dot(D, q)
    if v < 0.0 or u + v > 1.0:
        return math.inf

    t = f * dot(edge2, q)
    return t if t > EPSILON else math.inf

def ComputeLighting(P, N, V, s, t_max, scene):
    intensity = 0.0

    for light in scene.lights:
        if light.type == "ambient":
            intensity += light.intensity
        else:
            if light.type == "point":
                L = subtract(light.position, P)
            else:
                L = light.direction

            shadow_object, shadow_t = ClosestIntersection(P, L, 0.001, t_max, scene)
            if shadow_object != None:
                continue

            n_dot_l = dot(N, L)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (length(N) * length(L))

            if s != -1:
                R = subtract(multiply(N, 2 * dot(N, L)), L)
                r_dot_v = dot(R, V)
                if r_dot_v > 0:
                    intensity += light.intensity * pow(r_dot_v / (length(R) * length(V)), s)

    return intensity

def TraceRay(O, D, t_min, t_max, depth, scene):
    object, t = ClosestIntersection(O, D, t_min, t_max, scene)
    if object is None:
        return BACKGROUND_COLOR

    P = add(O, multiply(D, t))
    V = negate(D)
    if isinstance(object, Sphere):
        N = normalize(subtract(P, object.center))
    elif isinstance(object, Wall):
        N = object.normal
    elif isinstance(object, Triangle):
        N = normalize(cross(subtract(object.vertex1, object.vertex0),subtract(object.vertex2, object.vertex0)))
        if dot(N, V) < 0 : N = negate(N)
    else:
        raise ValueError("Unkown Object")

    lighting = ComputeLighting(P, N, V, object.specular, t_max, scene)

    local_color = (
        int(object.color[0] * lighting),
        int(object.color[1] * lighting),
        int(object.color[2] * lighting)
    )

    r = object.reflective

    if depth <= 0 or r <= 0:
        return local_color

    R = ReflectRay(V, N)
    reflected_color = TraceRay(P, R, 0.001, math.inf, depth - 1, scene)

    final_color = (
        int(local_color[0] * (1 - r) + reflected_color[0] * r),
        int(local_color[1] * (1 - r) + reflected_color[1] * r),
        int(local_color[2] * (1 - r) + reflected_color[2] * r)
    )

    return final_color

def ClosestIntersection(O, D, t_min, t_max, scene):
    closest_t = math.inf
    closest_object = None

    for sphere in scene.spheres:
        t1, t2 = IntersectRaySphere(O, D, sphere)

        if t_min < t1 < t_max and t1 < closest_t:
            closest_t = t1
            closest_object = sphere

        if t_min < t2 < t_max and t2 < closest_t:
            closest_t = t2
            closest_object = sphere
    
    for wall in scene.walls:
        t = IntersectRayWall(O, D, wall)
        if t_min < t < t_max and t < closest_t:
            closest_t = t
            closest_object = wall

    for triangle in scene.triangles:
        t = IntersectRayTriangle(O, D, triangle)
        if t_min < t < t_max and t < closest_t:
            closest_t = t
            closest_object = triangle

    return closest_object, closest_t

def ReflectRay(V, N):
    return subtract(
        multiply(N, 2 * dot(N, V)), V
    )

def main():
    print("Start Ray Tracing...")
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT))
    pixels = image.load()

    scene = Scene()
    O = scene.camera.position
    recursion_depth = 3

    for x in range(-CANVAS_WIDTH // 2, CANVAS_WIDTH // 2):
        for y in range(-CANVAS_HEIGHT // 2, CANVAS_HEIGHT // 2):
            D = multiply_matrix_vector(scene.camera.rotation, CanvasToViewport(x, y))
            color = TraceRay(O, D, 1, math.inf, recursion_depth, scene)
            px = x + CANVAS_WIDTH // 2
            py = CANVAS_HEIGHT // 2 - y - 1
            pixels[px, py] = color

    image.save("output/output.png")
    print("Completed Rendering : output.png")

if __name__ == "__main__":
    main()