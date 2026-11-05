"""Verificações matemáticas e de rasterização: python -m unittest -v."""
import unittest
from dataclasses import replace
from collections import Counter
from fractions import Fraction
from math import ceil
import numpy as np
from geometry import (default_transforms, world_scene, camera_matrix,
                      model_matrix, transform)
from models import make_objects, bezier, prism
from renderer import (Settings, clip_polygon, render, scanline, line_samples, rasterize_line,
                      vertex_colors, barycentric)


class GeometryTests(unittest.TestCase):
    def test_closed_oriented_meshes(self):
        # As peças dos móveis são malhas fechadas separadas; os aros têm genus 1.
        components = [9, 12, 9, 1, 7]
        holes = [0, 0, 0, 0, 2]
        for mesh, count, genus in zip(make_objects(), components, holes):
            with self.subTest(mesh=mesh.name):
                directed = Counter((int(a), int(b)) for face in mesh.faces
                                   for a, b in zip(face, np.roll(face, -1)))
                self.assertTrue(all(n == 1 and directed[b, a] == 1
                                    for (a, b), n in directed.items()))
                self.assertEqual(len(mesh.vertices)-len(mesh.edges)+len(mesh.faces),
                                 2 * (count - genus))
                np.testing.assert_allclose(np.linalg.norm(mesh.normals, axis=1), 1)
                # Verifica também o volume de cada peça, não só a soma do objeto.
                neighbors = {i: set() for i in range(len(mesh.vertices))}
                for a, b in mesh.edges:
                    neighbors[a].add(b)
                    neighbors[b].add(a)
                unseen = set(neighbors)
                found = 0
                while unseen:
                    pending, component = [next(iter(unseen))], set()
                    while pending:
                        vertex = pending.pop()
                        if vertex not in component:
                            component.add(vertex)
                            pending.extend(neighbors[vertex] - component)
                    unseen -= component
                    found += 1
                    faces = mesh.faces[np.isin(mesh.faces[:, 0], list(component))]
                    triangles = mesh.vertices[faces]
                    volume = np.sum(triangles[:, 0] * np.cross(triangles[:, 1], triangles[:, 2])) / 6
                    self.assertGreater(volume, 0)
                self.assertEqual(found, count)

    def test_inner_and_outer_normals(self):
        vase = make_objects()[3]
        centers = vase.vertices[vase.faces].mean(axis=1)
        radial = np.sum(centers[:, :2] * vase.normals[:, :2], axis=1)
        self.assertTrue(np.any(radial > .1))
        self.assertTrue(np.any(radial < -.1))

    def test_bezier_endpoints(self):
        control = np.array([[0, 0], [1, 2], [3, 2], [4, 0]])
        curve = bezier(control, 9)
        np.testing.assert_allclose(curve[[0, -1]], control[[0, -1]])
        np.testing.assert_allclose(curve[4], [2, 1.5])

    def test_prism_normals_point_outward(self):
        mesh = prism([(-1, -1), (1, -1), (1, 1), (-1, 1)], -1, 1)
        centers = mesh.vertices[mesh.faces].mean(axis=1)
        self.assertTrue(np.all(np.sum(centers * mesh.normals, axis=1) > 0))

    def test_default_scene_bounds(self):
        scene = world_scene(make_objects(), default_transforms())
        self.assertLessEqual(max(np.abs(m.vertices).max() for m in scene), 10)

    def test_invalid_scene_rejected(self):
        params = default_transforms()
        params[0] = dict(scale=1, angles=(0, 0, 0), translation=(11, 0, 0))
        with self.assertRaises(ValueError):
            world_scene(make_objects(), params)
        params[0]['translation'] = params[1]['translation']
        with self.assertRaises(ValueError):
            world_scene(make_objects(), params)

    def test_transform_order(self):
        matrix = model_matrix(2, (0, 0, 90), (3, 4, 5))
        np.testing.assert_allclose(matrix @ [1, 0, 0, 1], [3, 6, 5, 1], atol=1e-12)

    def test_camera_basis(self):
        s = Settings()
        matrix = camera_matrix(s.eye, s.at, s.aux)
        basis = matrix[:3, :3]
        np.testing.assert_allclose(basis @ basis.T, np.eye(3), atol=1e-12)
        np.testing.assert_allclose(matrix @ [*s.eye, 1], [0, 0, 0, 1], atol=1e-12)
        self.assertLess((matrix @ [*s.at, 1])[2], 0)
        self.assertAlmostEqual(np.linalg.det(basis), 1)

    def test_degenerate_camera_rejected(self):
        for eye, at, aux in [((0, 0, 0), (0, 0, 0), (1, 0, 0)),
                             ((0, 0, 1), (0, 0, 0), (0, 0, 2))]:
            with self.assertRaises(ValueError):
                camera_matrix(eye, at, aux)


