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

def load_mesh(filename, color, specular, reflective):
    mesh = trimesh.load(filename, force='mesh')
    mesh.vertices -= mesh.centroid
    rotation = np.array([
        [math.cos(-90), 0, math.sin(-90)],
        [0, 1, 0],
        [-math.sin(-90), 0, math.cos(-90)]
    ])
    mesh.vertices = mesh.vertices @ rotation
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
        ]
        self.walls = [
            Wall(center=(0, -1, 0), normal=(0, 1, 0), width=3, height=3, color=(255, 255, 255), specular=1000, reflective=0), #Bottom White
            Wall(center=(1.5, 0.5, 0), normal=(-1, 0, 0), width=3, height=3, color=(0, 255, 0), specular=500, reflective=0), #Right Green
            Wall(center=(-1.5, 0.5, 0), normal=(1, 0, 0), width=3, height=3, color=(255, 0, 0), specular=500, reflective=0), #Left Red
            Wall(center=(0, 0.5, 1.5), normal=(0, 0, -1), width=3, height=3, color=(255, 255, 255), specular=500, reflective=0), #Behind White
        ]
        self.triangles = [
            #Triangle((1, -2.5, 2.75), (-1, -2.5, 4.75), (1, 0.5, 4.75), color=(255, 0, 0), specular=50, reflective=0.3),
            #Triangle((-1, -2.5, 4.75), (1, -2.5, 6.75), (1, 0.5, 4.75), color=(255, 0, 0), specular=50, reflective=0.3),
            #Triangle((1, -2.5, 6.75), (3, -2.5, 4.75), (1, 0.5, 4.75), color=(255, 0, 0), specular=50, reflective=0.3),
            #Triangle((3, -2.5, 4.75), (1, -2.5, 2.75), (1, 0.5, 4.75), color=(255, 0, 0), specular=50, reflective=0.3),
        ]
        self.triangles += load_mesh("chess_knight.glb", color=(0,148,251), specular=1000, reflective=0)
        self.lights = [
            Light(type="ambient", intensity=0.1),
            Light(type="point", intensity=0.9, position=(0,5,-1)),
            #Light(type="directional", intensity=0.2, direction=(1,4,4))
        ]
        self.camera = Camera(
                        position=(0,0.5,-4.5),
                        rotation=(
                            (1, 0, 0),
                            (0, 1, 0),
                            (0, 0, 1),
                        ))

"""
Camera(
    position=(4, 0, 1.5),
    rotation=(
    (math.cos(-45),  0,  math.sin(-45)),
    (0,             1,  0),
    (-math.sin(-45), 0,  math.cos(-45)),
    ))
"""