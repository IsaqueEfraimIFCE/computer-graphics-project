---
tags: [cg, projecao]
fonte: "[[cáp 02 - projeções.pdf]], [[cáp 02 - projecoo perspectica e scn.pdf]]"
---
# Projeções e Sistema de Coordenadas Normalizado

Com os objetos no sistema da [[Câmera Virtual|câmera]], a **projeção** leva as coordenadas de 3D para 2D.

## Elementos de um modelo de projeção
- **Plano de projeção:** onde a imagem 2D se forma.
- **Objetos da cena:** o que será projetado.
- **Centro de projeção:** onde está o observador.
- **Raios de projeção:** linhas do centro até os vértices.

## Paralela × perspectiva

| | Paralela | Perspectiva |
|---|---|---|
| Raios | paralelos entre si | partem do centro de projeção (a origem do SCC) |
| Centro de projeção | no infinito | a uma distância finita |
| Como projeta | descarta uma componente | divide por z |
| Tamanho | igual ao da cena | o que está perto aparece maior |
| Realismo | baixo | alto, como uma câmera física |
| Subtipos | ortogonal e oblíqua | — |

## Elementos da perspectiva
O volume de visão é um **tronco de pirâmide** (*frustum*).
- **FoV** ($\alpha$): ângulo de visão **vertical** a partir do eye.
- **Aspect ratio** $r = w/h$: por exemplo, 800/600 = 1,33; 1920/1080 = 1,78; 1920/1200 = 1,60.
- **Plano próximo** ($n$, *near*) e **plano distante** ($f$, *far*).
- A janela de projeção é mapeada para o **backbuffer** do hardware. Por convenção se usa $h = 2$, então $w = 2r$.
- Ângulo horizontal $\beta$: $\tan(\beta/2) = r\,\tan(\alpha/2)$.

## Projetando um ponto (semelhança de triângulos)
Pela vista lateral, para y, e pela vista superior, para x:
$$y' = \frac{y}{z\tan(\alpha/2)},\qquad x' = \frac{x}{z\tan(\alpha/2)} \in [-r, r]$$

## Sistema de coordenadas normalizado (SCN)
- Elimina a dependência de $r$: a janela passa a ter $w = h = 2$.
- $-r \le x' \le r$ vira $-1 \le x'/r \le 1$; o hardware desfaz a deformação em X ao copiar para o backbuffer.
$$x_{n} = \frac{x}{r\,z\tan(\alpha/2)},\qquad y_n = \frac{y}{z\tan(\alpha/2)}$$

## Profundidade (z-buffer)
Quando vários pontos caem no mesmo pixel, vale o **mais próximo**. A placa de vídeo espera $z \in [0,1]$: 0 no plano near e 1 no far. Por isso a matriz carrega $z' = A + B/z$, e o hardware **divide tudo por z**:
$$[x\;y\;z\;1]\begin{bmatrix}\frac{1}{r\tan(\alpha/2)}&0&0&0\\0&\frac{1}{\tan(\alpha/2)}&0&0\\0&0&A&1\\0&0&B&0\end{bmatrix} = \Big[\tfrac{x}{r\tan(\alpha/2)}\;\;\tfrac{y}{\tan(\alpha/2)}\;\;Az+B\;\;z\Big]$$
Impondo $g(n) = 0$ e $g(f) = 1$:
$$A = \frac{f}{f-n},\qquad B = -\frac{f\,n}{f-n}$$

Relacionado: [[Percepção Visual]] (perspectiva), [[Recorte (Clipping)]] (janela $[-1,1]^2$)
