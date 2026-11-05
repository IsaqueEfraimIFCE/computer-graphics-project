"""Pipeline próprio: Phong, recorte, scan line, equação da reta e z-buffer.

NumPy somente faz contas. Nenhuma biblioteca desenha os triângulos rasterizados.
"""
from dataclasses import dataclass
import numpy as np
from geometry import camera_matrix, transform

RESOLUTIONS = [(160, 120), (320, 240), (640, 480)]
BACKGROUND = np.array([.055, .075, .11])


@dataclass
class Settings:
    # Somente eye é editado pela interface. Os demais valores são fixos na cena.
    eye: tuple = (10., -20., 13.)
    at: tuple = (0., 0., 2.)
    aux: tuple = (1., 0., 0.)
    fov: float = 38.
    near: float = 1.
    far: float = 70.
    light: tuple = (-3., -6., 12.)
    ka: float = .28
    kd: float = .70
    ks: float = .22
    shininess: float = 32.

    def validate(self):
        values = [*self.eye, *self.at, *self.aux, self.fov, self.near, self.far,
                  *self.light, self.ka, self.kd, self.ks, self.shininess]
        if not np.isfinite(values).all():
            raise ValueError("Todos os parâmetros devem ser números finitos.")
        if not 5 <= self.fov <= 150 or not 0 < self.near < self.far:
            raise ValueError("Use FoV entre 5 e 150 graus e 0 < near < far.")
        if not all(0 <= k <= 1 for k in (self.ka, self.kd, self.ks)):
            raise ValueError("Os coeficientes de iluminação devem estar entre 0 e 1.")
        if not 1 <= self.shininess <= 256:
            raise ValueError("O expoente especular deve estar entre 1 e 256.")
        camera_matrix(self.eye, self.at, self.aux)


def vertex_colors(points, normal, base_color, settings):
    """Phong, normal da face em cada vértice; interpolação posterior (Gouraud)."""
    light_delta = np.asarray(settings.light) - points
    view_delta = np.asarray(settings.eye) - points
    light = light_delta / np.maximum(np.linalg.norm(light_delta, axis=1, keepdims=True), 1e-12)
    view = view_delta / np.maximum(np.linalg.norm(view_delta, axis=1, keepdims=True), 1e-12)
    cosine = np.maximum(light @ normal, 0)
    reflection = 2 * cosine[:, None] * normal - light
    specular = np.maximum(np.sum(reflection * view, axis=1), 0) ** settings.shininess
    specular[cosine <= 0] = 0
    # Luz e ambiente brancos (Ia = Id = Is = [1,1,1]).
    ambient = settings.ka * base_color
    diffuse = settings.kd * cosine[:, None] * base_color
    shine = settings.ks * specular[:, None]
    return np.clip(ambient + diffuse + shine, 0, 1)


def clip_polygon(polygon):
    """Sutherland–Hodgman nas seis faces do frustum homogêneo.

    Linhas = [x_clip,y_clip,z_clip,w,R,G,B]; -w<=x,y<=w; 0<=z<=w.
    A mesma interseção interpola posição e atributos antes da divisão por w.
    """
    planes = [(1, 0, 0, 1), (-1, 0, 0, 1), (0, 1, 0, 1),
              (0, -1, 0, 1), (0, 0, 1, 0), (0, 0, -1, 1)]
    for plane in planes:
        if len(polygon) == 0:
            break
        output = []
        previous = polygon[-1]
        before = np.dot(previous[:4], plane)
        for current in polygon:
            after = np.dot(current[:4], plane)
            if (before >= 0) != (after >= 0):
                t = before / (before - after)
                output.append(previous + t * (current - previous))
            if after >= 0:
                output.append(current)
            previous, before = current, after
        polygon = np.array(output)
    return polygon


def projected_triangles(scene, settings, aspect):
    settings.validate()
    view = camera_matrix(settings.eye, settings.at, settings.aux)
    tangent = np.tan(np.radians(settings.fov) / 2)
    a = settings.far / (settings.far - settings.near)
    b = -settings.far * settings.near / (settings.far - settings.near)
    triangles = []
    stats = dict(total=0, backfaces=0, outside=0, projected=0)
    for mesh in scene:
        camera = transform(mesh, view)
        for face, normal, camera_normal in zip(mesh.faces, mesh.normals, camera.normals):
            stats['total'] += 1
            points = camera.vertices[face]
            # Em perspectiva o raio até o centro da face é o eixo de visão local.
            if np.dot(camera_normal, -points.mean(axis=0)) <= 0:
                stats['backfaces'] += 1
                continue
            colors = vertex_colors(mesh.vertices[face], normal, mesh.color, settings)
            depth = -points[:, 2]  # n=eye-at: objetos à frente têm z_c negativo.
            clip = np.column_stack([points[:, 0] / (aspect * tangent),
                                    points[:, 1] / tangent, a * depth + b, depth, colors])
            polygon = clip_polygon(clip)
            if len(polygon) < 3:
                stats['outside'] += 1
                continue
            for i in range(1, len(polygon) - 1):
                triangle = polygon[[0, i, i + 1]].copy()
                triangle[:, :3] /= triangle[:, 3, None]
                triangles.append(triangle)
    stats['projected'] = len(triangles)
    return triangles, stats


