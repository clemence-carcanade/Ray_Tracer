import math, time
from PIL import Image
from multiprocessing import Pool, cpu_count

from scene import Scene, Sphere, Wall, Triangle, Camera
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

"""Loot At Function made by Claude.ia"""

"""Computes a camera rotation matrix so the camera at camera_pos looks at target.
camera_pos: camera position
target: point to look at
up: reference up vector (default Y)
returns: 3x3 rotation matrix (right, true_up, forward)"""
def look_at(camera_pos, target, up=(0, 1, 0)):
    forward = subtract(target, camera_pos)

    forward = (forward[0], 0.0, forward[2])
    forward = normalize(forward)

    right = normalize(cross(forward, up))
    true_up = cross(right, forward)

    return (right, true_up, forward)

"""Converts canvas pixel coordinates to a 3D direction on the viewport.
x: int canvas x coordinate
y: int canvas y coordinate
returns: direction vector"""
def CanvasToViewport(x, y):
    return (
        x * VIEWPORT_WIDTH / CANVAS_WIDTH,
        y * VIEWPORT_HEIGHT / CANVAS_HEIGHT,
        PROJECTION_PLANE_D
    )

"""Computes ray–sphere intersection using the quadratic equation.
O: ray origin
D: ray direction
sphere: Sphere object
returns: (t1, t2) intersection distances or (inf, inf) for no intersection"""
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

"""Computes ray intersection with a bounded plane and checks rectangle limits.
O: ray origin
D: ray direction
wall: Wall object
returns: t distance or inf for no intersection"""
def IntersectRayWall(O, D, wall):
    ndotd = dot(wall.normal, D)
    if abs(ndotd) < EPSILON:
        return math.inf
    t = dot(subtract(wall.center, O), wall.normal) / ndotd
    if t < 0: return math.inf
    P = add(O, multiply(D, t))

    """Extension Plane to Wall assited with Claude.ia"""
    
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

"""Computes ray–triangle intersection using the Möller–Trumbore algorithm.
O: ray origin
D: ray direction
tri: Triangle object
returns: t distance or inf for no intersection"""
def IntersectRayTriangle(O, D, tri):
    edge1 = subtract(tri.vertex1, tri.vertex0)
    edge2 = subtract(tri.vertex2, tri.vertex0)
    #P = V0 + u·(V1-V0) + v·(V2-V0) où u ≥ 0, v ≥ 0, et u+v ≤ 1
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

"""Computes lighting at point P using ambient, diffuse and specular components.
P: intersection point
N: surface normal at P
V: direction toward the camera
s: int specular exponent
t_max: float maximum shadow ray distance
scene: Scene object
returns: total light intensity (float)"""
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

