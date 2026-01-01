from dataclasses import dataclass
from typing import Optional, Tuple
import math, trimesh
import numpy as np

@dataclass
class Sphere:
    center: Tuple[float, float, float]
    radius: float
    color: Tuple[int, int, int]
    specular: int
    reflective: float

@dataclass
class Wall:
    center: Tuple[float, float, float]
    normal: Tuple[float, float, float]
    width: float
    height: float
    color: Tuple[int, int, int]
    specular: int
    reflective: float
    checkered: bool = False

@dataclass
class Triangle:
    vertex0: Tuple[float, float, float]
    vertex1: Tuple[float, float, float]
    vertex2: Tuple[float, float, float]
    color: Tuple[int, int, int]
    specular: int
    reflective: float

@dataclass
class Light:
    type: str
    intensity: float
    position: Optional[Tuple[float, float, float]] = None
    direction: Optional[Tuple[float, float, float]] = None

@dataclass
class Camera:
    position: Tuple[float, float, float]
    rotation: Tuple[
        Tuple[float, float, float],
        Tuple[float, float, float],
        Tuple[float, float, float],
    ]

@dataclass
class BVHNode:
    def __init__(self, triangles):
        self.triangles = triangles
        self.left = None
        self.right = None

        mins = [math.inf]*3
        maxs = [-math.inf]*3
        for triangle in triangles:
            for v in (triangle.vertex0, triangle.vertex1, triangle.vertex2):
                for i in range(3):
                    mins[i] = min(mins[i], v[i])
                    maxs[i] = max(maxs[i], v[i])

        self.bounds_min = tuple(mins)
        self.bounds_max = tuple(maxs)

        if len(triangles) > 8:
            self.split()
    
    def split(self):
        sizes = [
            self.bounds_max[i] - self.bounds_min[i]
            for i in range(3)
        ]
        axis = sizes.index(max(sizes))

        self.triangles.sort(
            key=lambda t: (
                t.vertex0[axis] +
                t.vertex1[axis] +
                t.vertex2[axis]
            ) / 3
        )

        mid = len(self.triangles) // 2
        self.left = BVHNode(self.triangles[:mid])
        self.right = BVHNode(self.triangles[mid:])
        self.triangles = None

def load_mesh(filename, color, specular, reflective, position=(0, 0, 0), scale=1.0):
    mesh = trimesh.load(filename, force='mesh')
    mesh.vertices -= mesh.centroid
    mesh.vertices *= scale
    rotation = np.array([
        [math.cos(-90), 0, math.sin(-90)],
        [0, 1, 0],
        [-math.sin(-90), 0, math.cos(-90)]
    ])
    mesh.vertices = mesh.vertices @ rotation
    mesh.vertices += np.array(position)
    triangles = []
    for face in mesh.faces:
        vertex0 = tuple(mesh.vertices[face[0]])
        vertex1 = tuple(mesh.vertices[face[1]])
        vertex2 = tuple(mesh.vertices[face[2]])
        triangles.append(
            Triangle(vertex0, vertex1, vertex2, color, specular, reflective)
        )
    return triangles

class Scene:
    def __init__(self):
        self.spheres = [
            #Sphere(center=(0, -1, 3), radius=1, color=(255, 0, 0), specular=500, reflective = 0.2),   # Red
            #Sphere(center=(-0.5, -2, 2.5), radius=0.5, color=(0, 0, 255), specular=500, reflective = 0.3),   # Blue
            #Sphere(center=(-2, -1.5, 4), radius=1, color=(0, 255, 0), specular=10, reflective = 0.4),  # Green

            Sphere(center=(3, 1.5, 4), radius=2, color=(255, 0, 0), specular=500, reflective = 0.7),
            Sphere(center=(-1.5, 0, 0), radius=0.5, color=(112, 8, 191), specular=500, reflective = 0.3),
        ]
        self.walls = [
            Wall(center=(0, -1.6, 3), normal=(0, 1, 0), width=8, height=8, 
                color=(255, 255, 255), specular=1000, reflective=0.1, checkered=True),
        ]

            #Wall(center=(-1.8, -1.6, 0), normal=(0, 1, 0), width=0.5, height=0.5, color=(255, 255, 255), specular=1000, reflective=0), #Bottom White
            #Wall(center=(1.5, 0.5, 0), normal=(-1, 0, 0), width=3, height=3, color=(0, 255, 0), specular=500, reflective=0), #Right Green
            #Wall(center=(-1.5, 0.5, 0), normal=(1, 0, 0), width=3, height=3, color=(255, 0, 0), specular=500, reflective=0), #Left Red
            #Wall(center=(0, 0.5, 1.5), normal=(0, 0, -1), width=3, height=3, color=(255, 255, 255), specular=500, reflective=0), #Behind White

        self.triangles = [
            #Triangle((1, -2.5, 2.75), (-1, -2.5, 4.75), (1, 0.5, 4.75), color=(255, 0, 0), specular=50, reflective=0.3),
            #Triangle((-1, -2.5, 4.75), (1, -2.5, 6.75), (1, 0.5, 4.75), color=(255, 0, 0), specular=50, reflective=0.3),
            #Triangle((1, -2.5, 6.75), (3, -2.5, 4.75), (1, 0.5, 4.75), color=(255, 0, 0), specular=50, reflective=0.3),
            #Triangle((3, -2.5, 4.75), (1, -2.5, 2.75), (1, 0.5, 4.75), color=(255, 0, 0), specular=50, reflective=0.3),

            Triangle((1.5, -2.5, -1), (-0.5, -2.5, 1), (1.5, 0.5, 1), color=(0, 0, 255), specular=50, reflective=0.3),
            Triangle((-0.5, -2.5, 1), (1.5, -2.5, 3), (1.5, 0.5, 1), color=(0, 0, 255), specular=50, reflective=0.3),
            Triangle((1.5, -2.5, 3), (3.5, -2.5, 1), (1.5, 0.5, 1), color=(0, 0, 255), specular=50, reflective=0.3),
            Triangle((3.5, -2.5, 1), (1.5, -2.5, -1), (1.5, 0.5, 1), color=(0, 0, 255), specular=50, reflective=0.3),
        ]
        self.triangles += load_mesh("chess_knight.glb", color=(255,255,255), specular=1000, reflective=0, position=(-2, -0.2, 3), scale=1.5)
        self.bvh = BVHNode(self.triangles)
        self.lights = [
            Light(type="ambient", intensity=0.1),
            Light(type="point", intensity=0.9, position=(0,5,-1)),
            #Light(type="directional", intensity=0.2, direction=(1,4,4))
        ]
        self.camera = Camera(
            position=(5, 4, -6),
            rotation=(
                (math.cos(-0.5), 0, math.sin(-0.5)),
                (0, math.cos(0.5), -math.sin(0.5)),
                (-math.sin(-0.5), 0, math.cos(-0.5)),
            ))

"""
Camera(
    position=(0,0.5,-4.5),
    rotation=(
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    ))

Camera(
    position=(4, 0, 1.5),
    rotation=(
    (math.cos(-45),  0,  math.sin(-45)),
    (0,             1,  0),
    (-math.sin(-45), 0,  math.cos(-45)),
    ))
"""