# Trabalho de Computação Gráfica

Mesa, cadeira, estante de prateleiras, vaso e tesoura, modelados em Python.
O código usa NumPy para as contas, Tkinter para a janela e Matplotlib para
as vistas 3D. A imagem final é calculada pelo nosso próprio rasterizador.

## Abrir

Com Python 3.10 ou superior, execute nesta pasta:

```powershell
python -m pip install -r requirements.txt
python app.py
```

No Windows, também é possível abrir `iniciar.bat` com duplo clique.

A interface tem somente:

- **Eye x, y, z:** posição da câmera, cuja alteração é exigida pelo item 3e.
- **Atualizar câmera** e **Restaurar:** aplicar os três valores ou voltar ao início.
- **Resolução:** 160×120, 320×240 ou 640×480, conforme o item 6.
- **Abas:** objetos locais, mundo, câmera, projeção e rasterização final.

A cena, a luz, `at`, `aux`, FoV e planos de recorte são fixos. O enunciado
não exige controles para esses valores. Arrastar uma vista 3D apenas muda o
ângulo de inspeção do Matplotlib; o campo `eye` muda a câmera do pipeline.
O programa aceita ponto ou vírgula decimal e rejeita câmeras degeneradas.

## Ler o código nesta ordem

| Arquivo | O que faz |
|---|---|
| `geometry.py` | Mesh, normais, arestas, transformações e base da câmera |
| `models.py` | Peças simples e uma função para construir cada objeto |
| `renderer.py` | Iluminação, projeção, recorte, equação da reta, scan line e z-buffer |
| `views.py` | Desenha as vistas didáticas dos sistemas de coordenadas |
| `app.py` | Interface com eye e resolução |
| `test_pipeline.py` | Verifica geometria e rasterização |
| `RELATORIO.md` | Texto do relatório, editável diretamente |
| `report.py` | Atualiza figuras, medições, PDF e ZIP |

Cada sólido é um `Mesh`: matriz de vértices, matriz de faces triangulares,
cor RGB, propriedade `edges` com arestas únicas e propriedade `normals` com
uma normal unitária por face. As propriedades evitam duplicar dados.

## Como os objetos são feitos

**Mesa:** tampo espesso, quatro pés e quatro travessas. **Cadeira:** assento,
quatro pernas, montantes, travessas e três ripas no encosto. **Estante:** fundo,
laterais, rodapé e cinco prateleiras. São montagens de paralelepípedos fechados.

**Vaso:** três curvas Bézier cúbicas formam pé, bojo e pescoço. O perfil gira
em torno de z; retorna pela parede interna e fecha no fundo. A boca é vazada
e a parede tem espessura. **Tesoura:** duas lâminas afiladas em alturas
diferentes, aros elípticos vazados, pivô e cabeça com fenda.

As medidas estão nas cinco funções `make_table`, `make_chair`, `make_shelf`,
`make_vase` e `make_scissors`. Não há modelos baixados, CAD, motor 3D ou CSG.
O realismo vem das proporções e das peças reconhecíveis. Conservamos a cor
única por sólido exigida no trabalho; os modelos são poligonais e opacos.

As peças de cada montagem têm malhas fechadas e normais externas próprias.
As superfícies internas de encaixes não foram removidas por união booleana;
ficam ocultas na renderização. Isso mantém a modelagem simples. A condição de
não interseção entre os cinco objetos é verificada pelas caixas AABB da cena.

## Correspondência com a wiki

| Conteúdo da wiki | Aplicação |
|---|---|
| Modelagem de Sólidos / Estruturas de Dados de Malhas | Vértices, faces e arestas; triangulação com orientação consistente |
| Álgebra Linear para CG | Produtos interno e vetorial, normalização e mudança de base |
| Transformações Geométricas | Vetores-coluna; `M = T Rz Ry Rx S` |
| Curvas Paramétricas | `P(t) = [t³,t²,t,1] M_B G` no perfil do vaso |
| Câmera Virtual | `n=unit(eye-at)`, `u=unit(aux-proj_n(aux))`, `v=n×u` |
| Projeções | Perspectiva normalizada; profundidade `A+B/d` |
| Recorte | Sutherland–Hodgman, aplicado também aos planos near/far |
| Iluminação | Ambiente, difusa e especular do modelo de Phong |

Com a base da wiki, objetos à frente têm `z_camera < 0`. Usamos `d=-z_camera`
na projeção que espera profundidade positiva. Faces traseiras são descartadas
por `N_camera · (-centro_camera) <= 0`: no eixo óptico isso corresponde ao
teste com `N_z`; em perspectiva, a direção local do raio também importa.

**Rasterização de retas conforme a fotografia do quadro do professor:**
`line_samples` calcula `dx`, `dy`, `m=dy/dx` e `b=yi-m*xi`. Se `|dx|>|dy|`,
percorre x e calcula `y=m*x+b`; caso contrário, percorre y e calcula `x=(y-b)/m`.
`rasterize_line` corresponde à produção de fragmentos, usando `ceil(x)` e `ceil(y)`.

As correções para os casos especiais são explícitas: retas verticais são tratadas
antes do cálculo de m; o passo é +1 ou -1 conforme o sentido; o último passo é
limitado ao extremo final para não ultrapassar segmentos com coordenadas
fracionárias. Extremos coincidentes produzem uma única amostra. Quando duas
amostras caem no mesmo pixel, conserva-se a menor profundidade.

O preenchimento usa scan line com regra par/ímpar e interpolação baricêntrica.
A fotografia mostra o algoritmo de retas; ela não apresenta o preenchimento
dos polígonos. Todas essas operações estão explícitas no código e sempre
participam da renderização, sem controles adicionais na interface.

Phong é calculado nos vértices com a normal da face. RGB é interpolado nos
pixels com pesos baricêntricos corrigidos pela perspectiva (Gouraud).
O z-buffer escolhe a face mais próxima. Não há suavização artificial de
normais: os detalhes dos objetos vêm das faces construídas.

O Matplotlib não possui o z-buffer deste projeto. Nas vistas didáticas,
`display_triangles` divide apenas faces grandes para reduzir os erros de sua
ordenação por profundidade. Isso não altera a malha nem o rasterizador final.

## Verificação e entrega

```powershell
python -m unittest -v
python app.py --export
python report.py
```

Os 22 testes verificam as peças fechadas e orientadas, seus volumes, Euler–Poincaré,
Bézier, câmera, transformações, clipping, equação da reta, scan line, cores e z-buffer.
Os testes de retas cobrem os oito octantes, sentidos invertidos, verticais,
horizontais, ponto único, extremos fracionários, discretização por ceil e
amostras repetidas no mesmo pixel.

`report.py` gera os dois entregáveis na pasta acima:

- `Trabalho_CG_codigo.zip`
- `Trabalho_CG_relatorio.pdf`

As figuras e medições ficam em `resultados/`. O relatório compara as três
resoluções e uma segunda posição de eye. Para finalizar a capa, preencha
`TEAM` em `report.py` e gere novamente. Confirme com a turma a exclusividade
dos objetos, uma condição que não pode ser verificada pelos arquivos locais.

Para revisar somente o texto e a diagramação, use `python report.py --reuse-results`.
Essa opção preserva as figuras e medições existentes e atualiza o PDF e o ZIP.
