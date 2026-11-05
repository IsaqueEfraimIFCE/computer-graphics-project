---
tags: [cg, indice]
---
# Computação Gráfica — Prof. Ajalmar R. da Rocha Neto

Wiki construída a partir dos 15 PDFs de slides desta pasta (disciplina de 80 h, IFCE). Para usar, abra a pasta `Ajalmar` inteira como vault no Obsidian — assim os links para os PDFs também funcionam.

## Mapa do conteúdo

1. **Fundamentos** — [[Disciplina e Bibliografia]] · [[Histórico da CG]] · [[Áreas da Computação Visual]] · [[Percepção Visual]]
2. **Representação e modelagem** — [[Representação Vetorial e Raster]] · [[Modelagem de Sólidos]] · [[Característica de Euler e Topologia]] · [[Estruturas de Dados de Malhas]]
3. **Base matemática** — [[Álgebra Linear para CG]] · [[Sistemas de Coordenadas e Pipeline Gráfico]]
4. **Transformações** — [[Transformações Geométricas]]
5. **Visualização 3D** — [[Câmera Virtual]] · [[Projeções]]
6. **Curvas** — [[Curvas Paramétricas]]
7. **Renderização** — [[Recorte (Clipping)]] · [[Iluminação]]

Revisão rápida: [[Fórmulas-Chave]] · Origem de cada nota: [[Fontes - Slides]]

## Visão geral do pipeline

```mermaid
flowchart LR
  A[Coord. do objeto] -->|transformações| B[Coord. do mundo]
  B -->|câmera: eye, at| C[Coord. da câmera]
  C -->|projeção| D[Coord. normalizadas]
  D -->|recorte + rasterização| E[Coord. do dispositivo]
  E -->|iluminação / z-buffer| F[Imagem raster]
```

> [!note] Convenção
> Callouts `[!warning]` marcam pontos em que os slides têm erro de digitação ou ambiguidade; callouts `[!tip]` marcam complementos que não estão nos slides.
