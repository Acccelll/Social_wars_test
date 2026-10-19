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
| 5D.3 | Exportação incremental dos 1.117 SWFs restantes, iniciando por cinco unidades | **Em processamento; ainda não é extração integral** |
| 5D.4 | Exportação de timelines completas e atlas de animação | Pendente |
| 5D.5 | Catalogar recursos por unidade, edifício e UI, com prévias | Pendente |
