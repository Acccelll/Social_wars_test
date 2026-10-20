# Social Wars — Lote 5D.8Y: matrizes originais do `projectilePoint` do Bushwacker

**Resultado:** cinco pontos de disparo recuperados em coordenadas **locais de `DefineSprite 1092`**, a partir do SWF original, com composição das matrizes do sprite direcional e do marcador. Criamos uma API TypeScript tipada e um **inspetor gráfico executável em `/muzzle`** para as oito orientações. A arena existente não recebeu offsets absolutos inventados.

## 1. Proveniência e método

- Arquivo original: `assets/sprites/1358_bushwacker.swf`; SHA-256 `e9db23f98dcaa5cf81cbcdac85154fcb1da92a205b7d9047a5d420fb9d068c5e`. Fonte: distribuição original 0.02a. Nenhum SWF foi alterado ou registrado no Git.
- `tools/bushwacker_marker_matrices_5d8y.py` lê os tags `DefineSprite` e `PlaceObject` com `tools/visual_timelines.py`, recupera as 258 definições, simula a display list em cada quadro de ataque e encontra o único caminho raiz → sprite direcional → `projectilePoint`.
- As cinco raízes de ataque do sprite 1092 (frames 11–15) possuem respectivamente os sprites **643, 675, 716, 752, 786**, todos colocados na profundidade 1.
- O filho direcional contém o marcador de nome `projectilePoint` colocado no frame interno 11. O parser não encontrou erros de leitura de tags.
- Composição **sem omitir o espelhamento do filho**. Cada um dos cinco filhos é posicionado no sprite raiz com `scaleX=-1` e translation próprios.
- Formato Flash `[a,b,c,d,tx,ty]` aplicado como `x'=a*x+c*y+tx, y'=b*x+d*y+ty`. Os deslocamentos são registrados em **twips**; o relatório converte somente na etapa final usando **20 twips por pixel**.

### Posição final calculada no espaço local do sprite 1092

| Frame raiz de ataque | DefineSprite interno | Marker local no filho (twips) | Transform da raiz `(sx,tx,ty)` | Resultado no sprite 1092 (px) |
|---|---:|---|---|---|
| 11 | 643 | (−2150, −7903) | (−1, 173, 469) | **(116,15; −371,70)** |
| 12 | 675 | (−3943, −6910) | (−1, 1148, 926) | **(254,55; −299,20)** |
| 13 | 716 | (−2551, −4658) | (−1, 1180, 1008) | **(186,55; −182,50)** |
| 14 | 752 | (−650, −2469) | (−1, 1144, 904) | **(89,70; −78,25)** |
| 15 | 786 | (2197, −2610) | (−1, 319, 416) | **(−93,90; −109,70)** |

O cálculo completo inclui `scaleX` **duas vezes se for necessário espelhar a orientação lógica exterior**: uma vez na matriz do filho que já está no SWF, e outra no controle da unidade (`scaleX=-1` para direções 6–8). Não inverter X internamente mais uma vez sem fundamento.

O resultado binário completo mantém matrizes e caminhos originais como prova em [CI de extração 5D.8Y](https://github.com/Acccelll/Social_wars_test/actions/runs/39471783965), no artefato `original-bushwacker-muzzle-matrix-chain-5d8y`.

## 2. Nova API independente

[`rebuild/combat/src/bushMuzzle.ts`](../rebuild/combat/src/bushMuzzle.ts) disponibiliza:

- `BUSH_ATTACK_MARKERS` — cinco registros imutáveis com IDs, frames, matrizes e `projectilePoint`.
- `multiplyAffine()` e `transformPoint()` — composição e transformação genérica para verificar os dados sem depender de Flash.
- `bushMuzzleLocal(pose)` — retorna os pontos (twips e pixels) **locais do sprite**.
- `bushMuzzleForDirection(1..8)` — aplica a regra de cinco poses + espelhamento original recuperada no 5D.8X.
- `calibratedBushMuzzle()` — converte para Canvas **somente quando são fornecidos explicitamente** origem medida e escala medida do sprite.

Essa restrição é deliberada: o bitmap usado na arena é um atlas gerado pelo FFDec **recortado e redimensionado**, e o canvas exibe esse atlas com outro tamanho. A coordenada de `DefineSprite 1092` não pode ser somada à posição visual do Bushwacker sem recuperar/medir a origem de registro do sprite e a escala final.

## 3. Inspetor visual funcional, sem confundir eixos

- `rebuild/combat/demo/muzzle.html` e `muzzle.js`: gráfico SVG independente com os cinco pontos locais medidos e seleção das **oito direções**.
- O inspetor mostra ID de sprite, frame de ataque, twips e pixels, além de destacar o marcador selecionado e destacar o ponto correspondente espelhado no eixo horizontal para as direções 6–8.
- Acesse **http://127.0.0.1:5179/muzzle** com o pacote compilado.
- A arena `/arena` ganhou um link de acesso ao inspetor; mantém a origem visual provisória de bala já existente, evitando uma regressão provocada por offsets não calibrados.

### Testes de confiabilidade

`rebuild/combat/test/bushMuzzle.test.mjs` confirma todas as coordenadas, a composição `scaleX=-1`, as oito direções lógicas, os marcadores locais e a exigência de uma âncora medida antes da conversão para Canvas.

A workflow `bush-muzzle-inspector-5d8y.yml` compara programaticamente os cinco valores compilados pelo TypeScript com o relatório extraído **independentemente do arquivo SWF**, depois abre o inspetor em Chromium e testa direção direita, espelhamento para esquerda e retorno à arena com 13 atlas.

## 4. Limites de fidelidade — importantes

**Verificado:** ligações diretas de sprites, matrizes `PlaceObject`, offsets `projectilePoint` locais e a regra de espelhamento de orientação original.

**Ainda pendente:** a origem real do registro do bitmap exportado pelo FFDec, a cadeia de transformação do `bmd.getChildAt(0)` até o pai na execução Flash, zoom/escala em runtime e a associação visual exata entre o quadro de arma e o disparo. O ponto raiz calculado não é equivalente, sozinho, à posição final do projétil em tela.

Também permanecem as limitações anteriores: a reconstrução independente possui apenas combate parcial e não inclui economia, missões, mapa isométrico completo ou paridade temporal total.

## 5. Próximo lote — 5D.8Z

Medir os limites e registro gráfico efetivos dos frames 11–15 no bitmap original **sem cropping arbitrário**, relacionar os cinco offsets `projectilePoint` aos pixels visíveis dos canos e calibrar com um teste visual lado a lado. Só depois ativar o posicionamento automático da origem do disparo na arena principal.
