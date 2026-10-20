# Estado consolidado — 19/10/2026

## Produto funcional

- O usuário confirmou que a distribuição **Social Wars 0.02a** iniciou e funcionou no navegador com Ruffle.
- O servidor local da distribuição original utiliza `127.0.0.1:5055`.
- Essa execução é **do jogo original**, não da versão em fontes recompilados.
- Scripts externos de inicialização/Ruffle foram **propostos como protótipos**, mas não possuem validação no Windows aqui; não os trate como distribuição comprovadamente funcional.

## Extração / análise

Cliente: `assets/flash/Basesec_1.5.4.swf`.

| Métrica extraída no lote 3C | Valor |
|---|---:|
| Declarações de classe | 1.395 |
| Declarações de método | 11.842 |
| Corpos com bytecode | 11.709 |
| Instruções AVM2 decodificadas | 650.549 |
| Strings na constant pool | 20.068 |
| Tamanho SWF descomprimido | 6.089.497 bytes |
| DoABC | `frame1` (2.048.847 bytes) |

SHA-256 do SWF de referência: `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`.

## Recuperação funcional até agora

| Área | Estado | Referência |
|---|---|---|
| `IsoFightingElement.calculateDamage` | Fórmula reconstruída a partir do P-code; não compilada no jogo | 3C–3D |
| `IsoFightingElement.recibirAtaque` | Fluxo por etapas e P-code preservados; NÃO AS3 integral | 3E |
| `battle.IAAttack` | Métodos de seleção de alvo estudados parcialmente | 3C–3D |
| `AStar.findPath/look/searchNode` | Fragmentos e porta AS3 experimental; sem build validado | 3E–3G |
| Semântica `searchNode.g` | Anomalia original identificada e testada em microinterpretador AVM2 | 3G |
| `NodesPath` | Contrato `flash.utils.Proxy`, índices, métodos e `isAI` identificado | 3H–3I |
| `IsoUnit.setMove/updateMove` | Consumo de pontos `aNodes[0]`, `TileToPixel`, `splice` identificado | 3H |
| `IsoUnit.aNodes` | Setter tipado para NodesPath e evento `onMoveStart(isAI)` identificados | 3I |
| Probe `AS3Probe` | **SWF compilado e executado em Chromium/Ruffle**, 8/8 casos ActionScript aprovados (via ExternalInterface); não é o cliente integral | 5B |
| Contratos nominais NodesPath/IsoUnit | **15/15 testes Ruffle** aprovados em doubles isolados (5C.1); cliente real NÃO integrado | 5C.1 |
| Projeto AS3 completo recompilável | NÃO EXISTE ainda | futuro |
| Port HTML5 sem Flash | NÃO EXISTE ainda | futuro |

## Testes registrados nos lotes prévios

