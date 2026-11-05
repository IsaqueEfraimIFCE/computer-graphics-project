---
tags: [cg, renderizacao, iluminacao]
fonte: "[[cáp 05 - iluminação.pdf]]"
---
# Iluminação

Sem iluminação, um objeto de cor única (uma esfera, por exemplo) parece chapado. A CG usa regras simplificadas de óptica para modelar a interação da luz com os objetos.

**Contexto no pipeline:** objetos → faces → polígonos (triângulos/trapézios) → arestas. A rasterização de retas dá os pixels de borda, e a de polígonos dá o preenchimento. A **cor** de um pixel vem da modelagem do objeto; a **intensidade** depende do ambiente e das fontes de luz.

## Física básica
- A luz visível vai de **380 a 750 nm**. Um objeto reflete o comprimento de onda da sua cor e absorve os demais: o vermelho sob luz branca reflete só o vermelho.
- A luz anda em linha reta, se propaga em todas as direções e sua intensidade cai com o **inverso do quadrado da distância**.

## Fontes de luz

| Tipo | Parâmetros | Observações |
|---|---|---|
| **Ambiente** | cor, intensidade | constante na cena toda, sem equivalente físico; imita a luz refletida por superfícies difusas e garante uma iluminação mínima |
| **Direcional** | cor, intensidade, direção | raios paralelos, sem atenuação; simula o **sol** |
| **Pontual** | cor, intensidade, posição p | emite em todas as direções, com atenuação $1/d^2$; lâmpadas, faíscas, explosões |
| **Holofote** (spot) | as da pontual + direção do cone, abertura e decaimento | concentração $\cos(\phi)^k$ |

## Luz e meios
- **Transparente:** a trajetória da luz se mantém (vidro, celofane, ar, água).
- **Translúcido:** a luz se espalha e a nitidez se perde (vidro trabalhado, plástico fosco, papel vegetal).
- **Opaco:** bloqueia a luz (giz, madeira, metais, a maioria dos objetos).
- Fenômenos: **absorção**, **transmissão**, **refração** (muda direção e velocidade entre meios) e **reflexão**.
- A cor de um objeto opaco vem da luz **difusa** que ele reflete; um objeto preto absorve tudo. Superfícies **polidas** refletem de forma **especular** (regular); superfícies **rugosas**, de forma **difusa**.

## Modelo de Phong (anos 1970)
Combina três componentes: **ambiente** (reflexão do meio), **difusa** (superfícies ásperas, a opacidade) e **especular** (superfícies polidas, o brilho).

- Cada fonte tem intensidades RGB $I_d$ (difusa) e $I_s$ (especular); o ambiente tem $I_a$.
- Cada objeto tem, por canal, $\{K_a, K_d, K_s, \alpha\}$, com $0 \le K \le 1$.

| Componente | Fórmula |
|---|---|
| Ambiente | $A = K_a I_a$ |
| Difusa | $D = K_d\,(\mathbf{L}^T\mathbf{N})\,I_d = K_d\cos\theta\,I_d$ |
| Especular | $S = K_s\,(\mathbf{R}^T\mathbf{V})^\alpha\,I_s = K_s\cos^\alpha\phi\,I_s$ |

- $\mathbf{L}$ = direção da luz incidente, $\mathbf{N}$ = normal da superfície, $\mathbf{R}$ = direção refletida, $\mathbf{V}$ = direção do observador (todos unitários).

$$I_p = K_aI_a + \sum_{l\in\text{fontes}}\big(K_d\cos\theta_l\,I_{d,l} + K_s\cos^\alpha\phi_l\,I_{s,l}\big)$$

> [!warning] Sobre α
> Na soma final o slide omite o expoente α do termo especular. Os slides dizem "quanto maior α, menor o brilho": o sentido é que, quanto maior α, **menor e mais concentrado** fica o reflexo especular — a superfície parece mais polida.

Relacionado: [[Percepção Visual]] (sombreamento como pista de profundidade)
