# 1 INTRODUÇÃO

A Computação Gráfica permite produzir imagens a partir de representações matemáticas de objetos e de suas relações espaciais. Nesse processo, a geometria é inicialmente descrita em sistemas de coordenadas locais e, em seguida, submetida a transformações, projeção, análise de visibilidade, iluminação e rasterização. O estudo integrado dessas etapas permite compreender a relação entre a descrição tridimensional de uma cena e sua representação discreta em uma imagem.

Este trabalho apresenta a implementação de um sistema gráfico em Python para a modelagem e a visualização de cinco objetos cotidianos: mesa, cadeira, estante de prateleiras, vaso e tesoura. O desenvolvimento atende às etapas de modelagem, composição, câmera, projeção, iluminação e rasterização estabelecidas na proposta da disciplina [1].

A representação adotada utiliza malhas triangulares, com listas de vértices e índices de faces. Essa organização separa a geometria da conectividade e permite aplicar operações matriciais aos pontos, preservando a estrutura dos objetos [2]. A imagem final é produzida por um rasterizador implementado no projeto, enquanto as visualizações intermediárias auxiliam a análise dos sistemas de coordenadas.

# 2 OBJETIVOS

O objetivo geral é implementar e analisar as etapas de um pipeline gráfico tridimensional, desde a construção das malhas até a formação de imagens em diferentes resoluções.

Os objetivos específicos consistem em modelar os cinco objetos com triângulos orientados; compor uma cena sem interseção entre objetos e limitada ao intervalo [-10, 10] em cada coordenada; construir uma câmera com posição variável; realizar projeção em perspectiva e recorte de polígonos; calcular iluminação ambiente, difusa e especular; e comparar a rasterização em 160×120, 320×240 e 640×480 pixels.

# 3 DESENVOLVIMENTO

## 3.1 Organização da implementação

A implementação foi dividida em módulos de geometria, modelagem, renderização e interface. NumPy foi empregado nas operações vetoriais e matriciais. Tkinter foi utilizado na construção da interface, e Matplotlib, na apresentação das vistas tridimensionais e das imagens calculadas. A rasterização final das faces e arestas é realizada pelo código do projeto.

Cada objeto é armazenado em uma estrutura com matriz de vértices, matriz de faces triangulares e cor RGB. As arestas únicas e as normais são calculadas a partir desses dados. A interface permite alterar as três coordenadas da posição da câmera e selecionar a resolução da imagem. Os demais parâmetros foram mantidos fixos, permitindo comparações em condições controladas.

## 3.2 Modelagem geométrica

A mesa foi construída a partir de um tampo, quatro pés e quatro travessas de sustentação. A cadeira reúne assento, quatro pernas, montantes, travessas e três ripas no encosto. A estante possui duas laterais, fundo, rodapé e cinco prateleiras. Nesses modelos, as peças retangulares são paralelepípedos cujas seis faces são divididas em doze triângulos.

O vaso foi modelado pela revolução de um perfil composto por três curvas de Bézier cúbicas, correspondentes ao pé, ao bojo e ao pescoço. As curvas foram calculadas a partir de quatro pontos de controle, pela expressão de Bernstein apresentada no material de curvas paramétricas [3]:

> P(t) = (1−t)³P₀ + 3t(1−t)²P₁ + 3t²(1−t)P₂ + t³P₃,  0 ≤ t ≤ 1.    (1)

No código, essa expressão é avaliada em sua forma matricial. O perfil é rotacionado em 40 setores em torno do eixo z e retorna pela parede interna até o fundo. Dessa forma, a boca permanece aberta e a parede apresenta espessura.

A tesoura é composta por duas lâminas finas, obtidas pela extrusão de polígonos afilados, e dois aros elípticos de seção tubular. As metades foram posicionadas em alturas distintas e rotacionadas em sentidos opostos. Um pivô com cabeça e fenda completa a articulação. Os cinco objetos são apresentados na Figura 1, e as quantidades de elementos de suas malhas estão reunidas na Tabela 1.

![Modelos tridimensionais em seus sistemas de coordenadas locais.](resultados/objetos.png)

Tabela 1 — Composição das malhas dos objetos.

{MESH_TABLE}

## 3.3 Orientação das faces e normais

As faces de cada peça foram construídas com orientação consistente. Para uma face triangular definida pelos pontos A, B e C, a normal unitária foi calculada por:

> N = ((B−A) × (C−A)) / ‖(B−A) × (C−A)‖.    (2)

