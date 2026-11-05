---
tags: [cg, curvas]
fonte: "[[cáp 03 - curvas.pdf]]"
---
# Curvas Paramétricas

As curvas são geradas a partir de pontos conhecidos e podem **passar por todos eles** (interpolação) ou **descrevê-los da melhor forma** (aproximação).

## Formas de representação
- **Conjunto de pontos** ligados por segmentos de reta: é a forma mais simples, mas curvas acentuadas exigem muitos pontos.
- **Analítica não paramétrica:** y em função de x.
  - *Explícita:* $y = 3x + 1$, um y para cada x.
  - *Implícita:* $x^2 + y^2 - r^2 = 0$, que admite vários y para o mesmo x.
  - Problemas: pontos com espaçamento desigual e dependência do sistema de coordenadas.
- **Paramétrica:** as coordenadas dependem de um parâmetro, por exemplo $x = 2t + 1,\; y = t + 3$. É independente do sistema de coordenadas (basta acrescentar $z(t)$), e o espaçamento é controlado por $t \in [0,1]$.

> [!warning] Erro de digitação nos slides
> O círculo implícito aparece como $y^2 + x^2 + r = 0$; o correto é $x^2 + y^2 - r^2 = 0$.

## Cúbicas paramétricas
Curvas complexas são feitas unindo segmentos cúbicos com a continuidade desejada.
$$P(t) = [x(t)\;y(t)\;z(t)],\qquad x(t) = a_xt^3 + b_xt^2 + c_xt + d_x\;(\text{idem } y, z)$$
$$P(t) = \mathbf{t}\,C,\qquad \mathbf{t} = [t^3\;t^2\;t\;1],\qquad C_{4\times3} = M_{4\times4}\,G_{4\times3}$$
- $M$ é a matriz da técnica; $G$ guarda os 4 elementos geométricos.
- As mais conhecidas são **Hermite**, **Bézier** e **B-spline** (esta só é citada nos slides).

## Hermite
$G = [P_1;\,P_2;\,T_1;\,T_2]$: dois pontos e duas tangentes. $P(0) = P_1$, $P(1) = P_2$, $P'(0) = T_1$, $P'(1) = T_2$, com $P'(t) = 3at^2 + 2bt + c$.

O sistema $G = BC$ tem
$$B = \begin{bmatrix}0&0&0&1\\1&1&1&1\\0&0&1&0\\3&2&1&0\end{bmatrix},\qquad M_H = B^{-1} = \begin{bmatrix}2&-2&1&1\\-3&3&-2&-1\\0&0&1&0\\1&0&0&0\end{bmatrix}$$
$$P(t) = [t^3\;t^2\;t\;1]\;M_H\;\begin{bmatrix}P_1\\P_2\\T_1\\T_2\end{bmatrix}$$
> [!tip] Forma expandida
> $P(t) = (2t^3-3t^2+1)P_1 + (-2t^3+3t^2)P_2 + (t^3-2t^2+t)T_1 + (t^3-t^2)T_2$

## Bézier
Usa **4 pontos de controle** no lugar de 2 pontos e 2 vetores. Para grau $n$, com polinômios de Bernstein:
$$P(t) = \sum_{i=0}^{n} P_i\,J_{n,i}(t),\qquad J_{n,i}(t) = \binom{n}{i}t^i(1-t)^{n-i},\qquad \binom{n}{i} = \frac{n!}{i!(n-i)!}$$
Para a cúbica ($n = 3$):
$$P(t) = (1-t)^3P_0 + 3t(1-t)^2P_1 + 3t^2(1-t)P_2 + t^3P_3$$
$$M_B = \begin{bmatrix}-1&3&-3&1\\3&-6&3&0\\-3&3&0&0\\1&0&0&0\end{bmatrix},\qquad G = [P_0;P_1;P_2;P_3]$$
> [!warning] Slides
> No último slide de Bézier, o vetor G repete os rótulos de Hermite ($P_1, P_2, T_1, T_2$); o correto são os 4 pontos de controle. A curva passa por $P_0$ e $P_3$; $P_1$ e $P_2$ só "puxam" a forma (as tangentes nas pontas são $3(P_1 - P_0)$ e $3(P_3 - P_2)$).
