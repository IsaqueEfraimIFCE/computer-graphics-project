---
tags: [cg, transformacoes]
fonte: "[[aula 05 - transformação em escala.pdf]], [[cáp 02 - transformação em reflexão.pdf]], [[cáp 02 - transformação rotação.pdf]], [[cáp 02 - transformação em cisalhamento.pdf]]"
---
# Transformações Geométricas

Alteram a **posição, orientação, forma ou tamanho** de um objeto. Cada ponto é multiplicado por uma matriz: com vetor-coluna, $\mathbf{x}' = M\mathbf{x}$; com vetor-linha, $\mathbf{x}'^T = \mathbf{x}^T M$ (e, nesse caso, $M$ aparece transposta).

## Escala
$$S = \begin{bmatrix}s_x & 0\\ 0 & s_y\end{bmatrix},\qquad S^{-1} = \begin{bmatrix}1/s_x & 0\\ 0 & 1/s_y\end{bmatrix}$$
- $s > 1$ amplia, $0 < s < 1$ encolhe, $s = 1$ mantém.
- Exemplos: $I\,(2,3)^T = (2,3)$ (nada muda); com $s_x=s_y=2$, $(2,3) \to (4,6)$.
- A inversa desfaz a escala.

## Reflexão (espelhamento / *flip*)
Funciona como um espelho posto sobre um eixo.

| Matriz (slides) | Efeito |
|---|---|
| $M_x = \begin{bmatrix}-1&0\\0&1\end{bmatrix}$ | troca o sinal de x: o 1º quadrante vai para o 2º |
| $M_y = \begin{bmatrix}1&0\\0&-1\end{bmatrix}$ | troca o sinal de y |
| $M_{xy} = \begin{bmatrix}-1&0\\0&-1\end{bmatrix}$ | troca os dois sinais (equivale a girar 180°) |

Em 3D, usa-se a identidade com −1 na(s) componente(s) a inverter, por exemplo $\text{diag}(-1,1,1)$.

> [!warning] Nomenclatura
> Os slides chamam $M_x$ de "reflexão em relação ao eixo x" pelo critério de qual coordenada troca de sinal. Na nomenclatura mais comum, negar x é refletir **em torno do eixo y**. Confira qual convenção o professor cobra.

## Rotação (2D, em torno da origem)
Preserva a distância à origem, $r = \sqrt{\mathbf{x}^T\mathbf{x}}$. Com $x_1 = r\cos\theta$ e $x_2 = r\sin\theta$, girar de $\alpha$ dá $\beta = \theta + \alpha$:
$$x_1' = r\cos(\theta+\alpha) = x_1\cos\alpha - x_2\sin\alpha$$
$$x_2' = r\sin(\theta+\alpha) = x_1\sin\alpha + x_2\cos\alpha$$
$$R(\alpha) = \begin{bmatrix}\cos\alpha & -\sin\alpha\\ \sin\alpha & \cos\alpha\end{bmatrix}$$
> [!tip] Complemento
> $R^{-1} = R(-\alpha) = R^T$. Em 3D, a rotação em torno de z é $\begin{bmatrix}\cos\alpha&-\sin\alpha&0\\\sin\alpha&\cos\alpha&0\\0&0&1\end{bmatrix}$; para x e y é análoga.

## Cisalhamento (shear)
| Matriz | Efeito |
|---|---|
| $\begin{bmatrix}1&a\\0&1\end{bmatrix}$ | desloca x proporcionalmente a y ($x_1' = x_1 + a x_2$) |
| $\begin{bmatrix}1&0\\b&1\end{bmatrix}$ | desloca y proporcionalmente a x ($x_2' = b x_1 + x_2$) |
| $\begin{bmatrix}1&a\\b&1\end{bmatrix}$ | nas duas direções |

Em 3D, é a identidade com um termo fora da diagonal, por exemplo $\begin{bmatrix}1&a&0\\0&1&0\\0&0&1\end{bmatrix}$.

## Translação
Aparece no sumário dos slides, mas não tem deck próprio.
> [!tip] Complemento
> A translação não é linear, então usa **coordenadas homogêneas**: $\begin{bmatrix}1&0&t_x\\0&1&t_y\\0&0&1\end{bmatrix}\begin{bmatrix}x\\y\\1\end{bmatrix}$. Assim todas as transformações viram matrizes 3×3 (4×4 em 3D) e podem ser compostas por multiplicação.

Relacionado: [[Álgebra Linear para CG]], [[Câmera Virtual]]
