"""Estrutura de malha e matrizes da wiki: objeto → mundo → câmera."""
from dataclasses import dataclass
import numpy as np


@dataclass
class Mesh:
    name: str
    vertices: np.ndarray
    faces: np.ndarray
    color: np.ndarray

    @property
    def edges(self):
        pairs = np.concatenate([self.faces[:, [0, 1]], self.faces[:, [1, 2]],
                                self.faces[:, [2, 0]]])
        return np.unique(np.sort(pairs, axis=1), axis=0)

    @property
    def normals(self):
        triangles = self.vertices[self.faces]
        return unit(np.cross(triangles[:, 1] - triangles[:, 0],
                             triangles[:, 2] - triangles[:, 0]))


def unit(vectors):
    lengths = np.linalg.norm(vectors, axis=-1, keepdims=True)
    if np.any(lengths < 1e-12):
        raise ValueError("Vetor nulo: verifique a geometria ou a câmera.")
    return vectors / lengths


def model_matrix(scale=1., angles=(0, 0, 0), translation=(0, 0, 0)):
    """Vetores-coluna: M = T Rz Ry Rx S (graus; rotação na origem local)."""
    x, y, z = np.radians(angles)
    cx, cy, cz = np.cos([x, y, z])
    sx, sy, sz = np.sin([x, y, z])
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    matrix = np.eye(4)
    matrix[:3, :3] = rz @ ry @ rx * scale
    matrix[:3, 3] = translation
    return matrix


def transform(mesh, matrix):
    points = np.column_stack([mesh.vertices, np.ones(len(mesh.vertices))])
    return Mesh(mesh.name, (points @ matrix.T)[:, :3], mesh.faces, mesh.color)


def default_transforms():
    # Cinco posições separadas; z=0 é a base dos móveis e do vaso.
    positions = [(-3.5, -.8, 0), (1., -2., 0), (-1., 3.2, 0),
                 (4., 2.2, 0), (4.3, -2.7, .3)]
    scales = [1., 1., 1., 1.1, .9]
    angles = [(0, 0, 0), (0, 0, -15), (0, 0, 0), (0, 0, 0), (15, 0, -25)]
    return [dict(scale=s, angles=a, translation=p) for s, a, p in zip(scales, angles, positions)]


def world_scene(objects, transforms):
    scene = [transform(mesh, model_matrix(**params))
             for mesh, params in zip(objects, transforms)]
    for mesh in scene:
        if np.max(np.abs(mesh.vertices)) > 10 + 1e-9:
            raise ValueError(f"{mesh.name}: os vértices devem ficar em [-10, 10].")
    for i, a in enumerate(scene):
        for b in scene[i + 1:]:
            overlap = np.minimum(a.vertices.max(0), b.vertices.max(0)) - np.maximum(
                a.vertices.min(0), b.vertices.min(0))
            if np.all(overlap > 1e-9):
                raise ValueError(f"Separe {a.name} e {b.name}: suas caixas se sobrepõem.")
    return scene


def camera_matrix(eye, at, aux):
    """Wiki: n=unit(eye-at); u=unit(aux-proj_n(aux)); v=n×u."""
    eye, at, aux = np.asarray(eye), np.asarray(at), np.asarray(aux)
    n = unit(eye - at)
    u = unit(aux - np.dot(aux, n) * n)
    v = np.cross(n, u)
    basis = np.array([u, v, n])
    matrix = np.eye(4)
    matrix[:3, :3] = basis
    matrix[:3, 3] = -basis @ eye
    return matrix
