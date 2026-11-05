---
tags: [cg, modelagem, topologia]
fonte: "[[aula 03.pdf]]"
---
# Característica de Euler e Topologia

Um poliedro (como o cubo) tem **faces** (polígonos planos), **arestas** (*edges*, onde duas faces se encontram) e **vértices** (as pontas das arestas).

## Característica de Euler
Euler (suíço, nascido em 1707) descobriu que, para poliedros sem furos:
$$N_E = V - E + F = 2$$
Decompor o objeto de outro jeito não altera o valor.

## Topologia × geometria
- A **geometria** mede comprimentos, áreas, volumes e ângulos.
- A **topologia** estuda conectividade e "furos". Euler é considerado o fundador da área.
- Um balão dobrado em forma de cão mantém a topologia e muda a geometria; perfurar o balão muda a topologia. Deformar sem rasgar nem cortar preserva a topologia.
- Para superfícies curvas (cilindro, esfera, toro), admitem-se **arestas curvas** e **faces não planas**: as arestas são os limites entre faces, e os vértices são os limites das arestas.

## Euler–Poincaré
Inclui furos e componentes:
$$N_E = V - E + F - H = 2(C - G)$$
- $G$ = **genus**, furos que atravessam o sólido (genus 1 = um furo)
- $H$ = furos em faces (*holes*)
- $C$ = número de componentes conectadas

Não se transforma uma esfera num toro sem cortar ou rasgar.

## Exemplos dos slides

| Objeto | V | E | F | H | $N_E$ |
|---|---|---|---|---|---|
| Cubo | 8 | 12 | 6 | 0 | 2 |
| Cilindro (2 arestas curvas, 2 faces planas) | 2 | 3 | 3 | 0 | 2 |
| Bola de futebol (12 pentágonos + 20 hexágonos) | 60 | 90 | 32 | 0 | 2 |
| Esfera (12 longitudes × 7 latitudes; 72 retângulos + 24 triângulos) | 86 | 180 | 96 | 0 | 2 |
| Esfera, decomposição simples | 2 | 4 | 4 | 0 | 2 |
| Sólido com furo passante (C=1, G=1) | 24 | 36 | 15 | 3 | 0 |
| Toro (2 círculos em volta do furo × 4 em volta do tubo) | 8 | 16 | 8 | 0 | 0 |
| Toro, decomposição simples | 4 | 8 | 4 | 0 | 0 |
| Faixa de Möbius | 2 | 3 | 1 | 0 | 0 |

Segundo os slides: cubo, esfera e caixa → $N_E = 2$; toro, garrafa de Klein e faixa de Möbius → $N_E = 0$.

> [!warning] Cuidado
> Os slides dizem que objetos com a mesma característica de Euler "têm a mesma topologia". O inverso vale (topologia igual ⇒ mesmo $N_E$), mas o contrário não vale em geral: toro e faixa de Möbius têm $N_E = 0$ e não são homeomorfos (a faixa tem borda e não é orientável).

Relacionado: [[Estruturas de Dados de Malhas]], [[Modelagem de Sólidos]]
