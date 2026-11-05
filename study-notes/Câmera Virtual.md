---
tags: [cg, camera]
fonte: "[[cáp 02 - sistemas de coordenadas da camera.pdf]]"
---
# Câmera Virtual (Sistema de Coordenadas da Câmera)

O objetivo é descrever a cena do ponto de vista de um observador. Para isso é preciso uma **nova base** de 3 vetores ortogonais na posição da câmera — ver mudança de base em [[Álgebra Linear para CG]].

- **eye:** onde a câmera está.
- **at:** o ponto que ela olha (o centro da região ou um objeto da cena).

## Construção da base
1. **n** (direção da câmera): $\mathbf{n} = \text{eye} - \text{at}$, depois normalizado ($|\mathbf{n}| = 1$).
2. **u** (*up*): escolha um vetor qualquer **aux** e retire dele a componente na direção de n, usando a [[Álgebra Linear para CG#Produto interno|projeção]]:
$$\mathbf{u} = \text{aux} - \text{proj}_{\mathbf{n}}\,\text{aux} = \text{aux} - \frac{\text{aux}^T\mathbf{n}}{|\mathbf{n}|^2}\mathbf{n}$$
   Depois normalize.
3. **v**: ortogonal a n e a u, dado pelo [[Álgebra Linear para CG#Produto vetorial (só em 3D)|produto vetorial]] $\mathbf{v} = \mathbf{n}\times\mathbf{u}$.

Os vetores $\{\mathbf{u},\mathbf{v},\mathbf{n}\}$ geram o **SCC** (sistema de coordenadas da câmera).

> [!tip] Complemento
> Para levar um ponto P do mundo para a câmera: primeiro translade ($P - \text{eye}$), depois troque de base (produto interno com u, v e n). Isso responde à pergunta dos slides "e se a base não partir da origem?".

Próximo passo do pipeline: [[Projeções]]
