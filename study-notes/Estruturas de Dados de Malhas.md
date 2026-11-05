---
tags: [cg, modelagem, estruturas-de-dados]
fonte: "[[aula 03.pdf]]"
---
# Estruturas de Dados de Malhas

A estrutura de dados escolhida afeta a velocidade das operações e transformações geométricas sobre o sólido. As faces devem ser descritas todas no **mesmo sentido** (horário ou anti-horário).

## Baseada em vértices
- Duas listas: a de **vértices** (geometria — coordenadas) e a de **faces** (topologia — ponteiros para os vértices).
- ✅ Economiza memória. ❌ Arestas compartilhadas são **desenhadas duas vezes**.

| Vértice | V1 | V2 | V3 | V4 |
|---|---|---|---|---|
| Coord. | (x1,y1,z1) | (x2,y2,z2) | (x3,y3,z3) | (x4,y4,z4) |

| Face | Vértices |
|---|---|
| P1 | V1, V2, V4 |
| P2 | V2, V3, V4 |

## Baseada em arestas
- Acrescenta uma lista de **arestas**: as coordenadas descrevem os vértices, os vértices descrevem as arestas e as arestas descrevem as faces.
- Cada aresta guarda referências às **duas faces** que a compartilham ($\lambda$ = nenhuma face).
- ✅ Cada aresta é **desenhada uma só vez** (basta percorrer a lista). ❌ Gasta mais memória.

| Aresta | E1 | E2 | E3 | E4 | E5 |
|---|---|---|---|---|---|
| Vértices, faces | V1,V2,P1,λ | V2,V3,P2,λ | V3,V4,P2,λ | V2,V4,P1,P2 | V1,V4,P1,λ |

| Face | Arestas |
|---|---|
| P1 | E1, E4, E5 |
| P2 | E2, E3, E4 |

Relacionado: [[Característica de Euler e Topologia]]
