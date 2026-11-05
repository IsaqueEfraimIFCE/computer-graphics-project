"""Interface essencial: posição eye, resolução e vistas do enunciado."""
import argparse
from dataclasses import replace
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import image as mpl_image
from geometry import default_transforms, world_scene
from models import make_objects
from renderer import Settings, RESOLUTIONS, render
from views import draw_view


def export_images(folder, objects, scene, settings):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for resolution in RESOLUTIONS:
        image, _, _ = render(scene, settings, resolution)
        mpl_image.imsave(folder / f'raster_{resolution[0]}x{resolution[1]}.png', image)
    for kind in ('Objetos', 'Mundo', 'Câmera', 'Projeção'):
        figure = Figure(figsize=(12, 8))
        draw_view(figure, kind, objects, scene, settings)
        figure.savefig(folder / f'{kind.lower()}.png', dpi=140)


class App:
    def __init__(self, root):
        self.root = root
        root.title('Computação Gráfica — mesa, cadeira, estante, vaso e tesoura')
        root.geometry('1200x820')
        root.minsize(940, 660)
        self.objects = make_objects()
        self.scene = world_scene(self.objects, default_transforms())
        self.settings = Settings()
        self.cache = {}

        controls = ttk.Frame(root, padding=12)
        controls.pack(fill='x')
        ttk.Label(controls, text='Câmera (eye)').pack(side='left', padx=(0, 8))
        self.eye_fields = []
        for axis, value in zip('xyz', self.settings.eye):
            ttk.Label(controls, text=axis).pack(side='left')
            entry = ttk.Entry(controls, width=8)
            entry.insert(0, str(value))
            entry.pack(side='left', padx=(3, 10))
            entry.bind('<Return>', lambda event: self.apply_camera())
            self.eye_fields.append(entry)
        ttk.Button(controls, text='Atualizar câmera', command=self.apply_camera).pack(side='left')
        ttk.Button(controls, text='Restaurar', command=self.reset).pack(side='left', padx=8)
        ttk.Label(controls, text='Resolução').pack(side='left', padx=(15, 5))
        self.resolution = ttk.Combobox(controls, values=['160×120', '320×240', '640×480'],
                                      width=10, state='readonly')
        self.resolution.current(2)
        self.resolution.pack(side='left')
        self.resolution.bind('<<ComboboxSelected>>', self.show_raster)

        # Uma única figura: cada aba apenas seleciona a etapa a desenhar.
        self.tabs = ttk.Notebook(root)
        for title in ('Objetos', 'Mundo', 'Câmera', 'Projeção', 'Rasterização'):
            self.tabs.add(ttk.Frame(self.tabs), text=title)
        self.tabs.pack(fill='x', padx=12)
        self.figure = Figure(figsize=(12, 7))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.status = tk.StringVar()
        ttk.Label(root, textvariable=self.status, padding=10).pack(fill='x')
        self.tabs.select(4)
        self.tabs.bind('<<NotebookTabChanged>>', self.refresh)
        self.refresh()

    def apply_camera(self):
        try:
            eye = tuple(float(entry.get().replace(',', '.')) for entry in self.eye_fields)
            settings = replace(self.settings, eye=eye)
            settings.validate()
        except ValueError as error:
            messagebox.showerror('Posição inválida', str(error), parent=self.root)
            return
        self.settings = settings
        self.cache.clear()
        self.refresh()

    def reset(self):
        for entry, value in zip(self.eye_fields, Settings().eye):
            entry.delete(0, 'end')
            entry.insert(0, str(value))
        self.apply_camera()

    def show_raster(self, event=None):
        self.tabs.select(4)
        self.refresh()

    def refresh(self, event=None):
        kind = self.tabs.tab(self.tabs.select(), 'text')
        self.root.config(cursor='watch')
        self.root.update_idletasks()
        try:
            if kind == 'Rasterização':
                size = RESOLUTIONS[self.resolution.current()]
                if size not in self.cache:
                    self.cache[size] = render(self.scene, self.settings, size)
                image, _, stats = self.cache[size]
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.imshow(image, interpolation='nearest')
                ax.set_title(f'Imagem final • {size[0]}×{size[1]}')
                ax.axis('off')
                self.figure.tight_layout()
                self.status.set(f"{stats['total']} faces • {stats['backfaces']} traseiras descartadas • "
                                f"{stats['pixels']} pixels cobertos")
            else:
                draw_view(self.figure, kind, self.objects, self.scene, self.settings)
                self.status.set('Arraste a vista 3D para examiná-la. Use eye para mudar a câmera calculada.')
            self.canvas.draw()
        finally:
            self.root.config(cursor='')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true', help='Salva as sete vistas sem abrir janela')
    if parser.parse_args().export:
        objects = make_objects()
        export_images(Path(__file__).parent / 'resultados', objects,
                      world_scene(objects, default_transforms()), Settings())
    else:
        root = tk.Tk()
        App(root)
        root.mainloop()
