---
tags: [cg, coordenadas, pipeline]
fonte: "[[aula 04.pdf]]"
---
# Sistemas de Coordenadas e Pipeline Gráfico

## Básico
- Em 2D há o eixo das **abscissas** (x) e o das **ordenadas** (y), que se cruzam na **origem** O.
- Em 3D, o eixo z pode seguir a regra da **mão direita** ou da **mão esquerda**; o que muda é o sentido de z.
- Planos x-y, x-z e y-z. O plano se divide em **quadrantes**, e o espaço em **octantes**.

## Os 5 sistemas da renderização

| Sistema | Papel |
|---|---|
| **Objeto** | cada objeto é modelado no próprio sistema, a partir da origem, sem pensar onde ficará na cena; permite reusar e copiar o objeto |
| **Mundo** (universo) | compõe a cena, com os objetos posicionados |
| **Câmera** (olho/view) | a cena vista do observador — ver [[Câmera Virtual]] |
| **Normalizado** | a versão da câmera que cabe num cubo padrão — ver [[Projeções]] |
| **Dispositivo** | 2D (tela etc.); aqui a informação 3D vira 2D |

```mermaid
flowchart LR
  O[Objeto] --> W[Mundo] --> C[Câmera] --> N[Normalizado] --> D[Dispositivo]
```

As mudanças entre sistemas são feitas com [[Transformações Geométricas]] e [[Álgebra Linear para CG]] (mudança de base).