O produto vetorial determina um vetor perpendicular à superfície [4]. A ordem dos vértices foi escolhida para que esse vetor aponte para fora do material. Nas paredes internas do vaso, as normais apontam para a cavidade; nos aros da tesoura, apontam para fora do tubo, incluindo as superfícies voltadas para os furos. A Figura 2 apresenta uma amostra dessas normais.

![Amostra das normais externas das faces, representadas por setas.](resultados/normais.png)

Os móveis e a tesoura são montagens de peças fechadas, e não malhas únicas resultantes de união booleana. As superfícies internas dos encaixes permanecem na representação e são ocultadas na visualização. Essa escolha reduz a complexidade da modelagem, preservando a identificação das partes construtivas.

A verificação topológica considerou as componentes de cada malha e os furos dos aros. Foram avaliadas a incidência de duas faces por aresta, a orientação oposta das arestas compartilhadas e a positividade do volume orientado de cada peça. A relação de Euler–Poincaré foi aplicada considerando essas componentes e furos [2].

## 3.4 Composição da cena

Os modelos locais foram posicionados no sistema do mundo por escala, rotação e translação, utilizando coordenadas homogêneas. Para vetores-coluna, a transformação composta foi definida por:

> M = T Rz Ry Rx S.    (3)

A ordem de aplicação corresponde à escala, às rotações em x, y e z e, por fim, à translação. As normais são recalculadas a partir dos vértices transformados. A Tabela 2 apresenta os parâmetros utilizados, e a Figura 3 mostra a cena resultante.

Tabela 2 — Transformações dos objetos para o sistema do mundo.

{TRANSFORMS}

![Composição dos cinco objetos no sistema de coordenadas do mundo.](resultados/mundo.png)

Todos os vértices foram verificados em [-10, 10]³. A separação entre os cinco objetos foi confirmada por caixas delimitadoras alinhadas aos eixos, denominadas AABB. Esse procedimento é conservador: a ausência de sobreposição entre as caixas garante a ausência de interseção entre os objetos, embora o teste possa recusar algumas configurações geometricamente válidas.

## 3.5 Sistema de coordenadas da câmera

A câmera foi definida por sua posição eye, pelo ponto observado at e por um vetor auxiliar aux. Esses parâmetros determinam uma base ortonormal, conforme a mudança de base empregada na representação da câmera virtual [5]:

> n = unit(eye−at);  u = unit(aux−(aux·n)n);  v = n×u.    (4)

{CAMERA}

Se B é a matriz cujas linhas são u, v e n, a transformação de um ponto do mundo para a câmera é dada por:

> P_câmera = B(P_mundo−eye).    (5)

{BASIS}

A origem do sistema do mundo foi submetida à mesma transformação e destacada em vermelho na Figura 4. Alterações em eye provocam o recálculo da base e a geração de uma nova imagem. Configurações degeneradas, como eye igual a at ou aux paralelo a n, são rejeitadas.

![Cena no sistema da câmera, com identificação da origem do mundo.](resultados/câmera.png)

## 3.6 Projeção em perspectiva e recorte

A projeção em perspectiva relaciona o tamanho aparente dos objetos à sua profundidade [6]. Na convenção adotada, o eixo n aponta de at para eye; portanto, os pontos à frente da câmera apresentam coordenada z negativa. Definiu-se d=−z_câmera para empregar profundidade positiva nas equações:

> x_ndc = x / (r d tan(α/2));  y_ndc = y / (d tan(α/2)).    (6)

O ângulo de visão vertical α foi fixado em 38°, e a razão de aspecto r, em 4/3. Os planos próximo e distante foram definidos em 1 e 70, respectivamente. A profundidade normalizada foi calculada por z_ndc=A+B/d, com A=far/(far−near) e B=−far·near/(far−near), mapeando os planos próximo e distante em 0 e 1.

Antes da rasterização, foram descartadas as faces cujo produto entre a normal da câmera e a direção de observação até o centro da face é não positivo. O teste utiliza a direção local do raio de observação, necessária à perspectiva. As faces frontais remanescentes foram recortadas pelo algoritmo de Sutherland–Hodgman [7].

O recorte foi aplicado às seis faces do volume de visão, em coordenadas homogêneas, antes da divisão por w. Nas interseções, foram interpoladas a posição e a cor dos vértices. Cada polígono resultante foi triangulado em leque. A Figura 5 apresenta os objetos no espaço e suas projeções em uma janela transversal à direção de observação.

