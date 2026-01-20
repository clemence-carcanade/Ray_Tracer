# Python Ray Tracer

## Introduction

This academic project is a ray tracer implemented in Python. Each feature was added progressively to understand both the algorithmic and mathematical aspects of ray tracing. <br>The goal is to understand how a realistic 3D image can be generated solely from geometric calculations.

### Project Architecture

The project is structured around three main files:

- **config.py**: Configuration parameters (resolution, viewport, numerical epsilon)
- **scene.py**: Definition of objects and the 3D scene (geometric objects, lights, camera, and BVH optimization)
- **ray_tracer.py**: Rendering engine and ray tracing algorithms (vector calculations, intersections, lighting, reflections, and final rendering)

---

### Libraries Used

| Library        | Purpose                                  |
|----------------|------------------------------------------|
| dataclass      | Automatically generates `__init__`       |
| typing         | Type annotations for code clarity        |
| math           | Mathematical functions (sqrt, cos, sin, inf) |
| trimesh        | Loading and manipulating 3D meshes       |
| numpy          | Matrix operations                        |
| PIL (Pillow)   | Image creation and saving                |
| multiprocessing| Rendering parallelization across all CPU cores |
| time           | Rendering time measurement               |

### Vector Representation

Tuples are native Python structures optimized in C, offering better performance for operations repeated millions of times (a ray tracer casts rays for each pixel). That's why we used tuples `(x, y, z)` rather than a `Vector3` class. We implemented the following vector operations:
- Vector addition and subtraction
- Product between a vector and a scalar
- Dot product and cross product
- Vector norm calculation
- Vector normalization
- Vector negation
- Matrix-vector product

## 1. Configuration (config.py)

The **canvas** represents the final image in pixels. These dimensions define the output resolution.
The **viewport** is a virtual rectangle in 3D space through which the camera "sees" the scene. `PROJECTION_PLANE_D` is the distance between the camera and the projection plane.

**Mathematical relationship**: To convert a canvas coordinate (x, y) to a viewport coordinate:
```
Vx = x × (VIEWPORT_WIDTH / CANVAS_WIDTH)
Vy = y × (VIEWPORT_HEIGHT / CANVAS_HEIGHT)
```

## 2. Scene Description (scene.py)

### Sphere

A sphere is defined by its center `C` and radius `r`.<br>
**Implicit sphere equation**:
```
|P - C|² = r²
```
where P is a point on the sphere, C the center, r the radius.

- `specular`: Light reflectivity for mimicking materials (shininess)
- `reflective`: Environment reflectivity (mirror)

### Wall

A wall is defined by a point `C` and a normal `N`.<br>
**Implicit plane equation**:
```
N · (P - C) = 0
```
where N is the normal, P a point on the plane, C a reference point.
The wall is a bounded rectangular plane defined by its width and height. A checkerboard pattern can be applied.

### Triangle

Triangles are the basic primitives for representing complex 3D meshes. Three non-collinear vertices define a unique plane.

### Lights

Three types of lights are implemented:
- **ambient**: Uniform lighting in all directions
- **point**: Point source (like a light bulb)
- **directional**: Parallel rays (like the sun)

### BVH (Bounding Volume Hierarchy)

Testing intersection with each triangle is costly O(n). The BVH organizes triangles hierarchically to reduce tests to O(log n).

A BVH is a binary tree used to accelerate intersection tests with triangles.
A BVH node represents a bounding box containing a subset of triangles. Each node stores:

- bounds_min: the minimum on each axis (x, y, z) among all vertices of contained triangles
- bounds_max: the maximum on each axis (x, y, z) among all vertices of contained triangles
- triangles: the list of triangles if it's a leaf node
- left and right: child nodes if it's an internal node

To construct the bounding box of a node, we iterate through all triangles and all their vertices v (a vertex is a tuple (x, y, z)):
```python
for triangle in triangles:
    for v in (triangle.vertex0, triangle.vertex1, triangle.vertex2):
        for i in range(3):  # i = 0 -> x, 1 -> y, 2 -> z
            mins[i] = min(mins[i], v[i])
            maxs[i] = max(maxs[i], v[i])
```
Here, v is a triangle vertex, mins[i] and maxs[i] are the min/max coordinates on each axis to construct the AABB.

If a node contains more than 8 triangles, we subdivide it to create two smaller child nodes. The process is:
- Choice of the longest axis: we calculate the box size on x, y, and z, then choose the axis where the box is most extended to maximize spatial separation.
- Sorting triangles by their centroid on this axis: the triangle centroid is (v0 + v1 + v2)/3. This allows placing triangles coherently along the chosen axis.
- Division into two balanced subsets: we cut the sorted list in the middle to create the two child nodes.

Each leaf contains the triangles and their bounding box. The ray first tests the root, then only descends into branches where intersection with the box is possible, drastically reducing the number of tests.

### Loading 3D Meshes

The engine can load 3D files in GLB, STL, or OBJ format using the trimesh library.
- The mesh is first recentered so its center is at the origin (0,0,0).
- Then, transformations are applied: scaling, rotation, and translation to position it correctly in the scene.
- Each face of the mesh is converted into a Triangle object used for ray tracing.

---

## 3. Ray Tracing Algorithm (ray_tracer.py)

### Parallelized Line-by-Line Rendering

The image rendering is performed line by line. For each pixel of a line, the coordinate (x, y) is converted into a direction in the viewport, this direction is then transformed by the camera's rotation matrix, then a ray is traced in the scene to calculate the final pixel color.

Rendering is parallelized using the `multiprocessing` module. The `cpu_count()` function automatically detects the number of available cores on the machine, and a `Pool` of worker processes is created accordingly. Each worker independently calculates one or more image lines.

The `imap_unordered` method distributes the lines to render among the processes and retrieves results as soon as they are ready, without imposing order, which maximizes CPU utilization. Each process recreates its own `Scene(camera)` instance, which is necessary because processes don't share memory.

On a multi-core machine (for example 8 cores), this approach provides a performance gain close to a factor of 8. The main drawback is higher memory consumption, as each process has its own copy of the scene.

---

## User Guide

Before running the script, you need to create a virtual environment.

In VS Code:
1. Open the Command Palette (`Ctrl + Shift + P`)
2. Select **Python: Select Interpreter**
3. Choose **Create Virtual Environment**
4. Select **Venv**
5. Choose a Python version
6. Check `requirements.txt`

Once the virtual environment is created, run the ray tracer from the project root:

```bash
python ray_tracer.py
```

## About

This project is a Python implementation of a ray tracer based on the book *Computer Graphics from Scratch* by Gabriel Gambetta.  
More details can be found here: https://gabrielgambetta.com/computer-graphics-from-scratch/