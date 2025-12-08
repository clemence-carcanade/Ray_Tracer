from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class Sphere:
    center: Tuple[float, float, float]
    radius: float
    color: Tuple[int, int, int]
    specular: int

@dataclass
class Light:
    type: str
    intensity: float
    position: Optional[Tuple[float, float, float]] = None
    direction: Optional[Tuple[float, float, float]] = None

class Scene:
    def __init__(self):
        self.spheres = [
            Sphere(center=(0, -1, 3), radius=1, color=(255, 0, 0), specular=500),   # Red
            Sphere(center=(2, 0, 4), radius=1, color=(0, 0, 255), specular=500),   # Blue
            Sphere(center=(-2, 0, 4), radius=1, color=(0, 255, 0), specular=10),  # Green
            Sphere(center=(0, -5001, 0), radius=5000, color=(255, 255, 0), specular=1000) #Yellow
        ]
        self.lights = [
            Light(type="ambient", intensity=0.2),
            Light(type="point", intensity=0.6, position=(2,1,0)),
            Light(type="directional", intensity=0.2, direction=(1,4,4))
        ]
