# Social Wars Test

Projeto de preservação técnica, estudo e evolução do **Social Wars 0.02a**.

> **Estado atual:** o jogo original está funcionando localmente no Windows, com servidor na porta `5055` e execução confirmada pelo usuário no navegador com Ruffle. **Ainda não reconstruímos nem recompilamos o cliente completo.**

## Objetivo

Consolidar em um único repositório o conhecimento e os protótipos obtidos a partir do cliente `Basesec_1.5.4.swf`, e evoluir gradualmente até uma versão editável, compilável e testável.

### O que já foi obtido

- Execução da distribuição `social-warriors_0.02a` com servidor local.
- Extração/análise do bytecode AVM2 do cliente.
- Reconstrução parcial dos métodos de dano, inteligência artificial e movimentação.
- Port experimental do algoritmo A* em ActionScript 3, com verificação específica da regra de custo `g`.
- Adaptação experimental do contrato `NodesPath` / `IsoUnit`.
- Pipeline reproduzível que compilou e executou **dois SWFs experimentais** em Ruffle/Chromium: **8/8 testes A*** e **15/15 testes de contratos NodesPath/IsoUnit** (Lote 5C).

Leia [STATUS.md](docs/STATUS.md), [ARQUITETURA.md](docs/ARQUITETURA.md) e [ROADMAP.md](docs/ROADMAP.md).

## Estrutura

| Diretório | Conteúdo |
|---|---|
| `as3/src/com/socialpoint/astar/recovered/` | Reconstituições experimentais em ActionScript 3 |
| `as3/contract_harness/` | Doubles isolados de contratos com nomes originais (NÃO integrar ao jogo real) |
| `tools/` | Scripts de verificação e compilação |
| `tests/ruffle/` | Teste de execução do SWF experimental em Chromium/Ruffle, com relatório e captura de tela |
| `tools/visual_inventory.py` | Inventário automatizado dos recursos de TODOS os SWFs do jogo |
| `tools/visual_extract.py` | Exportação em lotes para arquivos PNG e SVG via JPEXS FFDec |
| `docs/` | Resultados dos lotes, limitações, roteiro de continuidade |

## Executar o jogo original

A distribuição original, necessária à execução, **não está incluída neste repositório**.

