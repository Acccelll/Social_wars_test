# Social Wars — Lote 5D.8O: alcance e perseguição no combate automático

> **Correção interpretativa posterior (5D.8R):** a ausência de comando persistido `kill` ou `move` **não comprova ausência de disparos, aquisição de alvo ou dano não letal**. O cenário `east_midshift` do [lote 5D.8R](LOTE_5D_8R.md) mostrou visualmente os dois mechas trocando tiros e exibindo números de dano, mesmo sem `kill` no período de observação. As observações de ausência de eliminação e movimentação persistida registradas neste relatório continuam válidas, mas não devem ser interpretadas como ausência geral de combate.

**Conclusão:** execução concluída, **quatro cenários de distância** aprovados no cliente original. Com o Bushwacker sempre no tile (55,45) e um Reaper Drone hostil deslocado apenas no eixo norte, o jogo eliminou automaticamente os adversários a 5, 10 e 15 tiles. Aos 20 tiles, **nenhuma eliminação ou movimentação persistida foi observada durante 25,339 segundos de amostragem de controle**.

## Fonte e segurança do experimento

- Cliente original: Social Wars 0.02a, SWF `Basesec_1.5.4.swf`, SHA-256 `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`.
- Ruffle em Chromium; servidor Flask original AcidCaos; execução em loopback.
- Vila inicial original com 40 objetos, restaurada por cenário. Os testes só inserem **Bushwacker item 1358/índice 41/PlayerID 1** e **Reaper Drone item 1376/índice 42/PlayerID 2** em tiles vagos.
- **Zero cliques manuais nas unidades**, zero comandos sintéticos de ataque/movimento/dano.
- Cada distância teve save descartável, sessão de navegador e reinicialização do servidor.
- [GitHub Actions #39363784245](https://github.com/Acccelll/Social_wars_test/actions/runs/39363784245) — sucesso.
- [Pacote original de evidências #12237824433](https://github.com/Acccelll/Social_wars_test/actions/runs/39363784245/artifacts/12237824433).

## 1. Resultados medidos

| Cenário | Tile alvo | Distância inicial (Manhattan) | `kill(42)` do cliente? | Removido do save? | Tile Bushwacker ao final |
|---|---|---:|---|---|---|
| `north_05` | (55,40) | **5** | Sim | Sim | (55,45) |
| `north_10` | (55,35) | **10** | Sim | Sim | (55,45) |
| `north_15` | (55,30) | **15** | Sim | Sim | **(55,40)** |
| `north_20` | (55,25) | **20** | Não observado | **Não** | (55,45) |

- A 5 tiles: comando `kill` aos **40,658 s** da sessão.
- A 10 tiles: `kill` aos **27,518 s** da sessão.
- A 15 tiles: `kill` aos **38,099 s** da sessão. O atacante foi persistido em (55,40), mostrando um avanço de **5 tiles** em relação à posição inicial.
- A 20 tiles: atacante em (55,45), alvo em (55,25), sem `kill`, sem movimento persistido, em **17 amostras** distribuídas ao longo de **25,339 s** após a fase de diálogo.
- **Zero erros de página** nos quatro cenários.

Os tempos de `kill` acima contam desde o início de cada navegador, **não** desde o primeiro disparo. O jogo pode começar combate durante inicialização/fechamento dos diálogos. Não comparar esses tempos como latências puras de aquisição de alvo.

## 2. O código original explica por que a detecção pode diferir do tiro

A decompilação de `core.isoengine.IsoFightingElement.acquireNewTarget()` mostra que o raio padrão usado para procurar um alvo é `Math.max(Config.AGGRO_RANGE, this.iAttackRange)`, **caso não seja passado um raio explícito**.

Em `core.isoengine.IsoUnit.IA_Attack`, uma unidade em modo de ataque calcula a distância até o alvo e procura formação/caminho de aproximação **quando a distância excede `iAttackRange`**.

Portanto, diferenciar **detecção**, **deslocamento** e **alcance de disparo** é necessário. Esses métodos não provam, sozinhos, quais valores foram utilizados na cena de teste nem que a lógica de aquisição automática partiu deles em todos os momentos.

## 3. O que a diferença 15 × 20 demonstra

Há evidência positiva de combate sem cliques até **15 tiles** na linha norte escolhida e um controle negativo temporal a **20 tiles**. Isso é consistente com algum limite/condição de aquisição, mas **não determina um raio exato entre 15 e 20**, pois:
- não houve medições nos intervalos de 16 a 19 tiles;
- a distância informada é **Manhattan entre tiles**, não distância A* nem linha de visão;
- o inimigo em (55,25) está fora da área visível da câmera nas screenshots, embora ainda conste do save;
- terreno, zonas ativas, o momento de carregamento da unidade e scripts do mapa podem influenciar a detecção;
- o cenário de 20 tiles foi acompanhado por aproximadamente 25 segundos; ausência de `kill` nesse período não é prova de incapacidade permanente.

Nos cenários com `kill`, o alvo já havia sido removido antes da **primeira amostra de controle**; portanto os dados de distância não medem o instante do primeiro golpe nem a curva de HP.

## 4. Recursos entregues

- `tools/seed_auto_aggro_5d8o.py` — fixture imutável da vila original, com as posições testadas;
- `tests/original/client_aggro_distances_5d8o.mjs` — capturas do cliente original e logs de movimento, `kill` e estado do save, sem cliques em unidades;
- `.github/workflows/auto-aggro-distances-5d8o.yml` — quatro execuções sequenciais isoladas, validação e artefatos;
- `data/visual/auto_aggro_distances_5d8o.json` — conclusão e limites documentados;
- `docs/LOTE_5D_8O.md` (este relatório).

O pacote CI contém `summary.json`, `report.json` de cada distância, screenshots, `session.webm` por cenário e hashes dos fixtures. Vídeos e imagens não são comitados ao Git.

## Próximo microlote — 5D.8P

Restringir a busca aos tiles **16, 17, 18 e 19**, repetindo em um segundo eixo para eliminar a hipótese de um limite apenas posicional. Depois recuperar `Config.AGGRO_RANGE` e os critérios de `getNearestTarget` do ActionScript original, distinguindo o raio de aquisição da distância real de ataque e dos obstáculos. O cliente independente recompilado ainda não foi demonstrado como equivalente ao original.
