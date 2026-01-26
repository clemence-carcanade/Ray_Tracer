from dataclasses import dataclass
from typing import Optional, Tuple
import math, trimesh
import numpy as np
import re

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

"""Scene parsing made by Claude.ia"""

def parse_tuple(s):
    s = s.strip('()')
    values = [float(x.strip()) for x in s.split(',')]
    return tuple(values)

def parse_tuple_of_tuples(s):
    s = s.strip('()')
    tuples = re.findall(r'\([^)]+\)', s)
    return tuple(parse_tuple(t) for t in tuples)

def parse_line(line):
    """Parse une ligne du fichier de scène"""
    parts = line.split(maxsplit=1)
    if len(parts) < 2:
        return None
    
    obj_type = parts[0]
    params_str = parts[1]
    
    params = {}
    pattern = r'(\w+)=((?:\([^)]*(?:\([^)]*\)[^)]*)*\)|[^,\s]+))'
    matches = re.findall(pattern, params_str)
    
    for key, value in matches:
        if value.startswith('(('):
            params[key] = parse_tuple_of_tuples(value)
        elif value.startswith('('):
            tuple_val = parse_tuple(value)
            if key == 'color':
                params[key] = tuple(int(x) for x in tuple_val)
            else:
                params[key] = tuple_val
        elif value.lower() in ('true', 'false'):
            params[key] = value.lower() == 'true'
        elif value.startswith('"') or value.startswith("'"):
            params[key] = value.strip('"\'')
        elif '.' in value:
            params[key] = float(value)
        else:
            params[key] = int(value)
    
    return obj_type, params

class Scene:
    def __init__(self, scene_file=None, camera=None):
        self.spheres = []
        self.walls = []
        self.triangles = []
        self.lights = []
        self.camera = camera
        
        if scene_file:
            self.load_from_file(scene_file)
        
        if self.triangles:
            self.bvh = BVHNode(self.triangles)
        else:
            self.bvh = None
    
    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                result = parse_line(line)
                if not result:
                    continue
                
                obj_type, params = result
                
                if obj_type == 'CAMERA':
                    if self.camera is None:
                        self.camera = Camera(**params)
                
                elif obj_type == 'SPHERE':
                    self.spheres.append(Sphere(**params))
                
                elif obj_type == 'WALL':
                    self.walls.append(Wall(**params))
                
                elif obj_type == 'TRIANGLE':
                    self.triangles.append(Triangle(**params))
                
                elif obj_type == 'MESH':
                    mesh_triangles = load_mesh(
                        filename=params['file'],
                        color=params['color'],
                        specular=params['specular'],
                        reflective=params['reflective'],
                        position=params.get('position', (0, 0, 0)),
                        scale=params.get('scale', 1.0)
                    )
                    self.triangles.extend(mesh_triangles)
                
                elif obj_type == 'LIGHT':
                    self.lights.append(Light(**params))  

"""
Camera(
    position=(5, 4, -6),
    rotation=(
        (math.cos(-0.5), 0, math.sin(-0.5)),
        (0, math.cos(0.5), -math.sin(0.5)),
        (-math.sin(-0.5), 0, math.cos(-0.5)),
    ))

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