![Cena tridimensional e projeções na janela de visualização.](resultados/projeção.png)

## 3.7 Iluminação e rasterização

A iluminação foi calculada nos vértices pelo modelo de Phong, que combina contribuições ambiente, difusa e especular [8]. A cor base do objeto participa das parcelas ambiente e difusa, enquanto o brilho especular utiliza a cor branca da fonte de luz.

> I = Ka Ia + Kd max(N·L,0) Id + Ks max(R·V,0)^α Is.    (7)

Os vetores N, L, R e V representam a normal, a direção da luz, a direção refletida e a direção do observador. Foram adotados Ka=0,28, Kd=0,70, Ks=0,22 e expoente especular igual a 32, com a luz posicionada em (−3, −6, 12). A contribuição especular é anulada quando a superfície não está voltada para a luz.

O preenchimento dos triângulos foi realizado por scan line e regra par/ímpar. Em cada linha de amostragem, foram calculadas e ordenadas as interseções com as arestas, preenchendo-se os intervalos entre pares. Intervalos verticais semiabertos evitam a contagem duplicada de vértices.

As cores dos vértices foram interpoladas por coordenadas baricêntricas. Para RGB, os pesos foram corrigidos pela perspectiva, utilizando lambda_i/w_i e normalização pela soma. A profundidade normalizada foi interpolada na tela e comparada com o z-buffer, que mantém a superfície mais próxima em cada pixel.

A rasterização das arestas utiliza o método da equação explícita da reta apresentado em aula [9]. Para dx=xf−xi e dy=yf−yi, calculam-se m=dy/dx e b=yi−m·xi. Quando |dx|>|dy|, percorre-se x e obtém-se y=m·x+b. Caso contrário, percorre-se y e obtém-se x=(y−b)/m. A produção de fragmentos utiliza ceil(x) e ceil(y), conforme o procedimento apresentado no quadro.

As retas verticais são tratadas antes do cálculo de m, mantendo x constante. O passo no eixo dominante é +1 ou −1 de acordo com a ordem dos extremos. O último avanço é limitado à coordenada final, evitando ultrapassagem quando os extremos são fracionários. Um segmento de comprimento nulo produz uma única amostra. Cor e profundidade são interpoladas pela posição ao longo do segmento; se amostras coincidem no mesmo pixel, conserva-se a menor profundidade.

A avaliação da iluminação nos vértices seguida da interpolação das cores caracteriza o sombreamento de Gouraud. O procedimento conserva a normal de cada face e, consequentemente, a aparência facetada das superfícies curvas.

# 4 SIMULAÇÕES COMPUTACIONAIS E RESULTADOS

## 4.1 Condições de avaliação

Os experimentos utilizaram a mesma geometria, iluminação e câmera nas três resoluções. A cena contém 5.200 faces triangulares. Os tempos apresentados correspondem a uma execução por resolução e incluem descarte de faces, iluminação, recorte, preenchimento e rasterização das arestas. Por se tratar de medições individuais, os valores caracterizam a execução observada, sem constituir uma avaliação estatística de desempenho.

Tabela 3 — Resultados da rasterização nas três resoluções.

{MEASUREMENTS}

## 4.2 Efeito da resolução

A Figura 6 apresenta a imagem em 640×480 pixels. Nessa resolução, são distinguíveis os elementos estreitos da cadeira, os aros e as lâminas da tesoura e a abertura do vaso. A cor base de cada sólido é preservada, com variações de intensidade decorrentes da iluminação.

![Resultado da rasterização em 640×480 pixels.](resultados/raster_640x480.png)

Nas Figuras 7 e 8, a redução da resolução aumenta o serrilhado e diminui a definição dos elementos finos. As imagens foram apresentadas com ampliação para permitir a comparação visual, sem alterar os pixels produzidos pelo rasterizador. Não foi aplicado antialiasing.

![Resultado da rasterização em 320×240 pixels.](resultados/raster_320x240.png)

![Resultado da rasterização em 160×120 pixels.](resultados/raster_160x120.png)

{ANALYSIS}

A quantidade de faces descartadas permanece constante entre resoluções, pois a visibilidade é determinada antes do mapeamento para a grade de pixels. O aumento do número de amostras afeta o preenchimento e o cálculo das cores, sem modificar a geometria da cena.

## 4.3 Alteração da posição da câmera