"""Traces a ray recursively to compute the final pixel color.
O: ray origin
D: ray direction
t_min: float minimum intersection distance
t_max: float maximum intersection distance
depth: int recursion depth limit
scene: Scene object
returns: RGB color tuple"""
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
    
    obj_color = object.color
    
    if hasattr(object, 'checkered') and object.checkered:
        size = 1.0 
        
        if (int(math.floor(P[0] / size)) + int(math.floor(P[2] / size))) % 2 != 0:
            obj_color = (50, 50, 50)
        else:
            obj_color = (220, 220, 220)

    lighting = ComputeLighting(P, N, V, object.specular, t_max, scene)

    local_color = (
        int(obj_color[0] * lighting),
        int(obj_color[1] * lighting),
        int(obj_color[2] * lighting)
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

"""Finds the closest object intersected by the ray within bounds.
O: ray origin
D: ray direction
t_min: float minimum distance
t_max: float maximum distance
scene: Scene object
returns: closest (object, t)"""
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

    triangle, t = intersect_bvh(scene.bvh, O, D, t_min, t_max)
    if triangle and t < closest_t:
        closest_t = t
        closest_object = triangle

    return closest_object, closest_t

"""Computes the reflection direction of vector V around normal N.
V: incident direction
N: surface normal
returns: reflected direction"""
def ReflectRay(V, N):
    return subtract(
        multiply(N, 2 * dot(N, V)), V
    )

"""BVH Tree implementation assited with Claude.ia"""

"""Tests ray–AABB intersection using the slab method.
O: ray origin
D: ray direction
bounds_min: AABB minimum corner
bounds_max: AABB maximum corner
returns: bool"""
def intersect_aabb(O, D, bounds_min, bounds_max):
    tmin = -math.inf
    tmax = math.inf

    for i in range(3):  #x,y,z
        if abs(D[i]) < EPSILON:
            if O[i] < bounds_min[i] or O[i] > bounds_max[i]:
                return False
        else:
            invD = 1.0 / D[i]
            t0 = (bounds_min[i] - O[i]) * invD
            t1 = (bounds_max[i] - O[i]) * invD
            if t0 > t1:
                t0, t1 = t1, t0
            tmin = max(tmin, t0)
            tmax = min(tmax, t1)
            if tmax < tmin:
                return False

    return True

"""Traverses the BVH to find the closest triangle hit by the ray.
node: BVH node
O: ray origin
D: ray direction
t_min: float minimum distance
t_max: float maximum distance
returns: (Triangle or None, t)"""
def intersect_bvh(node, O, D, t_min, t_max):
    if node is None:
        return None, math.inf
    if not intersect_aabb(O, D, node.bounds_min, node.bounds_max):
        return None, math.inf

    closest_obj = None
    closest_t = t_max

    if node.triangles is not None:
        for tri in node.triangles:
            t = IntersectRayTriangle(O, D, tri)
            if t_min < t < closest_t:
                closest_t = t
                closest_obj = tri
        return closest_obj, closest_t

    obj_l, t_l = intersect_bvh(node.left, O, D, t_min, closest_t)
    obj_r, t_r = intersect_bvh(node.right, O, D, t_min, closest_t)

    if t_l < t_r:
        return obj_l, t_l
    return obj_r, t_r

"""Renders a single image row by casting one ray per pixel.
args: tuple (y, Camera)
returns: (y, list of RGB colors)"""
def RenderRow(args):
    y, camera = args
    scene = Scene("scene.txt", camera)
    O = camera.position
    row = []

    for x in range(-CANVAS_WIDTH // 2, CANVAS_WIDTH // 2):
        D = multiply_matrix_vector(camera.rotation, CanvasToViewport(x, y))
        row.append(TraceRay(O, D, 1, math.inf, 3, scene))

    return y, row

"""Renders a single animation frame with an orbiting camera.
frame_num: int current frame index
total_frames: int total number of frames
returns: PIL Image"""
def render_frame(frame_num, total_frames):
    frame_time = frame_num / total_frames
    print(f"Rendering frame {frame_num + 1}/{total_frames}...")

    center = (0, 0, 3)
    radius = 10
    height = 2

    angle = 2 * math.pi * frame_time

    cam_pos = (
        center[0] + radius * math.cos(angle),
        height,
        center[2] + radius * math.sin(angle)
    )

    cam_rot = look_at(cam_pos, center)
    camera = Camera(position=cam_pos, rotation=cam_rot)

    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT))
    pixels = image.load()

    rows_y = range(-CANVAS_HEIGHT // 2, CANVAS_HEIGHT // 2)
    args = [(y, camera) for y in rows_y]

    with Pool(cpu_count()) as pool:
        for y, row in pool.imap_unordered(RenderRow, args):
            py = CANVAS_HEIGHT // 2 - y - 1
            for px, color in enumerate(row):
                pixels[px, py] = color

    return image

"""Program entry point.
renders the output"""
def main():
    print("Start Ray Tracing Animation...")
    start_time = time.time()
    
    total_frames = 60 #60 fps
    frames = []
    
    for frame_num in range(total_frames):
        frame = render_frame(frame_num, total_frames)
        frames.append(frame)
    
    print("Saving GIF...")
    frames[0].save(
        "output/animation-test.gif",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )
    
    print("Completed Animation: output/animation-test.gif")
    end_time = int(time.time() - start_time)
    minutes = end_time // 60
    seconds = end_time % 60
    print(f"Total render time: {minutes:02d}:{seconds:02d}")

if __name__ == "__main__":
    main()