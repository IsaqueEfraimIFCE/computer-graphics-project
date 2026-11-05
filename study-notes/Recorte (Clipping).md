---
tags: [cg, renderizacao, recorte]
fonte: "[[cáp 05 - recorte.pdf]]"
---
# Recorte (Clipping)

Recortar é remover a parte de um segmento (ou polígono) que fica **fora da janela de visualização**. O que está todo dentro é desenhado inteiro; o que está todo fora é descartado. Nos slides, a janela é o quadrado normalizado de $(-1,-1)$ a $(+1,+1)$ — ver [[Projeções]].

## Cohen–Sutherland (retas)
O plano é dividido em **9 regiões**, cada uma com um código de 4 bits na ordem **Topo, Baixo, Direita, Esquerda**:

| | Esquerda | Centro | Direita |
|---|---|---|---|
| **Cima** | 1001 | 1000 | 1010 |
| **Meio** | 0001 | **0000** (janela) | 0010 |
| **Baixo** | 0101 | 0100 | 0110 |

**Algoritmo:**
1. Calcule o código de cada ponta do segmento.
2. Se `cod1 == 0000` e `cod2 == 0000`, **aceite** o segmento.
3. Se `cod1 AND cod2 != 0000`, **rejeite**: o segmento está todo fora, do mesmo lado.
4. Caso contrário, **recorte**:
   1. pegue uma ponta que está fora;
   2. calcule a interseção com a borda correspondente;
   3. troque a ponta pela interseção e recalcule o código;
   4. volte ao passo 1 até o segmento ser aceito ou rejeitado.

**Interseção com uma borda vertical** $x = x_b$ (por exemplo, $x_b = -1$):
$$y_i = y_1 + m\,(x_b - x_1),\qquad m = \frac{y_2 - y_1}{x_2 - x_1}$$
> [!tip] Complemento
> Para uma borda horizontal $y = y_b$: $x_i = x_1 + (y_b - y_1)/m$.

## Sutherland–Hodgman (polígonos)
O polígono é cortado contra **cada borda** da janela retangular, uma de cada vez; a saída de uma borda é a entrada da próxima. A entrada são as arestas num único sentido (horário ou anti-horário); a saída é a lista de vértices recortados, que mistura vértices originais e novos (interseções ou cantos da janela).

| Aresta (de → para) | O que vai para a saída |
|---|---|
| fora → dentro | interseção **e** vértice de chegada |
| dentro → dentro | vértice de chegada |
| dentro → fora | só a interseção |
| fora → fora | nada |

Exemplo dos slides, com a borda direita e começando por uma aresta fora → dentro: a lista termina como `{V1β, V2, V3, V3α}`.

Relacionado: [[Representação Vetorial e Raster]] (rasterização após o recorte)