Em um segundo experimento, a posição da câmera foi alterada para eye=(−10, −20, 13), mantendo-se o alvo, a iluminação e os objetos. A Figura 9 mostra a mudança da disposição das projeções e das superfícies visíveis.

{ALTERNATIVE}

![Imagem produzida após a alteração da posição da câmera.](resultados/camera_alternativa.png)

O resultado evidencia que a alteração de eye modifica a base de observação e a seleção de faces, sem exigir mudanças nos modelos ou em suas transformações para o mundo.

## 4.4 Verificação e limitações

Foram executados 22 testes automatizados, com aprovação em todos os casos. As verificações abrangem fechamento e orientação das peças, volume orientado, relação de Euler–Poincaré, normais internas do vaso, curvas de Bézier, transformações, base da câmera, recorte, rasterização de retas, preenchimento sem fendas, interpolação de cores e independência da ordem de desenho no z-buffer. Para as retas, foram verificados os oito octantes, sentidos invertidos, segmentos verticais e horizontais, ponto único, extremos fracionários, discretização por ceil e amostras coincidentes em um pixel.

A interface também foi verificada nas cinco vistas e nas três resoluções, incluindo alteração da câmera, rejeição de entradas inválidas e restauração da configuração inicial.

Os modelos são poligonais e opacos, sem texturas, sombras projetadas ou refração. As peças montadas conservam superfícies internas nos encaixes. As vistas tridimensionais intermediárias utilizam a ordenação de faces do Matplotlib e são destinadas à inspeção; a visibilidade da imagem final é determinada pelo rasterizador próprio. Nessas vistas intermediárias, a subdivisão de faces grandes reduz erros de ordenação sem alterar a malha empregada na rasterização.

# 5 CONCLUSÃO

O trabalho implementou as etapas necessárias à geração de imagens de uma cena composta por cinco objetos cotidianos. A modelagem por peças trianguladas e por superfícies de revolução permitiu representar características reconhecíveis da mesa, da cadeira, da estante, do vaso e da tesoura, com estruturas de dados explícitas e manipuláveis.

A composição por matrizes homogêneas, a construção da base da câmera e a projeção em perspectiva estabeleceram a passagem entre os sistemas de coordenadas. O recorte, o descarte de faces e o z-buffer trataram a visibilidade, enquanto a iluminação nos vértices e a interpolação baricêntrica determinaram as cores dos pixels.

Os experimentos evidenciaram a influência da resolução sobre a definição dos detalhes e demonstraram a atualização da imagem após a mudança da posição da câmera. Os resultados e as verificações realizadas indicam o atendimento às etapas propostas, dentro das simplificações geométricas e de iluminação adotadas.

# REFERÊNCIAS

[1] ROCHA NETO, Ajalmar. Trabalho — 2ª etapa: Computação Gráfica. Instituto Federal do Ceará, 2026.2. Enunciado da atividade, 2 p.

[2] COMPUTAÇÃO GRÁFICA. Característica de Euler, topologia de Euler e estrutura de dados em CG. [S. l.: s. n.], [s. d.]. Material de aula, arquivo aula 03.pdf.

[3] COMPUTAÇÃO GRÁFICA. Curvas. [S. l.: s. n.], [s. d.]. Material de aula, arquivo cáp 03 - curvas.pdf.

[4] COMPUTAÇÃO GRÁFICA. Transformações geométricas no plano e no espaço. [S. l.: s. n.], [s. d.]. Material de aula, arquivo aula 04.pdf.

[5] COMPUTAÇÃO GRÁFICA. Câmera virtual. [S. l.: s. n.], [s. d.]. Material de aula, arquivo cáp 02 - sistemas de coordenadas da camera.pdf.

[6] COMPUTAÇÃO GRÁFICA. Projeção perspectiva e sistema de coordenadas normalizado. [S. l.: s. n.], [s. d.]. Material de aula, arquivo cáp 02 - projecoo perspectica e scn.pdf.

[7] COMPUTAÇÃO GRÁFICA. Recorte — clipping. [S. l.: s. n.], [s. d.]. Material de aula, arquivo cáp 05 - recorte.pdf.

[8] COMPUTAÇÃO GRÁFICA. Iluminação — renderização. [S. l.: s. n.], [s. d.]. Material de aula, arquivo cáp 05 - iluminação.pdf.

[9] ROCHA NETO, Ajalmar. Rasterização de segmentos de reta pelo eixo dominante. [S. l.], [s. d.]. Notas de aula em quadro, registro fotográfico fornecido para o desenvolvimento do trabalho.