1. Obtenha a versão `0.02a` do projeto de preservação [Social Warriors](https://github.com/AcidCaos/socialwarriors).
2. Extraia localmente e execute `social-warriors.exe`.
3. Abra `http://127.0.0.1:5055/`; se necessário, use [Ruffle](https://ruffle.rs/).
4. **Preserve e faça backup da pasta `saves/` antes de qualquer teste.**

Ver [EXECUCAO.md](docs/EXECUCAO.md).

## Integridade da fonte analisada

- SWF original: `assets/flash/Basesec_1.5.4.swf`
- SHA-256: `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`
- Os números de método e instruções nos relatórios referem-se a **esse SWF**, não necessariamente a outras versões.

## Limites e propriedade intelectual

Este repositório **não inclui** o jogo, o servidor original, recursos gráficos/áudio, salvamentos ou binários de terceiros. Disponibiliza apenas documentação e código experimental de análise/portabilidade; isso não implica autorização para redistribuir os ativos do jogo. Não há declaração de equivalência ou compatibilidade integral.

## Próximo passo

**Lote 5C.1 concluído:** o workflow [39262967632](https://github.com/Acccelll/Social_wars_test/actions/runs/39262967632) compilou e executou dois SWFs experimentais com **23/23 verificações aprovadas**. Veja [LOTE_5C.md](docs/LOTE_5C.md) e [MATRIZ_COMPATIBILIDADE_5C.md](docs/MATRIZ_COMPATIBILIDADE_5C.md). **Próximo lote 5C.2:** comparação de saídas com o cliente original. O jogo completo ainda não foi recompilado.

## Recursos visuais (Lote 5D)

O [inventário completo](docs/LOTE_5D.md) da distribuição oficial 0.02a percorreu **1.118 SWFs** e **1.899 imagens externas**. Foram localizadas **41.069 definições de bitmaps**, **62.318 formas vetoriais** e **43.426 sprites**, além de morphshapes e botões. Essas definições **ainda não representam PNGs exportados**. Use o exportador local por lotes para preservar recursos fora do repositório público.

GitHub Actions: [inventário de 0.02a](https://github.com/Acccelll/Social_wars_test/actions/runs/39277345729).

## Exportação visual verificada

Em 19/10/2026, o [GitHub Actions 39277803644](https://github.com/Acccelll/Social_wars_test/actions/runs/39277803644) exportou **369 bitmaps** de `Basesec_1.5.4.swf`, sem erros, usando JPEXS FFDec 26.3.0. Essa é uma extração real em PNG/JPEG (não apenas contagem de tags). Os recursos **não foram commitados**; pacote disponível temporariamente na página da execução. A exportação das demais imagens e animações continua em lotes.

### Lote 5D.3 — Exportações e catálogo

Os workflows já concluídos exportaram **1.899 imagens externas** (143 PNG, 1.756 JPG) e **7.493 arquivos visuais do SWF principal** em uma segunda execução FFDec. O próximo lote separa cinco SWFs de unidades e cria uma tabela geral de identificação de arquivos, sem guardar os recursos na branch main.

- [Unidades: lote selecionado](https://github.com/Acccelll/Social_wars_test/actions/runs/39292249010)
- [Relatório do 5D.3](docs/LOTE_5D_3.md)
- [Gerador de catálogo dos arquivos exportados](tools/visual_asset_manifest.py)

Os pacotes de recursos são artefatos temporários do Actions (a expirar), por isso a exportação local com `tools/EXTRAIR_IMAGENS_WINDOWS.bat` permanece como alternativa durável.

### Cobertura da extração (revisada)

Os trabalhos já verificados cobrem **44 dos 1.118 SWFs**:
1 cliente principal (7.493 saídas PNG/SVG), 5 mechas (14.436
saídas PNG/SVG), os 26 SWFs de `characters_2` (61 bitmaps)
e 12 construções (116 bitmaps). Em paralelo, foram copiadas
**1.899 imagens externas** (PNG/JPG).

**Atenção:** os 38 arquivos de personagens e edifícios foram processados
apenas em modo bitmap; as formas vetoriais e animações continuam pendentes.
O índice permanente está em [data/visual/export_coverage.csv](data/visual/export_coverage.csv).
Os SWFs e suas imagens não são incluídos no repositório público.

## Recuperação das animações — 5D.4

O [inventário de timelines](docs/LOTE_5D_4.md) analisou os
**1.118 SWFs**, totalizando **43.426 sprites**, **400.023 quadros**
e **2.782.788 eventos de posicionamento**. Foram registrados
quadros, relações de dependência entre sprites, identidades e
transformações presentes nos tags Flash. O conjunto ainda não
corresponde à reprodução completa de animações em runtime.

A extração de timelines já está **registrada permanentemente** em
[data/visual/timeline_inventory.csv](data/visual/timeline_inventory.csv)
e nos [seis exemplos detalhados](data/visual/timeline_details), sem
necessidade de baixar artefatos temporários para consultar os metadados.

## Primeira galeria de prévias animadas — 5D.5

O [Lote 5D.5](docs/LOTE_5D_5.md) compilou uma galeria HTML offline
com **8 GIFs animados** de cinco SWFs (Tetrapod, Splinter,
torre, centro de comando e personagem good_10_m), usando os
identificadores reais de sprites recuperados.

[Baixe o pacote de prévias e abra index.html](https://github.com/Acccelll/Social_wars_test/actions/runs/39301011532/artifacts/12211297019).
As imagens permanecem fora do repositório; os metadados são preservados
em data/visual. A cobertura integral dos recursos animados está pendente.

## Biblioteca visual categorizada — Lote 5D.6

O [workflow 39303077044](https://github.com/Acccelll/Social_wars_test/actions/runs/39303077044)
gerou uma galeria **HTML offline com filtros e busca** contendo **17 GIFs
animados de 14 SWFs**: 8 prévias de unidades, 6 de construções e 3 de
interface/telas. A execução terminou com **0 erros**.

[Baixar a galeria HTML + GIFs](https://github.com/Acccelll/Social_wars_test/actions/runs/39303077044/artifacts/12212183676)
(artefato temporário) ou consultar o
[catálogo de metadados versionado](data/visual/gallery_5d6.csv).

Ainda não existe biblioteca completa de sprites editáveis nem paridade
com estados dinâmicos da animação original.

## Auditoria de animações — 5D.7

A [auditoria de 17 GIFs](docs/LOTE_5D_7.md) encontrou **um par de
arquivos exatamente duplicados** (Torre #52 e Oficina #52).
A checagem por nomes de símbolos, rótulos e instâncias **não**
permitiu identificar com segurança espera, movimento, ataque,
dano, destruição ou construção em nenhuma das 17 prévias.
Por isso, todas continuam marcadas para verificação no jogo.

[Relatório técnico por sprite](data/visual/animation_review_5d7.json) ·
[Fila de 17 estados a validar](data/visual/animation_review_5d7_queue.csv) ·
[Galeria de revisão GIF](https://github.com/Acccelll/Social_wars_test/actions/runs/39304404150/artifacts/12212991791).

## Cliente original no Ruffle — Lote 5D.8A

O [workflow 39306732074](https://github.com/Acccelll/Social_wars_test/actions/runs/39306732074)
executou o **servidor Flask oficial** com uma vila descartável e carregou
`SWLoader.swf` no `ruffle-embed` de Chromium (SWF 10, AVM2/AS3, 760×600,
30 fps). As requisições confirmaram o carregamento do `Basesec_1.5.4.swf`,
fontes, efeitos, terreno e construções, além dos endpoints de config e jogador.

O painel separado `tests/original/observer.js` registra rótulos manuais,
cliques e capturas ao iniciar/finalizar uma ação, mas **não identifica
MovieClips/IDs internos automaticamente**. A [matriz de
presença na inicialização](data/visual/runtime_boot_presence_5d8.csv)
confirma apenas quais recursos SWF foram requisitados, não se as ações
das animações foram executadas. Veja [LOTE_5D_8.md](docs/LOTE_5D_8.md).

## Captura do cliente original (5D.8B)

O [lote 5D.8B](docs/LOTE_5D_8B.md) grava vídeo WebM e capturas do
Social Wars 0.02a no Ruffle. O teste automatizado confirmou alteração
visual após um clique no Flash. Ainda **não** confirmou uma animação de
movimento, ataque ou dano nem sua associação ao ID interno do sprite.

[Ver vídeo, capturas e relatório do lote](https://github.com/Acccelll/Social_wars_test/actions/runs/39310113510/artifacts/12215307646).
