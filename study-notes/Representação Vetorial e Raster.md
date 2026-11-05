---
tags: [cg, representacao]
fonte: "[[aula 02.pdf]]"
---
# Representação Vetorial e Raster

Na síntese de imagens a **entrada é vetorial** (contínua) e a **saída é raster** (discreta).

## Vetorial
- Ocupa pouco armazenamento, **não perde qualidade ao ampliar** e permite tratar objetos e zonas de forma isolada, o que facilita animação e composição.
- **Primitivas:** pontos, retas, curvas, superfícies 3D…
  - **Geometria** = pontos de controle
  - **Topologia** = conexões entre os pontos (arestas, faces)
  - **Atributos** = aparência (por exemplo, a cor)
- Segmento de reta entre $P_i$ e $P_f$:
$$(x,y,z) = (P_f - P_i)\,t + P_i,\quad t\in[0,1]$$

## Raster (matricial / bitmap)
- A imagem é uma matriz de **pixels** (*picture elements*), monocromática ou RGB.
- A memória depende da resolução e do número de cores. Exemplo: $800\times600\times3\text{ bytes} = 1.440.000 \approx 1{,}4\text{ MB}$.

## Conversões
- **Rasterização:** vetorial → raster. Converte modelos 3D para uma representação inteira guardada na memória de vídeo e pode gerar "dentes" (serrilhado).
- **Vetorização:** raster → vetorial. Serve para obter imagens escaláveis sem perda de definição.

## Aliasing
- É efeito da **subamostragem**: primitivas simples, como retas, desenhadas em telas de baixa resolução ficam serrilhadas.
- As técnicas de **anti-aliasing** atenuam esse efeito.

Relacionado: [[Modelagem de Sólidos]], [[Recorte (Clipping)]]
