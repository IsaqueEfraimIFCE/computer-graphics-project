---
tags: [cg, revisao]
---
# Fórmulas-Chave (revisão)

| Tema | Fórmula | Nota |
|---|---|---|
| Euler | $V - E + F = 2$ | [[Característica de Euler e Topologia]] |
| Euler–Poincaré | $V - E + F - H = 2(C - G)$ | [[Característica de Euler e Topologia]] |
| Memória raster | largura × altura × bytes/pixel | [[Representação Vetorial e Raster]] |
| Produto interno | $\mathbf{x}^T\mathbf{y} = \lvert\mathbf{x}\rvert\lvert\mathbf{y}\rvert\cos\theta$ | [[Álgebra Linear para CG]] |
| Projeção vetorial | $\text{proj}_\mathbf{u}\mathbf{v} = \frac{\mathbf{v}^T\mathbf{u}}{\lvert\mathbf{u}\rvert^2}\mathbf{u}$ | [[Álgebra Linear para CG]] |
| Produto vetorial | $\lvert\mathbf{u}\times\mathbf{v}\rvert = \lvert\mathbf{u}\rvert\lvert\mathbf{v}\rvert\sin\theta$ | [[Álgebra Linear para CG]] |
| Inversa | $A^{-1} = C^T/\det A$ | [[Álgebra Linear para CG]] |
| Mudança de base | $\mathbf{x}_{novo} = [\mathbf{i}\;\mathbf{j}]^{-1}\mathbf{x}_{antigo}$ | [[Álgebra Linear para CG]] |
| Escala | $\text{diag}(s_x, s_y)$ | [[Transformações Geométricas]] |
| Rotação | $\begin{bmatrix}\cos\alpha&-\sin\alpha\\\sin\alpha&\cos\alpha\end{bmatrix}$ | [[Transformações Geométricas]] |
| Cisalhamento | $\begin{bmatrix}1&a\\b&1\end{bmatrix}$ | [[Transformações Geométricas]] |
| Câmera | $\mathbf{n} = \text{eye} - \text{at}$; $\mathbf{u} = \text{aux} - \text{proj}_\mathbf{n}\text{aux}$; $\mathbf{v} = \mathbf{n}\times\mathbf{u}$ | [[Câmera Virtual]] |
| Perspectiva (SCN) | $x' = \frac{x}{r z\tan(\alpha/2)}$, $y' = \frac{y}{z\tan(\alpha/2)}$ | [[Projeções]] |
| Profundidade | $z' = A + B/z$, $A = \frac{f}{f-n}$, $B = -\frac{fn}{f-n}$ | [[Projeções]] |
| Cúbica | $P(t) = [t^3\,t^2\,t\,1]\,M\,G$ | [[Curvas Paramétricas]] |
| Bézier cúbica | $(1-t)^3P_0 + 3t(1-t)^2P_1 + 3t^2(1-t)P_2 + t^3P_3$ | [[Curvas Paramétricas]] |
| Phong | $I = K_aI_a + \sum(K_d\cos\theta\,I_d + K_s\cos^\alpha\phi\,I_s)$ | [[Iluminação]] |
| Holofote | $\cos(\phi)^k$ | [[Iluminação]] |
| Cohen–Sutherland | aceita se ambos 0000; rejeita se `AND` ≠ 0000 | [[Recorte (Clipping)]] |

**Matrizes de curvas:**
$$M_{Hermite} = \begin{bmatrix}2&-2&1&1\\-3&3&-2&-1\\0&0&1&0\\1&0&0&0\end{bmatrix}\qquad M_{Bézier} = \begin{bmatrix}-1&3&-3&1\\3&-6&3&0\\-3&3&0&0\\1&0&0&0\end{bmatrix}$$
