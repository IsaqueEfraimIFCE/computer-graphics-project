"""Gera o relatório acadêmico e o ZIP. --reuse-results preserva as medições."""
import argparse
import json
from dataclasses import asdict, replace
from html import escape
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile, ZIP_DEFLATED
from matplotlib.figure import Figure
from matplotlib import image as mpl_image
from matplotlib.font_manager import FontProperties, findfont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                               Image, Table, TableStyle, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents
from app import export_images
from geometry import default_transforms, world_scene, camera_matrix
from models import make_objects
from renderer import Settings, RESOLUTIONS, render
from views import draw_view

ROOT = Path(__file__).resolve().parent
TEAM = ['[Nome e matrícula do integrante 1]', '[Nome e matrícula do integrante 2]',
        '[Nome e matrícula do integrante 3]']


class ReportDocument(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ('H1', 'H2'):
            level = 0 if flowable.style.name == 'H1' else 1
            self.notify('TOCEntry', (level, flowable.getPlainText(), self.page))


def styles():
    for suffix, weight, slant in [('', 'normal', 'normal'), ('Bold', 'bold', 'normal'),
                                 ('Italic', 'normal', 'italic')]:
        font = findfont(FontProperties(family=['Times New Roman', 'DejaVu Serif'],
                                      weight=weight, style=slant))
        pdfmetrics.registerFont(TTFont('Report' + suffix, font))
    pdfmetrics.registerFontFamily('Report', normal='Report', bold='ReportBold',
                                  italic='ReportItalic', boldItalic='ReportBold')
    body = ParagraphStyle('Body', fontName='Report', fontSize=12, leading=18,
                          alignment=TA_JUSTIFY, firstLineIndent=1.25*cm, spaceAfter=9,
                          allowWidows=0, allowOrphans=0)
    return dict(body=body,
        h1=ParagraphStyle('H1', parent=body, fontName='ReportBold', fontSize=13,
                          firstLineIndent=0, spaceBefore=16, spaceAfter=12, keepWithNext=True),
        h2=ParagraphStyle('H2', parent=body, fontName='ReportBold', firstLineIndent=0,
                          spaceBefore=12, spaceAfter=8, keepWithNext=True),
        center=ParagraphStyle('Center', parent=body, alignment=TA_CENTER, firstLineIndent=0),
        caption=ParagraphStyle('Caption', parent=body, fontSize=10, leading=13,
                               alignment=TA_CENTER, firstLineIndent=0, spaceAfter=5),
        table=ParagraphStyle('Cell', parent=body, fontSize=9, leading=12,
                             alignment=TA_CENTER, firstLineIndent=0, spaceAfter=0),
        reference=ParagraphStyle('Reference', parent=body, alignment=0, firstLineIndent=0),
        equation=ParagraphStyle('Equation', parent=body, fontSize=11, alignment=TA_CENTER,
                                firstLineIndent=0, spaceBefore=5, spaceAfter=10))


def page_number(canvas, doc):
    if doc.page > 1:
        canvas.setFont('Report', 10)
        canvas.drawRightString(A4[0]-2*cm, A4[1]-1.8*cm, str(doc.page))


def build_pdf(source, target):
    style = styles()
    paragraph = lambda text, kind='body': Paragraph(escape(text).replace('\n', '<br/>'), style[kind])
    story = [paragraph('INSTITUTO FEDERAL DO CEARÁ\n'
                       'CAMPUS FORTALEZA\nDEPARTAMENTO DE TELEMÁTICA\n'
                       'ENGENHARIA DA COMPUTAÇÃO', 'center'), Spacer(1, 1.6*cm),
             paragraph('\n'.join(TEAM), 'center'), Spacer(1, 2.2*cm),
             paragraph('MODELAGEM E VISUALIZAÇÃO DE OBJETOS\n'
                       'TRIDIMENSIONAIS EM PYTHON', 'center'), Spacer(1, 1.3*cm)]
    cover_note = ParagraphStyle('CoverNote', parent=style['body'], leftIndent=7*cm,
                                firstLineIndent=0, fontSize=11, leading=16)
    story += [Paragraph('Relatório apresentado à disciplina de Computação Gráfica, '
                        'como parte da avaliação da segunda etapa do semestre 2026.2.<br/><br/>'
                        'Professor: Ajalmar Rocha Neto, Dr.', cover_note),
              Spacer(1, 3*cm), paragraph('FORTALEZA\n2026', 'center'), PageBreak(),
              paragraph('RESUMO', 'center')]
    story.append(paragraph('Este relatório apresenta a implementação de um sistema gráfico '
        'em Python para a modelagem e a visualização de uma mesa, uma cadeira, uma estante '
        'de prateleiras, um vaso e uma tesoura. A geometria é representada por malhas '
        'triangulares construídas a partir de peças retangulares, extrusões e superfícies '
        'de revolução com perfil de Bézier. As etapas implementadas compreendem '
        'transformações geométricas, mudança para o sistema da câmera, projeção em '
        'perspectiva, descarte de faces, recorte de polígonos, iluminação nos vértices '
        'e rasterização. O preenchimento utiliza scan line e regra par/ímpar, com '
        'interpolação baricêntrica de cores e z-buffer. Foram comparadas imagens de '
        '160×120, 320×240 e 640×480 pixels, além de uma segunda posição da câmera. '
        'Os resultados mostram a influência da resolução na definição dos elementos '
        'finos e a alteração das superfícies visíveis em função do observador. '
        'As verificações automatizadas confirmaram as propriedades geométricas e '
        'os comportamentos de rasterização avaliados.'))
    story += [paragraph('Palavras-chave: computação gráfica; modelagem tridimensional; '
                        'projeção em perspectiva; rasterização.', 'reference'), PageBreak(),
              paragraph('SUMÁRIO', 'center')]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle('TOC0', fontName='Report', fontSize=12, leading=18,
                                     spaceBefore=7),
                       ParagraphStyle('TOC1', fontName='Report', fontSize=11, leading=16,
                                      leftIndent=.6*cm, spaceBefore=3)]
    story += [toc, PageBreak()]
    figure_number, references = 0, False
    for block in source.strip().split('\n\n'):
        if block.startswith('# '):
            title = block[2:]
            references = title == 'REFERÊNCIAS'
            if references:
                story.append(PageBreak())
            story.append(paragraph(title, 'h1'))
        elif block.startswith('## '):
            story.append(paragraph(block[3:], 'h2'))
        elif block.startswith('!['):
            figure_number += 1
            caption, path = block[2:].split('](', 1)
            filename = ROOT / path.rstrip(')')
            width, height = ImageReader(str(filename)).getSize()
            scale = min(16*cm/width, 10*cm/height)
            story.append(KeepTogether([
                paragraph(f'Figura {figure_number} — {caption}', 'caption'),
                Image(str(filename), width=width*scale, height=height*scale),
                paragraph('Fonte: elaboração própria.', 'caption'), Spacer(1, .3*cm)]))
        elif block.startswith('|'):
            rows = [[paragraph(cell.strip(), 'table') for cell in row.strip('|').split('|')]
                    for row in block.splitlines() if not set(row) <= set('|-: ')]
            table = Table(rows, colWidths=[16*cm/len(rows[0])]*len(rows[0]), repeatRows=1)
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eeeeee')),
                ('LINEABOVE', (0, 0), (-1, 0), .6, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), .4, colors.black),
                ('LINEBELOW', (0, -1), (-1, -1), .6, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
            story += [table, paragraph('Fonte: elaboração própria.', 'caption'), Spacer(1, .3*cm)]
        elif block.startswith('Tabela '):
            heading = paragraph(block, 'caption')
            heading.keepWithNext = True
            story.append(heading)
        elif block.startswith('> '):
            story.append(paragraph(block[2:], 'equation'))
        else:
            story.append(paragraph(block, 'reference' if references else 'body'))
    doc = ReportDocument(str(target), pagesize=A4, leftMargin=3*cm, rightMargin=2*cm,
                         topMargin=3*cm, bottomMargin=2*cm,
                         title='Modelagem e visualização de objetos tridimensionais em Python')
    doc.multiBuild(story, onFirstPage=page_number, onLaterPages=page_number)


def main(reuse_results=False):
    objects, settings = make_objects(), Settings()
    transforms = default_transforms()
    scene = world_scene(objects, transforms)
    output = ROOT / 'resultados'
    if not reuse_results:
        export_images(output, objects, scene, settings)
        figure = Figure(figsize=(12, 8))
        draw_view(figure, 'Objetos', objects, scene, settings, normals=True)
        figure.savefig(output / 'normais.png', dpi=140)
        measurements = []
        for size in RESOLUTIONS:
            start = perf_counter()
            _, _, stats = render(scene, settings, size)
            measurements.append(dict(resolution=size, seconds=perf_counter()-start, **stats))
        image, _, alternative = render(scene, replace(settings, eye=(-10., -20., 13.)), (640, 480))
        mpl_image.imsave(output / 'camera_alternativa.png', image)
        (output / 'medicoes.json').write_text(json.dumps(dict(settings=asdict(settings),
            resolutions=measurements, alternative=alternative), indent=2), encoding='utf-8')
    data = json.loads((output / 'medicoes.json').read_text(encoding='utf-8'))
    measurements, alternative = data['resolutions'], data['alternative']
    small, large = measurements[0], measurements[-1]
    values = dict(
        MESH_TABLE='| Objeto | Vértices | Arestas | Faces |\n|---|---|---|---|\n' + '\n'.join(
            f'| {m.name} | {len(m.vertices)} | {len(m.edges)} | {len(m.faces)} |' for m in objects),
        TRANSFORMS='| Objeto | Escala | Rotação (graus) | Translação |\n|---|---|---|---|\n' + '\n'.join(
            f"| {m.name} | {p['scale']} | {p['angles']} | {p['translation']} |"
            for m, p in zip(objects, transforms)),
        CAMERA=f'Eye={settings.eye}; at={settings.at}; aux={settings.aux}.',
        BASIS='Base calculada, com linhas correspondentes a u, v e n:\n' + '\n'.join(
            '[ ' + '   '.join(f'{x:.5f}' for x in row) + ' ]'
            for row in camera_matrix(settings.eye, settings.at, settings.aux)[:3, :3]),
        MEASUREMENTS='| Resolução | Pixels cobertos | Tempo (s) | Faces descartadas |\n|---|---|---|---|\n' +
            '\n'.join(f"| {m['resolution'][0]}×{m['resolution'][1]} | {m['pixels']} | "
                      f"{m['seconds']:.3f} | {m['backfaces']} |" for m in measurements),
        ANALYSIS=f"Entre as resoluções de 160×120 e 640×480, a quantidade de pixels cobertos "
            f"passou de {small['pixels']} para {large['pixels']}, um aumento de "
            f"{large['pixels']/small['pixels']:.2f} vezes. O tempo medido passou de "
            f"{small['seconds']:.3f} s para {large['seconds']:.3f} s. A diferença entre "
            'o crescimento da cobertura e o crescimento do tempo é compatível com a '
            'presença de etapas cujo custo depende da quantidade fixa de faces, além '
            'das operações por pixel. Essa interpretação se restringe às execuções medidas.',
        ALTERNATIVE=f"Nessa configuração, foram descartadas {alternative['backfaces']} faces "
                    f"traseiras, e {alternative['pixels']} pixels foram cobertos.")
    source = (ROOT / 'RELATORIO.md').read_text(encoding='utf-8')
    for key, value in values.items():
        source = source.replace('{' + key + '}', value)
    target = ROOT.parent / 'Trabalho_CG_relatorio.pdf'
    build_pdf(source, target)
    images = ['objetos', 'normais', 'mundo', 'câmera', 'projeção', 'camera_alternativa',
              'raster_160x120', 'raster_320x240', 'raster_640x480']
    files = [p for p in ROOT.iterdir() if p.suffix in ('.py', '.md', '.txt', '.bat')]
    files += [output / (name + '.png') for name in images] + [output / 'medicoes.json']
    archive = ROOT.parent / 'Trabalho_CG_codigo.zip'
    with ZipFile(archive, 'w', ZIP_DEFLATED) as zipped:
        for path in sorted(files):
            zipped.write(path, Path(ROOT.name) / path.relative_to(ROOT))
    print(f'PDF: {target}\nZIP: {archive}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse-results', action='store_true', help='Reutiliza imagens e medições existentes')
    main(parser.parse_args().reuse_results)