def barycentric(points, triangle):
    a, b, c = triangle[:, :2]
    denominator = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
    if abs(denominator) < 1e-12:
        return None
    x, y = points[:, 0], points[:, 1]
    first = ((b[1]-c[1])*(x-c[0]) + (c[0]-b[0])*(y-c[1])) / denominator
    second = ((c[1]-a[1])*(x-c[0]) + (a[0]-c[0])*(y-c[1])) / denominator
    return np.column_stack([first, second, 1-first-second])


def paint_pixels(image, zbuffer, xs, ys, weights, triangle, edge=False):
    depth = weights @ triangle[:, 2]
    visible = depth <= zbuffer[ys, xs] + (1e-7 if edge else 0)
    xs, ys, weights, depth = xs[visible], ys[visible], weights[visible], depth[visible]
    # Pesos baricêntricos com correção de perspectiva para os atributos RGB.
    corrected = weights / triangle[:, 3]
    corrected /= corrected.sum(axis=1, keepdims=True)
    image[ys, xs] = np.clip(corrected @ triangle[:, 4:7], 0, 1)
    zbuffer[ys, xs] = depth


def scanline(image, zbuffer, triangle):
    """Regra par/ímpar: interseções ordenadas, preenchimento entre pares.

    Amostras no centro do pixel; intervalo semiaberto evita contar vértices 2x.
    """
    height, width = zbuffer.shape
    ymin = max(0, int(np.ceil(triangle[:, 1].min() - .5)))
    ymax = min(height, int(np.ceil(triangle[:, 1].max() - .5)))
    for y in range(ymin, ymax):
        sample_y = y + .5
        intersections = []
        for p, q in zip(triangle, np.roll(triangle, -1, axis=0)):
            if min(p[1], q[1]) <= sample_y < max(p[1], q[1]):
                intersections.append(p[0] + (sample_y-p[1]) * (q[0]-p[0]) / (q[1]-p[1]))
        intersections.sort()
        for left, right in zip(intersections[::2], intersections[1::2]):
            start = max(0, int(np.ceil(left - .5)))
            stop = min(width, int(np.ceil(right - .5)))
            xs = np.arange(start, stop)
            if not len(xs):
                continue
            points = np.column_stack([xs + .5, np.full(len(xs), sample_y)])
            weights = barycentric(points, triangle)
            if weights is not None:
                paint_pixels(image, zbuffer, xs, np.full(len(xs), y), weights, triangle)


def line_samples(start, end):
    """Método do quadro: percorre o eixo dominante e usa y=m*x+b ou x=(y-b)/m.

    Retorna [x, y, t], ainda sem discretizar. t servirá para interpolar RGB e z.
    O passo pode ser +1 ou -1; o último passo termina exatamente no extremo.
    """
    xi, yi = start
    xf, yf = end
    dx, dy = xf - xi, yf - yi
    x, y = xi, yi
    samples = [(x, y, 0.)]
    if dx == 0:  # Reta vertical, incluindo o caso de um único ponto.
        step = 1 if dy > 0 else -1
        while step * (yf - y) > 0:
            y = min(y + step, yf) if step > 0 else max(y + step, yf)
            samples.append((x, y, (y - yi) / dy))
    else:
        m = dy / dx
        b = yi - m * xi
        if abs(dx) > abs(dy):
            step = 1 if dx > 0 else -1
            while step * (xf - x) > 0:
                x = min(x + step, xf) if step > 0 else max(x + step, xf)
                y = yf if x == xf else m * x + b
                samples.append((x, y, (x - xi) / dx))
        else:
            step = 1 if dy > 0 else -1
            while step * (yf - y) > 0:
                y = min(y + step, yf) if step > 0 else max(y + step, yf)
                x = xf if y == yf else (y - b) / m
                samples.append((x, y, (y - yi) / dy))
    return np.array(samples, dtype=float)


def rasterize_line(image, zbuffer, triangle, first, last):
    """Produz os fragmentos da reta: ceil(x), ceil(y), cor e profundidade."""
    p, q = triangle[first], triangle[last]
    samples = line_samples(p[:2], q[:2])
    xs, ys = np.ceil(samples[:, :2]).astype(int).T
    t = samples[:, 2]
    height, width = zbuffer.shape
    inside = (xs >= 0) & (xs < width) & (ys >= 0) & (ys < height)
    weights = np.zeros((len(t), 3))
    weights[:, first], weights[:, last] = 1-t, t
    xs, ys, weights = xs[inside], ys[inside], weights[inside]
    # O último passo fracionário pode cair no mesmo pixel: preserve a menor profundidade.
    order = np.argsort(weights @ triangle[:, 2], kind='stable')
    _, unique = np.unique((ys * width + xs)[order], return_index=True)
    selected = order[unique]
    paint_pixels(image, zbuffer, xs[selected], ys[selected], weights[selected], triangle, edge=True)


def render(scene, settings, resolution=(320, 240)):
    width, height = resolution
    triangles, stats = projected_triangles(scene, settings, width / height)
    image = np.tile(BACKGROUND, (height, width, 1))
    zbuffer = np.full((height, width), np.inf)
    screen_triangles = []
    for triangle in triangles:
        screen = triangle.copy()
        screen[:, 0] = (screen[:, 0] + 1) * width / 2
        screen[:, 1] = (1 - screen[:, 1]) * height / 2
        screen_triangles.append(screen)
        scanline(image, zbuffer, screen)
    for triangle in screen_triangles:
        for first, last in ((0, 1), (1, 2), (2, 0)):
            rasterize_line(image, zbuffer, triangle, first, last)
    stats['pixels'] = int(np.isfinite(zbuffer).sum())
    return (image * 255).round().astype(np.uint8), zbuffer, stats