class RasterTests(unittest.TestCase):
    def test_clipping_all_six_planes(self):
        planes = np.array([(1, 0, 0, 1), (-1, 0, 0, 1), (0, 1, 0, 1),
                           (0, -1, 0, 1), (0, 0, 1, 0), (0, 0, -1, 1)])
        for point in [(3, 0, .5, 1), (-3, 0, .5, 1), (0, 3, .5, 1),
                      (0, -3, .5, 1), (0, 0, -2, 1), (0, 0, 3, 1)]:
            polygon = np.array([[*point, 1, 0, 0], [-.3, -.3, .5, 1, 0, 1, 0],
                                [.3, .3, .5, 1, 0, 0, 1]], dtype=float)
            result = clip_polygon(polygon)
            self.assertGreaterEqual(len(result), 3)
            self.assertTrue(np.all(result[:, :4] @ planes.T >= -1e-12))
            np.testing.assert_allclose(result[:, 4:].sum(axis=1), 1)

    def test_wholly_behind_rejected(self):
        polygon = np.array([[0, 0, -2, -1, 1, 0, 0], [1, 0, -2, -1, 1, 0, 0],
                            [0, 1, -2, -1, 1, 0, 0]], dtype=float)
        self.assertEqual(len(clip_polygon(polygon)), 0)

    @staticmethod
    def triangle(depth=.5, color=(1, 0, 0)):
        return np.array([[0, 0, depth, 1, *color], [8, 0, depth, 1, *color],
                         [0, 8, depth, 1, *color]], dtype=float)

    def test_scanline_square_has_no_cracks(self):
        image, depth = np.zeros((8, 8, 3)), np.full((8, 8), np.inf)
        first = self.triangle()
        second = first.copy()
        second[:, :2] = [[8, 0], [8, 8], [0, 8]]
        scanline(image, depth, first)
        scanline(image, depth, second)
        self.assertTrue(np.isfinite(depth).all())
        np.testing.assert_allclose(image, np.tile([1, 0, 0], (8, 8, 1)))

    def test_zbuffer_independent_of_order(self):
        near, far = self.triangle(.2, (1, 0, 0)), self.triangle(.8, (0, 1, 0))
        images = []
        for triangles in [(near, far), (far, near)]:
            image, depth = np.zeros((8, 8, 3)), np.full((8, 8), np.inf)
            for triangle in triangles:
                scanline(image, depth, triangle)
            images.append(image)
        np.testing.assert_array_equal(*images)
        np.testing.assert_allclose(images[0][1, 1], [1, 0, 0])

    def test_barycentric_colors(self):
        triangle = self.triangle()
        triangle[:, 4:] = np.eye(3)
        image, depth = np.zeros((8, 8, 3)), np.full((8, 8), np.inf)
        scanline(image, depth, triangle)
        expected = barycentric(np.array([[1.5, 1.5]]), triangle)[0]
        np.testing.assert_allclose(image[1, 1], expected)
        triangle[:, 3] = [1, 2, 4]
        scanline(image, depth, triangle)
        corrected = expected / triangle[:, 3]
        np.testing.assert_allclose(image[1, 1], corrected/corrected.sum())

    def test_line_horizontal_vertical_diagonal(self):
        for endpoint in [(7, 0), (0, 7), (7, 7), (0, 0)]:
            for start, end in [((0, 0), endpoint), (endpoint, (0, 0))]:
                triangle = self.triangle()
                triangle[:2, :2] = [start, end]
                image, depth = np.zeros((8, 8, 3)), np.full((8, 8), np.inf)
                with np.errstate(divide='raise', invalid='raise'):
                    rasterize_line(image, depth, triangle, 0, 1)
                self.assertEqual(np.isfinite(depth).sum(), 1 if start == end else 8)
                self.assertTrue(np.isfinite(depth[start[1], start[0]]))
                self.assertTrue(np.isfinite(depth[end[1], end[0]]))

    def test_line_all_octants(self):
        for dx, dy in [(6, 2), (6, -2), (-6, 2), (-6, -2),
                       (2, 6), (2, -6), (-2, 6), (-2, -6)]:
            a, b = (10, 10), (10 + dx, 10 + dy)
            # Referência com frações exatas, independente dos cálculos float da reta.
            expected = {(ceil(10 + Fraction(i * dx, 6)),
                         ceil(10 + Fraction(i * dy, 6))) for i in range(7)}
            for start, end in [(a, b), (b, a)]:
                with self.subTest(start=start, end=end):
                    samples = line_samples(start, end)
                    pixels = {tuple(p) for p in np.ceil(samples[:, :2]).astype(int)}
                    self.assertEqual(pixels, expected)
                    np.testing.assert_allclose(samples[[0, -1], 2], [0, 1])

    def test_line_fractional_endpoints(self):
        cases = [((1.25, 1.75), (4.1, 3.4)), ((1.2, 2.3), (2.5, 7.1)),
                 ((2.25, 1.1), (2.25, 4.8)), ((1.1, 2.25), (4.8, 2.25))]
        for a, b in cases:
            for start, end in [(a, b), (b, a)]:
                samples = line_samples(start, end)
                np.testing.assert_allclose(samples[[0, -1], :2], [start, end])
                self.assertTrue(np.all((samples[:, 2] >= 0) & (samples[:, 2] <= 1)))
                self.assertTrue(np.all(np.abs(np.diff(samples[:, :2], axis=0)) <= 1 + 1e-12))
                expected = np.array(start) + samples[:, 2, None] * (np.array(end)-start)
                np.testing.assert_allclose(samples[:, :2], expected, atol=1e-12)

    def test_line_ceil_quantization(self):
        triangle = self.triangle()
        triangle[:2, :2] = [[1.2, 2.2], [3.2, 2.2]]
        image, depth = np.zeros((8, 8, 3)), np.full((8, 8), np.inf)
        rasterize_line(image, depth, triangle, 0, 1)
        pixels = set(zip(*np.where(np.isfinite(depth))[::-1]))
        self.assertEqual(pixels, {(2, 3), (3, 3), (4, 3)})

    def test_line_duplicate_pixel_keeps_nearest(self):
        triangle = self.triangle()
        triangle[:2, :2] = [[1.2, 2.2], [3.4, 2.2]]
        triangle[:2, 2] = [.2, .8]
        triangle[:2, 4:] = [[1, 0, 0], [0, 1, 0]]
        image, depth = np.zeros((8, 8, 3)), np.full((8, 8), np.inf)
        rasterize_line(image, depth, triangle, 0, 1)
        t = 2 / 2.2  # x=3.2 e x=3.4 discretizam para x_pixel=4.
        self.assertAlmostEqual(depth[3, 4], .2 + t * .6)
        np.testing.assert_allclose(image[3, 4], [1-t, t, 0])

    def test_scanline_reversed_winding(self):
        triangle = self.triangle()
        images = []
        for face in (triangle, triangle[::-1]):
            image, depth = np.zeros((8, 8, 3)), np.full((8, 8), np.inf)
            with np.errstate(divide='raise', invalid='raise'):
                scanline(image, depth, face)
            images.append(image)
        np.testing.assert_array_equal(*images)

    def test_lighting_components(self):
        settings = Settings(ka=.5, kd=0, ks=0)
        color = np.array([.2, .4, .8])
        points = np.array([[0., 0., 0.]])
        np.testing.assert_allclose(vertex_colors(points, np.array([0, 0, 1]), color, settings),
                                   [color * .5])
        dark = replace(settings, ka=0, kd=1, light=(0, 0, -5))
        np.testing.assert_allclose(vertex_colors(points, np.array([0, 0, 1]), color, dark), 0)

    def test_eye_changes_image_and_clips(self):
        scene = world_scene(make_objects(), default_transforms())
        original, _, stats = render(scene, Settings(), (80, 60))
        changed, _, _ = render(scene, Settings(eye=(12, -18, 10)), (80, 60))
        self.assertFalse(np.array_equal(original, changed))
        self.assertGreater(stats['pixels'], 0)
        self.assertGreater(stats['backfaces'], 0)
        _, _, clipped = render(scene, Settings(near=26, far=32), (80, 60))
        self.assertGreater(clipped['outside'], 0)


if __name__ == '__main__':
    unittest.main()
