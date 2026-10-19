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