- 3F: 7/7 cenários aprovados em **modelo Python normalizado**, não no Flash.
- 3G: 12/12 verificações de blocos de `g` com um microinterpretador AVM2 parcial.
- 3H: 27 verificações **estáticas**.
- 3I: 38 verificações de contrato em P-code/modelo, **não** no runtime AS3.
- **Lote 5A (19/10/2026):** primeiro `AS3Probe.swf` compilado com Apache Flex 4.16.1/Flash 32.0 no GitHub Actions, com cabeçalho válido.
- **Lote 5B (19/10/2026):** SWF executado **realmente** em Chromium/Ruffle 0.7.1; `ExternalInterface` devolveu `SWTEST:SUMMARY pass=8 fail=0`, 11 sinais totais e 0 erros. O `traceObserver` retornou 0 mensagens nesta configuração. Execução [39260961090](https://github.com/Acccelll/Social_wars_test/actions/runs/39260961090). Testes do **protótipo**, não paridade com o jogo original.
- **Lote 5C.1 (19/10/2026):** outro SWF `ContractProbe.swf` compilado e executado no Chromium/Ruffle; **15/15 contratos** aprovados (setter tipado, evento manual/IA, Proxy, conversão de rota, cópia independente). O `AS3Probe.swf` anterior também foi aprovado **8/8**. Workflow [39262967632](https://github.com/Acccelll/Social_wars_test/actions/runs/39262967632). **Não** foi executado o cliente original nesses testes.

Os códigos neste repositório são **protótipos**. A compilação e execução **do AS3Probe** foram demonstradas no runtime Ruffle. A reconstrução, compilação e validação **do jogo completo** continuam pendentes.

## Importante: origem dos pacotes históricos

Os arquivos `Social_Wars_0.02a_AVM2_Lote3C.zip` até os lotes 3I foram entregues na conversa original, mas **não foram importados integralmente aqui**. Este repositório armazena a documentação e a nova árvore de continuidade. Para importação verificável dos artefatos históricos, recuperar os ZIPs locais, comparar com o inventário e incluir somente fontes legalmente redistribuíveis.

## Lote 5D — Recursos visuais

- Inventário executado no GitHub Actions em 19/10/2026, execução [39277345729](https://github.com/Acccelll/Social_wars_test/actions/runs/39277345729).
- Original confirmado: distribuição oficial ZIP com **492.630.085 bytes**.
- **3.272 arquivos** no ZIP; **1.118 arquivos SWF** analisados sem erros.
- **1.899 imagens externas** com extensões PNG/JPG/GIF/WebP/BMP/SVG/APNG.
- Tags SWF: **41.069 bitmaps**, **62.318 formas vetoriais**, **316 morphshapes**, **43.426 sprites**, **53 botões**.
- Sprites declaram **400.023 quadros de timeline**, não imagens únicas.
- SWF principal `Basesec_1.5.4.swf`: **369 bitmaps, 1.468 shapes, 4 morphshapes, 1.224 sprites, 52 botões**, SHA-256 corresponde à referência.
- [`tools/visual_extract.py`](../tools/visual_extract.py) permite processar lotes com FFDec; a extração integral de PNG/SVG e de animações **não está concluída**.

## Prova de exportação do SWF principal — 5D.2

- Workflow [39277803644](https://github.com/Acccelll/Social_wars_test/actions/runs/39277803644): **success**.
- JPEXS FFDec 26.3.0 exportou **369/369 definições de bitmaps** de `Basesec_1.5.4.swf`, **0 erros**.
- Tempo do comando FFDec: aproximadamente **5,09 segundos**.
- Pasta de saída: aproximadamente **9,7 MB**.
- Artefato temporário: [social-wars-visual-export-sample](https://github.com/Acccelll/Social_wars_test/actions/runs/39277803644/artifacts/12198640486) (ID 12198640486; expira em 20/10/2026).
- A exportação completa dos outros SWFs e das animações ainda NÃO foi finalizada. Não interpretar este resultado como descompilação integral de todas as imagens.

## 5D.3 — Verificações adicionais em 19/10/2026

- **Imagens externas:** workflow [39278619312](https://github.com/Acccelll/Social_wars_test/actions/runs/39278619312) aprovado, com 1.899 arquivos extraídos (143 PNG e 1.756 JPG), 95.899.970 bytes antes da compressão do artefato, zero erros.
- **Recursos do SWF principal:** workflow [39278874264](https://github.com/Acccelll/Social_wars_test/actions/runs/39278874264) aprovado, com 7.493 arquivos PNG/SVG exportados pelo FFDec, zero erros, ~62,61 s.
- **Lote de cinco unidades:** workflow [39292249010](https://github.com/Acccelll/Social_wars_test/actions/runs/39292249010) iniciado. O resultado final depende da conclusão do Actions; não considerar aprovado sem examinar `export_results.csv`.
- **Catálogo:** `tools/visual_source_catalog.py` produz lista de SWFs por pasta e identificador. `tools/visual_asset_manifest.py` gera metadados de arquivos PNG/SVG/JPG exportados, preservando hashes e dimensões quando disponíveis.
- Recursos originais continuam fora do Git; animações completas ainda não foram reconstituídas.

## 5D.3 — Situação final deste micro-lote

- [Lote de 5 mechas](https://github.com/Acccelll/Social_wars_test/actions/runs/39292249010):
  5/5 arquivos `assets/sprites`, 14.436 imagens/vetores/quadros renderizados, 0 erros.
- [Pasta `assets/characters_2`](https://github.com/Acccelll/Social_wars_test/actions/runs/39294770739):
  26/26 SWFs, **61 bitmaps**, 0 erros.
- [12 construções](https://github.com/Acccelll/Social_wars_test/actions/runs/39295245833):
  12/12 SWFs, **116 bitmaps**, 0 erros.
- Catálogo original pesquisável [data/visual/swf_catalog.csv](../data/visual/swf_catalog.csv):
  **1.118 SWFs** e [90 arquivos candidatos a construções](../data/visual/building_candidates.csv),
  com identificação preliminar apenas pelos nomes.
- [Tabela de cobertura](../data/visual/export_coverage.csv) e
  [resumo JSON](../data/visual/coverage_summary.json) registram **44 SWFs com alguma exportação**.
- Quantidade de arquivos produzidos somando os quatro lotes SWF distintos:
  **22.106**; as imagens externas somam mais **1.899**.
- **1.074 SWFs ainda não têm exportação verificada**, e a conversão integral
  de animações editáveis continua pendente.

## 5D.4 — Timeline estrutural dos SWFs

- [Execução 39297155116](https://github.com/Acccelll/Social_wars_test/actions/runs/39297155116)
  aprovada para **1.118/1.118 SWFs** com **0 falhas de análise**.
- 43.426 sprites, 400.023 quadros declarados/observados, 2.782.788
  operações `PlaceObject` e 109.884 remoções em timelines de sprites.
- 2 advertências de interpretação de posicionamento; investigação separada.
- CSV geral e seis relatórios de eventos por quadro gerados como
  artefato temporário. Nenhum asset original foi commitado.
- Animações controladas dinamicamente por AS3 não foram recriadas.

## Registro final 5D.4

Workflow final [39297904335](https://github.com/Acccelll/Social_wars_test/actions/runs/39297904335):
**sucesso**, 1.118/1.118 SWFs, 5 testes sintéticos aprovados.
Inventário permanente: [timeline_inventory.csv](../data/visual/timeline_inventory.csv)
e [seis timelines compactadas](../data/visual/timeline_details).
As duas operações PlaceObject3 com decodificação parcial foram preservadas
em hex nos eventos `place_raw`; nenhuma animação AS3 dinâmica
foi reconstruída por este procedimento.

## Lote 5D.5 — Galeria visual animada

- FFDec exportou **8 GIFs animados** de 5 SWFs, com caracteres
  362/393 (Tetrapod), 188/189 (Splinter), 85/52 (torre),
  21 (centro de comando) e 11 (good_10_m).
- [GitHub Actions 39301011532](https://github.com/Acccelll/Social_wars_test/actions/runs/39301011532)
  concluiu com **success**, 8/8 imagens de prévia e 8/8 com múltiplos quadros.
- [Galeria HTML offline](https://github.com/Acccelll/Social_wars_test/actions/runs/39301011532/artifacts/12211297019)
  gerada e compactada (1.264.939 bytes).
- GIFs são artefatos temporários; CSV/JSON de metadados são
  armazenados na branch main, com referências aos SWFs e sprite IDs.
- As animações controladas por ActionScript ainda precisam ser
  comparadas com o runtime; não considerar a biblioteca completa.

## Lote 5D.6 — Galeria categorizada

- Workflow [39303077044](https://github.com/Acccelll/Social_wars_test/actions/runs/39303077044):
  **success**, 17/17 GIFs exportados de 14 SWFs, 0 erros.
- Categorias técnicas: **8 unidades**, **6 construções**, **3 interface/telas**.
- Novas unidades: Bushwacker #327, Reaper Drone #1654, Megatank #132.
- Novas construções: tower_2 #74, workshop_1 #52, laboratory #11.
- Interface/telas: popupResearchCenter_buildingProcess #74,
  variante _2 #73 e crossDCi #123.
- [Pacote da galeria](https://github.com/Acccelll/Social_wars_test/actions/runs/39303077044/artifacts/12212183676)
  com HTML, filtros, busca, GIFs, CSV/JSON; 1.994.256 bytes comprimidos,
  expiração prevista em **02/11/2026**.
- [CSV permanente](../data/visual/gallery_5d6.csv) e
  [JSON permanente](../data/visual/gallery_5d6.json) preservam metadados.
- A categoria é classificação preliminar baseada no arquivo; exportar
  uma prévia não garante todas as animações, efeitos nem movimentos em runtime.

## Lote 5D.7 — Auditoria de duplicações e estados

- Workflow [39304404150](https://github.com/Acccelll/Social_wars_test/actions/runs/39304404150):
  **success**, 4 testes unitários aprovados, 14 SWFs e 17 GIFs analisados.
- Uma duplicação exata comprovada por SHA-256:
  `0022_tower_1_m.swf#52` e `0040_workshop_1_m.swf#52`.
- Nenhuma equivalência nova por assinatura de pixels nem par adicional
  sinalizado pelos limiares desta amostra (não é prova de inexistência).
- **0/17 estados de ação classificados por evidência**; todos permanecem
  como `unclassified` e `original_runtime_confirmation_pending`.
- [JSON de auditoria](../data/visual/animation_review_5d7.json),
  [CSV](../data/visual/animation_review_5d7.csv) e
  [fila para revisão](../data/visual/animation_review_5d7_queue.csv)
  preservados na branch `main`.
- [Galeria HTML de revisão](https://github.com/Acccelll/Social_wars_test/actions/runs/39304404150/artifacts/12212991791)
  inclui os 17 GIFs e filtros; o arquivo é temporário.

## 5D.8A — Servidor e cliente ORIGINAL observados no Chromium/Ruffle

- Workflow [39306732074](https://github.com/Acccelll/Social_wars_test/actions/runs/39306732074)
  **success** (19/10/2026); testes sintéticos do observador e cruzamento
  de nomes de SWF aprovados.
- Servidor Flask do projeto original em **cópia descartável**, vila temporária,
  sem alterar o executável ou saves do usuário.
- `play.html` carregou com `ruffle-embed` real, metadata `760×600`,
  `30 fps`, SWF 10, AS3, 1 quadro do SWLoader.
- Rede comprovou carregamento do `SWLoader.swf`, `Basesec_1.5.4.swf`,
  e requisições para config, jogador e recursos adicionais.
- Marcador de UI na página do jogo: `observer_ready`, `begin_action`
  e `end_action` (tipo **other**, meramente sintético, sem ação do jogo);
  capturas PNG do começo/fim e final armazenadas em
  [artefato 12213468689](https://github.com/Acccelll/Social_wars_test/actions/runs/39306732074/artifacts/12213468689).
- Dos **14 SWFs** com 17 GIFs do catálogo, foram requisitados no
  boot **2 SWFs** (torre `0022_tower_1_m`, centro de comando
  `0026_command_center_1_m`) vinculados a **3 linhas de sprites**.
  **Nenhum dos 3 sprites teve sua execução individual comprovada**.
- [Matriz permanente](../data/visual/runtime_boot_presence_5d8.json)
  documenta as 17 linhas e diferencia requisição de ação efetiva.
- Estados de ataque/deslocamento/dano/destruição ainda **0 confirmados**.

## Lote 5D.8B — Vídeo e auditoria visual do cliente original

- [Execução 39310113510](https://github.com/Acccelll/Social_wars_test/actions/runs/39310113510)
  **success**; original Flask + Chromium/Ruffle + vila descartável.
- Em um intervalo de teste rotulado `other`, foi executado um clique
  real no `ruffle-embed`, com capturas antes/depois.
- O comparador detectou **uma mudança visual** na região do Flash.
- `session.webm` produzido com **2.521.901 bytes**.
- Arquivos `action_evidence_5d8b.json`, `report.json`, PNGs e vídeo
  estão no [artefato 12215307646](https://github.com/Acccelll/Social_wars_test/actions/runs/39310113510/artifacts/12215307646).
- **0 ações específicas e 0 sprite IDs identificados**.
  O CI prova interação de ponteiro e variação visual, não movimento/ataque.
- Script `tools/analyze_runtime_5d8b.py` e testes sintéticos persistidos;
  [instruções do lote](LOTE_5D_8B.md) disponíveis para registrar ações reais.

## Lote 5D.8C — Três tipos de unidades no cliente original

- [Execução final 39313160511](https://github.com/Acccelll/Social_wars_test/actions/runs/39313160511):
  **success**, testes de seed e de screenshots aprovados.
- A distribuição 0.02a foi iniciada em **cópia isolada**, com quatro unidades
  no template da vila (Splinter Mech ×2, Bushwacker e Reaper Drone).
- O cliente Ruffle requisitou os três SWFs
  `1313_splinterMech.swf`, `1358_bushwacker.swf` e
  `1376_reaperDrone.swf`.
- Foram gerados vídeo, 3 pares de capturas, 3 sondagens e
  **3 diferenças visuais**.
- **Nenhuma** ação de combate/deslocamento foi comprovada; nenhum ID
  interno de animação foi associado ao gameplay. Clique e carregamento
  de SWF não demonstram execução de ação.
- [Resumo permanente](../data/visual/original_unit_probe_5d8c.json);
  [vídeo/capturas/manifesto](https://github.com/Acccelll/Social_wars_test/actions/runs/39313160511/artifacts/12217206551).
- [Procedimento e limites técnicos](LOTE_5D_8C.md).

## 5D.8D — Bloqueio da missão inicial no jogo original

- A inspeção das imagens reais do 5D.8C encontrou
  `RESCUE YOUR COMRADE!` cobrindo todo o centro do mapa.
- O primeiro clique de teste a 1090px
  ([39315571893](https://github.com/Acccelll/Social_wars_test/actions/runs/39315571893))
  não fechou a janela.
- Na resolução nativa 760×600, a CI
  [39316722288](https://github.com/Acccelll/Social_wars_test/actions/runs/39316722288)
  terminou **success para o diagnóstico**. A área do diálogo
  não mudou após clique ou Enter.
- Hit-test `RUFFLE-EMBED` → `CANVAS` com pointer-events auto:
  o navegador entrega eventos ao player, porém a ação do botão
  não foi comprovada.
- [Registro permanente](../data/visual/intro_diagnostic_5d8d.json)
  e [evidências visuais](https://github.com/Acccelll/Social_wars_test/actions/runs/39316722288/artifacts/12219005558).
- **Nenhuma animação de movimento/ataque e nenhum character_id
  foram validados.**

## Lote 5D.8E — Movimento real no servidor original

- [Workflow aprovado 39318650244](https://github.com/Acccelll/Social_wars_test/actions/runs/39318650244), 6 testes Python concluídos.
- Via endpoint original command.php, Splinter Mech (item 1313; índice 41) movido de **(52,45) para (53,46)**.
- O save temporário foi reaberto; **1 de 44 itens** do mapa mudou, com identidade/dono intactos.
- O SWF principal contém 2 referências à frase Rescue Your Comrade e 48 ao termo tutorial, mas a rotina responsável pelo OK permanece não identificada.
- [Prova persistida](../data/visual/original_move_proof_5d8e.json) e [strings da missão](../data/visual/original_intro_text_5d8e.json).
- **0 animações Ruffle e 0 IDs internos de sprite confirmados.**
- Nenhum arquivo de jogo ou save do computador do usuário foi alterado.

## Lote 5D.8F — Janela inicial liberada no Ruffle

- [FFDec 39320622043](https://github.com/Acccelll/Social_wars_test/actions/runs/39320622043)
  decompilou em cópia temporária **11 classes AS3** do cliente original, incluindo
  \`popups.PopupMissionInfo\`, \`popups.PopupTutorial\`,
  \`popups.PopupIntro\`, \`managers.PopupManager\` e \`core.TutorialMain\`.
- \`PopupMissionInfo\` registra \`btnOk.addEventListener(MouseEvent.MOUSE_UP, closeWindow)\`;
  \`closeWindow()\` emite \`Event.CLOSE\`, recebido pelo \`PopupManager\`.
- O [ensaio 39321595058](https://github.com/Acccelll/Social_wars_test/actions/runs/39321595058)
  confirmou que o primeiro clique dispensou uma camada de aviso de
  aceleração de hardware do Ruffle, mas manteve a missão.
- **Um segundo clique no OK fechou efetivamente a janela**: a captura
  mostrou o mapa, mechas e HUD visíveis; mudança na região
  do diálogo **~89,87%** em relação ao quadro anterior.
- [Capturas/vídeo originais do Ruffle](https://github.com/Acccelll/Social_wars_test/actions/runs/39321595058/artifacts/12220326999);
  [índice AS3](../data/visual/tutorial_as3_index_5d8f.json).
- Isso resolve **o bloqueio de entrada nos testes**, não confirma
  movimento ou ataque de unidades nem identificação do DefineSprite.
- O SWF e os salvamentos do usuário permanecem intocados.


## Lote 5D.8G — Movimento nativo pelo cliente Flash comprovado

- [GitHub Actions 39329666474](https://github.com/Acccelll/Social_wars_test/actions/runs/39329666474) finalizado com sucesso.
- Chromium/Ruffle fechou o modal e, após 3 pares de cliques na interface original, o próprio navegador enviou **1 comando `move`** para `command.php`.
- Objeto índice **42**, item **1358 (Bushwacker)**: save da vila isolada alterado de **(55,45)** para **(52,41)**, sem alterar outros objetos do mapa.
- Inspeção do vídeo mostra deslocamento visual de unidade, mas o painel exibe **REAPER DRONE**, e a associação com o índice 42/Bushwacker ou com um `DefineSprite` específico **não foi comprovada**.
- Não foram feitos POSTs de movimento pelo teste; capturados somente campos minimizados da requisição.
- [Relatório permanente](../data/visual/original_client_move_5d8g.json) · [Doc e limites](LOTE_5D_8G.md) · [Vídeo e capturas](https://github.com/Acccelll/Social_wars_test/actions/runs/39329666474/artifacts/12224430675).
- **Próximo: 5D.8H**, isolamento e identificação inequívoca da entidade animada por índice de mapa antes do estado de ataque.


## Lote 5D.8H — Identidade das três unidades e movimento original isolado

- [CI 39347814190](https://github.com/Acccelll/Social_wars_test/actions/runs/39347814190) concluído com sucesso; três cenários descartáveis com **uma única unidade adicional cada**, usando o SWF original não modificado.
- Bushwacker **1358**, objeto **41**: `(55,45)` → `(54,35)`, **2 movimentos nativos**.
- Reaper Drone **1376**, objeto **41**: `(55,45)` → `(58,40)`, **1 movimento nativo**.
- Splinter Mech **1313**, objeto **41**: `(55,45)` → `(55,39)`, **2 movimentos nativos**.
- Os nomes **BUSHWACKER**, **REAPER DRONE** e **SPLINTER MECH** coincidem com os painéis da interface em capturas isoladas, corrigindo a ambiguidade do 5D.8G.
- Correspondência entre ação do cliente original, índice, item e save confirmada nos três casos. **DefineSprite SWF e frames de animação ainda não identificados**.
- [Relatório](LOTE_5D_8H.md) · [Dados](../data/visual/isolated_original_units_5d8h.json) · [Evidências/vídeos](https://github.com/Acccelll/Social_wars_test/actions/runs/39347814190/artifacts/12232061894).
- **Próximo lote 5D.8I:** começar a investigar ataques e dano por eventos emitidos pelo próprio cliente.


## Lote 5D.8I — Seleção original confirmada; combate ainda pendente

- Cenário original Bushwacker **1358** (jogador, índice 41) × Reaper Drone **1376** (oponente, índice 42).
- Três rodadas de testes no Chromium/Ruffle com saves separados: [leste](https://github.com/Acccelll/Social_wars_test/actions/runs/39349462830), [norte/oeste](https://github.com/Acccelll/Social_wars_test/actions/runs/39349850417) e [cliques calibrados](https://github.com/Acccelll/Social_wars_test/actions/runs/39350441517).
- O clique na unidade aliada abre painel **BUSHWACKER 6500/6500**; o clique seguinte no oponente abre **REAPER DRONE 700/700** — **seleção/inspeção, não dano**.
- **Não foram observados** `kill`, `sell`, `end_attack`, redução de HP persistida ou remoção do alvo. `batch_remove` da inicialização não é evidência de combate.
- Testes CI verdes demonstram execução do experimento, **não** sucesso de ataque.
- [Relatório 5D.8I](LOTE_5D_8I.md) · [dados de evidência](../data/visual/native_combat_observation_5d8i.json).
- **Próximo: 5D.8J:** estudar UI/estado de batalha e ativação de ataque a partir de ActionScript e cenas, antes de novos testes de clique.


## Lote 5D.8J — Combate nativo e eliminação confirmados

- Corrigida a confusão do 5D.8I: no **SWF original**, `PLAYER_ENEMY=2` e `PLAYER_NEUTRAL=3`. Os experimentos anteriores haviam tratado um Reaper Drone **neutro** como inimigo.
- Decompiladas **15 classes originais** relacionadas a clique, UI, IA e dano (FFDec 26.3.0; binário SHA-256 validado): [CI 39352875836](https://github.com/Acccelll/Social_wars_test/actions/runs/39352875836).
- Confirmada rota original `IsoInteractiveElement.clickItem → Base.startMovements → IsoUnit.setMove → updateAttack → attackNormal → recibirAtaque`.
- Cenário corrigido: Bushwacker **1358/41/PlayerID=1** × Reaper Drone **1376/42/PlayerID=2**.
- [CI de combate 39353157986](https://github.com/Acccelll/Social_wars_test/actions/runs/39353157986) comprovou **`kill` nativo do objeto 42**, remoção do save original e efeitos visuais de disparo/experiência. **SWF não modificado; sem POSTs artificiais.**
- O teste é da distribuição original no Ruffle, **não** do cliente AS3 recompilado.
- [Relatório detalhado](LOTE_5D_8J.md) · [Dados persistentes](../data/visual/original_combat_proof_5d8j.json) · [Vídeo e capturas](https://github.com/Acccelll/Social_wars_test/actions/runs/39353157986/artifacts/12233034780).
- **Próximo: 5D.8K**, correlacionar estados/frames de tiro com os SWFs de Bushwacker e Reaper Drone.


## Lote 5D.8K — GIFs e estados originais de combate (Bushwacker / Reaper Drone)

- [CI de inventário 39355691232](https://github.com/Acccelll/Social_wars_test/actions/runs/39355691232): identificados sem ambiguidade `assets/sprites/1358_bushwacker.swf` (258 símbolos internos) e `assets/sprites/1376_reaperDrone.swf` (554 símbolos), com hashes originais verificados.
- **Bushwacker:** timeline principal `DefineSprite=1092`; **Reaper Drone:** `DefineSprite=1654`. Ambos com `FrameLabel` originais `QUIETO` frame 1, `ANDAR` frame 6, `ATAQUE` frame 11 e `MUERTE` frame 16.
- **Ataques direcionais Bushwacker:** frame 11→sprite `643` (`E_attack`), 12→`675` (`TE_attack`), 13→`716` (`P_attack`), 14→`752` (`T_attack`), 15→`786` (`F_attack`).
- [CI de estados 39355945927](https://github.com/Acccelll/Social_wars_test/actions/runs/39355945927): **9 GIFs** das timelines rotuladas exportados e disponíveis em [artefato](https://github.com/Acccelll/Social_wars_test/actions/runs/39355945927/artifacts/12235636024).
- Limites: os GIFs `QUIETO/ANDAR/ATAQUE` do Reaper ficaram idênticos nesta exportação; não foi comprovada a identidade do projétil, impacto ou quadros específicos da captura runtime.
- [Relatório 5D.8K](LOTE_5D_8K.md) · [metadados versionados](../data/visual/combat_animations_5d8k.json).
- **Próximo 5D.8L:** detalhar os cinco ataques direcionais e correlacionar efeitos visuais à execução original do Ruffle, sem editar SWFs.
