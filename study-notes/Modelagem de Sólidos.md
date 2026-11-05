---
tags: [cg, modelagem]
fonte: "[[aula 02.pdf]]"
---
# Modelagem de Sólidos

**Modelagem de sólidos** é o conjunto de teorias, técnicas e sistemas que criam objetos com suas propriedades geométricas e topológicas. Um sólido tem **forma própria**; gases e líquidos também são modelados em CG, mas ficam fora deste conceito.

**Definição:** um sólido é um subconjunto **fechado** e **limitado** do espaço euclidiano 3D.
- *Fechado:* tem contorno, ou seja, interior e exterior, como a pele delimita o corpo. A **garrafa de Klein** é o contraexemplo.
- *Limitado:* nenhuma dimensão é infinita.
- *Euclidiano:* obedece à geometria de Euclides; a de Lobatchevski aparece nos slides como contraste.

## Métodos de representação

| Método | Ideia | Vantagem | Desvantagem |
|---|---|---|---|
| **Aramada** (wireframe) | conjunto de arestas que definem as bordas | exibição rápida (só linhas) | **ambígua** — admite várias interpretações |
| **Por faces** (superfícies limitantes) | superfícies que delimitam o interior | é a mais comum | — |
| **Faces poligonais** | faces especiais que ladrilham o plano sem vazios (*tessellation/tiling*): triângulos equiláteros, quadrados, hexágonos | cobertura regular | — |
| **Enumeração de ocupação espacial** | divide o sólido em cubos iguais, os **voxels** (só o cubo preenche o espaço repetindo a si mesmo) | testar se um ponto pertence ao sólido, detectar interferência entre objetos, calcular massa e volume | muita memória para objetos detalhados |
| **Octree** | subdivisão espacial com voxels de tamanhos diferentes | economiza memória | — |

## Octree (árvore de octantes)
1. Um cubo envolve o objeto e é dividido em 8 cubos iguais (**octantes**).
2. Cada octante é classificado como **cheio** (todo dentro do objeto), **vazio** (todo fora) ou **cheio-vazio** (parcial).
3. Os octantes parciais são subdivididos de novo em 8, e o processo se repete enquanto houver cubos parciais.

Relacionado: [[Característica de Euler e Topologia]], [[Estruturas de Dados de Malhas]]
