"""Vistas didáticas. Matplotlib só exibe malhas e a imagem já rasterizada."""
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from geometry import camera_matrix, transform, unit
from renderer import projected_triangles


def display_triangles(triangles, colors):
    """Divide faces grandes só na vista Matplotlib, que não possui z-buffer.

    Quatro triângulos menores têm exatamente a mesma superfície e a mesma cor.
    Isso reduz erros de ordenação do Matplotlib. A malha original não muda.
    """
    for _ in range(4):
        large = np.max(np.linalg.norm(triangles - np.roll(triangles, 1, axis=1), axis=2), axis=1) > .65
        if not large.any():
            break
        a, b, c = triangles[large].transpose(1, 0, 2)
        ab, bc, ca = (a+b)/2, (b+c)/2, (c+a)/2
        small = np.stack([np.stack(t, axis=1) for t in
                          ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))], axis=1)
        triangles = np.concatenate([triangles[~large], small.reshape(-1, 3, 3)])
        colors = np.concatenate([colors[~large], np.repeat(colors[large], 4, axis=0)])
    return triangles, colors


def draw_mesh(ax, mesh, normals=False):
    triangles = mesh.vertices[mesh.faces]
    # Ambiente + difusa da wiki permitem enxergar a orientação das faces em 3D.
    intensity = .30 + .70 * np.maximum(mesh.normals @ unit(np.array([-3., -6., 12.])), 0)
    colors = intensity[:, None] * mesh.color
    displayed, colors = display_triangles(triangles, colors)
    ax.add_collection3d(Poly3DCollection(displayed, facecolors=colors,
                                       edgecolors=colors, linewidths=.2))
    if normals:
        step = max(1, len(triangles) // 20)
        centers = triangles.mean(axis=1)[::step]
        directions = mesh.normals[::step]
        ax.quiver(*centers.T, *directions.T, length=.35, color='black', linewidth=.6)


def axes3d(ax, vertices, labels=('x', 'y', 'z')):
    low, high = vertices.min(axis=0), vertices.max(axis=0)
    center = (low + high) / 2
    radius = max((high-low).max() * .57, 1)
    ax.set(xlim=(center[0]-radius, center[0]+radius),
           ylim=(center[1]-radius, center[1]+radius),
           zlim=(center[2]-radius, center[2]+radius),
           xlabel=labels[0], ylabel=labels[1], zlabel=labels[2])
    ax.set_box_aspect((1, 1, 1))
    ax.scatter(0, 0, 0, color='black', s=15)
    ax.view_init(elev=23, azim=-65)


def draw_view(figure, kind, objects, scene, settings, normals=False):
    figure.clear()
    if kind == 'Objetos':
        for i, mesh in enumerate(objects):
            ax = figure.add_subplot(2, 3, i+1, projection='3d')
            draw_mesh(ax, mesh, normals)
            axes3d(ax, mesh.vertices)
            ax.set_title(f'{mesh.name}: {len(mesh.vertices)} V / {len(mesh.faces)} F')
        figure.text(.71, .18, 'Origem própria em cada objeto\n'
                    'z aponta para cima\nUma cor base por objeto\n'
                    'Faces e arestas trianguladas', fontsize=11, linespacing=1.8)
        figure.tight_layout()
        return
    ax = figure.add_subplot(111, projection='3d')
    if kind == 'Mundo':
        for mesh in scene:
            draw_mesh(ax, mesh, normals)
        axes3d(ax, np.vstack([m.vertices for m in scene]))
        ax.set_title('Mundo: escala → rotação → translação; limite |x,y,z| ≤ 10')
    else:
        view = camera_matrix(settings.eye, settings.at, settings.aux)
        camera_scene = [transform(m, view) for m in scene]
        for mesh in camera_scene:
            draw_mesh(ax, mesh, normals)
        origin = view[:3, 3]
        ax.scatter(*origin, color='red', s=45)
        ax.text(*origin, '  Origem do mundo', color='red')
        ax.text(0, 0, 0, 'eye', color='black')
        vertices = np.vstack([m.vertices for m in camera_scene] + [origin[None], np.zeros((1, 3))])
        if kind == 'Projeção':
            triangles, _ = projected_triangles(scene, settings, 4/3)
            depths = -np.concatenate([m.vertices[:, 2] for m in camera_scene])
            positive = depths[depths > 0]
            distance = np.clip(.6 * positive.min() if len(positive) else settings.near,
                               settings.near, settings.far)
            extent = distance * np.tan(np.radians(settings.fov)/2)
            for triangle in triangles:
                points = np.column_stack([triangle[:, 0] * extent * 4/3,
                                          triangle[:, 1] * extent,
                                          np.full(3, -distance)])
                ax.add_collection3d(Poly3DCollection([points],
                    facecolors=[triangle[:, 4:7].mean(axis=0)], linewidths=0))
            corners = np.array([[-extent*4/3, -extent, -distance],
                                [extent*4/3, -extent, -distance],
                                [extent*4/3, extent, -distance],
                                [-extent*4/3, extent, -distance],
                                [-extent*4/3, -extent, -distance]])
            ax.plot(*corners.T, color='red', linewidth=2)
            for corner in corners[:4]:
                ax.plot(*np.array([np.zeros(3), corner / distance * settings.far]).T,
                        color='gray', alpha=.3, linewidth=.7)
            vertices = np.vstack([vertices, corners])
            ax.set_title(f'Cena 3D e projeção 2D no plano d={distance:.2f} (janela vermelha)')
        else:
            basis = view[:3, :3]
            ax.set_title('Câmera: n=eye−at; u=aux−proj_n(aux); v=n×u\n'
                         + np.array2string(basis, precision=2))
        axes3d(ax, vertices, ('u (x câmera)', 'v (y câmera)', 'n (z câmera)'))
    figure.tight_layout()
