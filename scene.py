from dataclasses import dataclass
from typing import Optional, Tuple
import math

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

class Scene:
    def __init__(self):
        self.spheres = [
            Sphere(center=(0, -1, 3), radius=1, color=(255, 0, 0), specular=500, reflective = 0.2),   # Red
            Sphere(center=(2, 0, 4), radius=1, color=(0, 0, 255), specular=500, reflective = 0.3),   # Blue
            Sphere(center=(-2, 0, 4), radius=1, color=(0, 255, 0), specular=10, reflective = 0.4),  # Green
        ]
        self.walls = [
            Wall(center=(0, -3.5, 3.5), normal=(0, 1, 0), width=7, height=7, color=(255, 255, 255), specular=1000, reflective=0), #Bottom White
            Wall(center=(3.5, 0, 3.5), normal=(-1, 0, 0), width=7, height=7, color=(0, 255, 0), specular=500, reflective=0), #Right Green
            Wall(center=(-3.5, 0, 3.5), normal=(1, 0, 0), width=7, height=7, color=(255, 0, 0), specular=500, reflective=0), #Left Red
            Wall(center=(0, 0, 7), normal=(0, 0, -1), width=7, height=7, color=(255, 255, 255), specular=500, reflective=0), #Behind White
        ]
        self.lights = [
            Light(type="ambient", intensity=0.1),
            Light(type="point", intensity=0.9, position=(0,5,3.5)),
            #Light(type="directional", intensity=0.2, direction=(1,4,4))
        ]
        self.camera = Camera(
                        position=(0,0,-5),
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