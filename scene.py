from dataclasses import dataclass

@dataclass
class Sphere:
    center: tuple
    radius: float
    color: tuple


class Scene:
    def __init__(self):
        self.spheres = [
            Sphere(center=(0, -1, 3), radius=1, color=(255, 0, 0)),   # Red
            Sphere(center=(2, 0, 4), radius=1, color=(0, 0, 255)),   # Blue
            Sphere(center=(-2, 0, 4), radius=1, color=(0, 255, 0)),  # Green
        ]
