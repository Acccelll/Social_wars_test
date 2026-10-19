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
