"""Cinco objetos feitos de peças simples. Todas as medidas estão aqui.

Os móveis usam caixas; o vaso, um perfil Bézier; a tesoura, lâminas e aros.
Cada peça tem triângulos orientados para fora e cada objeto tem uma só cor.
"""
import numpy as np
from geometry import Mesh, model_matrix, transform


def assemble(name, color, parts):
    vertices, faces = [], []
    offset = 0
    for part in parts:
        vertices.extend(part.vertices)
        faces.extend(part.faces + offset)
        offset += len(part.vertices)
    return Mesh(name, np.array(vertices), np.array(faces), np.array(color))


def prism(outline, bottom, top):
    """Extrusão de polígono convexo anti-horário; tampas em leque."""
    outline = np.asarray(outline)
    count = len(outline)
    vertices = np.vstack([np.column_stack([outline, np.full(count, bottom)]),
                          np.column_stack([outline, np.full(count, top)])])
    faces = []
    for i in range(1, count - 1):
        faces.extend([[0, i + 1, i], [count, count + i, count + i + 1]])
    for i in range(count):
        j = (i + 1) % count
        faces.extend([[i, j, count + j], [i, count + j, count + i]])
    return Mesh('', vertices, np.array(faces), np.ones(3))


def box(size, center):
    x, y, z = np.array(size) / 2
    mesh = prism([(-x, -y), (x, -y), (x, y), (-x, y)], -z, z)
    return transform(mesh, model_matrix(translation=center))


def revolve(profile, segments=40):
    """Gira (raio,z) em torno de z; percorre o exterior de baixo para cima.

    Polos têm um só vértice; cada faixa retangular vira dois triângulos.
    Para uma cavidade, o perfil retorna pela parede interna até o fundo.
    """
    vertices, rings, faces = [], [], []
    for radius, height in profile:
        angles = np.arange(segments) * 2 * np.pi / segments if radius else [0]
        ring = []
        for angle in angles:
            ring.append(len(vertices))
            vertices.append([radius * np.cos(angle), radius * np.sin(angle), height])
        rings.append(ring)
    for lower, upper in zip(rings, rings[1:]):
        for j in range(segments):
            a, b = lower[j % len(lower)], lower[(j + 1) % len(lower)]
            c, d = upper[j % len(upper)], upper[(j + 1) % len(upper)]
            if a != b:
                faces.append([a, b, d])
            if c != d:
                faces.append([a, d, c])
    return Mesh('', np.array(vertices), np.array(faces), np.ones(3))


def bezier(control, samples=8):
    """P(t) = [t³,t²,t,1] M_B G, exatamente como na wiki."""
    matrix = np.array([[-1, 3, -3, 1], [3, -6, 3, 0],
                       [-3, 3, 0, 0], [1, 0, 0, 0]])
    t = np.linspace(0, 1, samples)
    return np.column_stack([t**3, t**2, t, np.ones(samples)]) @ matrix @ control


def oval_handle(rx, ry, tube=.10, segments=40):
    """Aro elíptico vazado: ângulo ao redor do aro e ao redor do tubo."""
    vertices, faces = [], []
    sides = 8
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        for j in range(sides):
            around = 2 * np.pi * j / sides
            vertices.append([(rx + tube * np.cos(around)) * np.cos(angle),
                             (ry + tube * np.cos(around)) * np.sin(angle),
                             tube * np.sin(around)])
    for i in range(segments):
        for j in range(sides):
            a, b = i*sides+j, ((i+1) % segments)*sides+j
            c, d = i*sides+(j+1) % sides, ((i+1) % segments)*sides+(j+1) % sides
            faces.extend([[a, b, d], [a, d, c]])
    return Mesh('', np.array(vertices), np.array(faces), np.ones(3))


def make_table():
    # Tampo, quatro pés e quatro travessas logo abaixo do tampo.
    parts = [box((3.8, 2.3, .22), (0, 0, 2.65))]
    for x in (-1.55, 1.55):
        for y in (-.85, .85):
            parts.append(box((.22, .22, 2.54), (x, y, 1.27)))
    for y in (-.85, .85):
        parts.append(box((2.88, .14, .35), (0, y, 2.365)))
    for x in (-1.55, 1.55):
        parts.append(box((.14, 1.48, .35), (x, 0, 2.365)))
    return assemble('Mesa', (.67, .40, .20), parts)


def make_chair():
    # Assento, pernas, montantes do encosto, travessas e três ripas.
    parts = [box((1.55, 1.5, .18), (0, 0, 1.55))]
    for x in (-.61, .61):
        parts.append(box((.16, .16, 1.46), (x, -.58, .73)))
        parts.append(box((.16, .16, 3.15), (x, .58, 1.575)))
        parts.append(box((.10, 1., .12), (x, 0, .65)))
    parts.append(box((1.06, .13, .23), (0, .58, 3.035)))
    parts.append(box((1.06, .13, .14), (0, .58, 1.92)))
    for x in (-.34, 0, .34):
        parts.append(box((.16, .10, .93), (x, .58, 2.455)))
    return assemble('Cadeira', (.24, .52, .57), parts)


def make_shelf():
    # Duas laterais, fundo fino, rodapé e cinco prateleiras (incluindo o topo).
    parts = [box((3.2, .10, 4.8), (0, .57, 2.4)),
             box((2.84, .95, .22), (0, 0, .11))]
    for x in (-1.51, 1.51):
        parts.append(box((.18, 1.04, 4.8), (x, 0, 2.4)))
    for z in (.31, 1.41, 2.51, 3.61, 4.71):
        parts.append(box((2.84, 1.04, .18), (0, 0, z)))
    return assemble('Estante de prateleiras', (.66, .53, .35), parts)


def make_vase():
    # Três Bézier cúbicas formam pé, bojo e pescoço. O vaso tem fundo e espessura.
    foot = bezier([[.57, 0], [.65, .10], [.90, .30], [1.02, .8]])
    belly = bezier([[1.02, .8], [1.20, 1.55], [.48, 1.80], [.43, 2.3]])
    neck = bezier([[.43, 2.3], [.40, 2.55], [.46, 2.7], [.57, 2.8]])
    outside = np.vstack([foot, belly[1:], neck[1:]])
    inside = outside[2:][::-1] - [ .12, 0 ]
    profile = np.vstack([[0, 0], outside, inside, [0, inside[-1, 1]]])
    return assemble('Vaso', (.72, .27, .19), [revolve(profile)])


def make_scissors():
    # Duas metades abertas: lâmina afilada, haste e aro. Cada metade tem sua altura.
    blade = [(-.13, -1.05), (.13, -1.05), (.25, .25), (.02, 2.65), (-.17, .30)]
    parts = []
    for angle, height, radius in [(-22, -.07, .46), (22, .07, .55)]:
        metal = prism(blade, -.045, .045)
        handle = transform(oval_handle(radius, .68), model_matrix(translation=(0, -1.62, 0)))
        half = assemble('', (1, 1, 1), [metal, handle])
        parts.append(transform(half, model_matrix(angles=(0, 0, angle), translation=(0, 0, height))))
    # Cabeça do pivô com borda chanfrada; fenda representada por duas metades da tampa.
    pivot = revolve([(0, -.17), (.19, -.17), (.19, .17), (.16, .20), (0, .20)], 24)
    parts.append(pivot)
    for x in (-.065, .065):
        parts.append(box((.10, .18, .025), (x, 0, .2125)))
    return assemble('Tesoura', (.64, .70, .77), parts)


def make_objects():
    return [make_table(), make_chair(), make_shelf(), make_vase(), make_scissors()]
