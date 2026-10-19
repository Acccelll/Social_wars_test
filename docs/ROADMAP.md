# Roadmap de continuidade

## Objetivo final

Um projeto Social Wars editável, compilável e jogável, usando a distribuição já funcional como referência. Não confundir isso com reimplementar completamente em HTML5 — esse é um caminho separado.

| Lote | Meta | Estado |
|---|---|---|
| 3C | Extração integral de P-code AVM2 | Histórico concluído |
| 3D | Fragmentos AS3 de combate/IA | Histórico concluído |
| 3E | Levantamento do A* e `recibirAtaque` | Histórico concluído |
| 3F | Tradução de `findPath`, `look`, `searchNode` | Histórico parcial |
| 3G | Verificar regra de custo `g` | Histórico concluído no modelo |
| 3H | Adaptar `NodesPath` e `IsoUnit` | Protótipo + testes estáticos |
| 3I | Contrato `aNodes.isAI` e delegados | Protótipo + teste modelado |
| 4A | Rodar a distribuição original com Ruffle | Confirmado pelo usuário |
| 4B | Inicializador com Ruffle próprio | Planejado; não validado |
| 5A | Estrutura AS3 e compilação automatizada do AS3Probe | **Concluído (build CI aprovado)** |
| 5B | Executar `AS3Probe` no Ruffle, testar a rota e registrar resultados | **Concluído (8/8 runtime AS3, via ExternalInterface)** |
| 5C.1 | Harness isolado de contratos `IsoUnit`/`NodesPath` com dois SWFs testados | **Concluído (8/8 + 15/15 Ruffle)** |
| 5C.2 | Comparar trajetórias, colisões e IA com o SWF **original** | **Próximo; pendente instrumentação original** |
| 5E | Empacotar SWF modificado usando o servidor existente (frente de código) | Pendente |
| 6A | Replanejar evolução de mecânicas e interface | Futuro |

## Regras de trabalho

- Trabalhar em lotes pequenos e entregar código/documentação diretamente neste repo.
- Preservar a distribuição e os saves originais em diretório separado.
- Distinguir **P-code**, **AS3 reconstruído**, **equivalência em modelo** e **execução real**.
- Não declarar "recompilável" antes de um `mxmlc` bem-sucedido.
- Documentar os resultados dos testes com entradas, saídas e ferramentas.
- Preferir evoluir a árvore `as3/src/` ao invés de gerar ZIPs desconectados.

## Extração dos recursos gráficos

| Lote | Meta | Estado |
|---|---|---|
| 5D.1 | Inventário de todos os arquivos gráficos/SWFs e hash do cliente | **Concluído, 0 erros em 1.118 SWFs** |
| 5D.2 | Exportação de bitmaps e recursos do SWF principal, mais imagens externas | **Concluído: 1.899 externas e 7.493 exportações do cliente** |
| 5D.3 | 5 mechas (visual), 26 personagens e 12 construções (bitmaps) | **44/1.118 SWFs cobertos; exportação integral pendente** |
| 5D.4 | Extração estrutural das timelines, quadros e relações de sprite | **Concluído (1.118 SWFs); 2 advertências em PlaceObject** |
| 5D.4B | Prévias GIF em amostra; comparação com reprodução real do jogo | **Prévia inicial concluída; comparação runtime pendente** |
| 5D.4C | Atlas e animações editáveis para substituições | Pendente |
| 5D.5 | Primeira galeria GIF e catálogo offline de 5 SWFs | **Primeira amostra: 8/8 GIFs; catálogo integral ainda pendente** |
