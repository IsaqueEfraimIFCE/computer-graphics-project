---
tags: [cg, matematica]
fonte: "[[aula 04.pdf]]"
---
# Álgebra Linear para CG

As transformações geométricas exigem manipular vetores e matrizes.

## Escalares, pontos e vetores
- **Escalar:** um valor numérico, geralmente com unidade (10 kg, 5 cm).
- **Ponto:** uma localização, como (1, 2) ou (2, 5, −1).
- **Vetor:** $\mathbf{x} = [x_1\;x_2]^T$ em 2D ou $[x_1\;x_2\;x_3]^T$ em 3D.
- Soma, subtração e multiplicação por escalar são feitas componente a componente: $(\mathbf{x}\pm\mathbf{y})_i = x_i \pm y_i$, $(\alpha\mathbf{x})_i = \alpha x_i$.

## Produto interno
$$u = \mathbf{x}^T\mathbf{y} = \sum_i x_i y_i = |\mathbf{x}|\,|\mathbf{y}|\cos\theta,\qquad |\mathbf{x}| = \sqrt{\mathbf{x}^T\mathbf{x}}$$
- Serve para achar o **ângulo** entre vetores e para testar **ortogonalidade** (produto interno 0 ⇒ 90°).
- **Projeção** de $\mathbf{v}$ sobre $\mathbf{u}$: decompõe-se $\mathbf{v} = \mathbf{p} + \mathbf{q}$, com $\mathbf{p} = \lambda\mathbf{u}$ e $\mathbf{q}\perp\mathbf{u}$. De $(\mathbf{v}-\lambda\mathbf{u})^T\mathbf{u} = 0$ sai:
$$\text{proj}_{\mathbf{u}}\mathbf{v} = \frac{\mathbf{v}^T\mathbf{u}}{|\mathbf{u}|^2}\,\mathbf{u}$$
> [!warning] Atenção ao quadrado
> O denominador é $|\mathbf{u}|^2$ (ou $|\mathbf{u}|$ se $\mathbf{u}$ for normalizado depois: $\frac{\mathbf{v}^T\mathbf{u}}{|\mathbf{u}|}\frac{\mathbf{u}}{|\mathbf{u}|}$).

## Produto vetorial (só em 3D)
Dá um vetor **ortogonal** aos dois originais:
$$\mathbf{u}\times\mathbf{v} = \begin{vmatrix}\mathbf{i}&\mathbf{j}&\mathbf{k}\\u_1&u_2&u_3\\v_1&v_2&v_3\end{vmatrix} = (u_2v_3 - v_2u_3,\; v_1u_3 - u_1v_3,\; u_1v_2 - v_1u_2)$$
- $|\mathbf{u}\times\mathbf{v}| = |\mathbf{u}||\mathbf{v}|\sin\theta$ é a **área do paralelogramo** formado pelos dois vetores.
- Se o resultado é nulo (com vetores não nulos), os vetores são **paralelos**.

## Matrizes
- Uma matriz $n\times2$ ($n\times3$) guarda $n$ pontos em 2D (3D), um por linha (ou por coluna, no formato $2\times n$).
- **Soma e subtração** exigem dimensões iguais e são feitas elemento a elemento.
- **Multiplicação** $AB$: o número de colunas de A deve ser igual ao número de linhas de B. Cada elemento $(AB)_{ij} = \mathbf{a}_{i*}^T\mathbf{b}_{*j}$ é um produto interno de linha por coluna.
- **Identidade** $I$: 1 na diagonal, 0 no resto; $AI = A$.
- **Inversa:** $AA^{-1} = I$, com $A^{-1} = \dfrac{C^T}{\det A}$, em que os cofatores são $c_{ij} = (-1)^{i+j}\det(A'_{ij})$ e $A'_{ij}$ é $A$ sem a linha $i$ e a coluna $j$.
- **Sistemas lineares:** $AX = B \Rightarrow X = A^{-1}B$.

### Exercício dos slides (resolvido)
| Matriz | Inversa |
|---|---|
| $A=\begin{bmatrix}1&2\\3&4\end{bmatrix}$ | $\begin{bmatrix}-2&1\\1{,}5&-0{,}5\end{bmatrix}$ |
| $B=\begin{bmatrix}1&2\\1&0\end{bmatrix}$ | $\begin{bmatrix}0&1\\0{,}5&-0{,}5\end{bmatrix}$ |
| $C=\begin{bmatrix}2&1\\1&2\end{bmatrix}$ | $\frac13\begin{bmatrix}2&-1\\-1&2\end{bmatrix}$ |

## Base e mudança de base
*Fonte: [[cáp 02 - sistemas de coordenadas da camera.pdf]]*
- Uma **base** é um conjunto de vetores linearmente independentes que geram o espaço. As bases canônicas são $\mathbf{i}=(1,0)$, $\mathbf{j}=(0,1)$ em $\mathbb{R}^2$ e $\mathbf{i},\mathbf{j},\mathbf{k}$ em $\mathbb{R}^3$.
- Passar da base A para a base B obedece a $A\mathbf{x}_A = B\mathbf{x}_B$. Saindo da canônica:
$$\mathbf{x}_{novo} = [\,\mathbf{i}\;\mathbf{j}\,]^{-1}\,\mathbf{x}_{antigo}$$
- Exemplo: com a base $\mathbf{i}=(2,0)$, $\mathbf{j}=(0,2)$, o ponto $(1,0)$ vira $(0{,}5,\;0)$.
- Isso vale para bases com origem comum; quando a origem também muda, é preciso transladar antes (é o caso da [[Câmera Virtual]]).

Relacionado: [[Transformações Geométricas]]
