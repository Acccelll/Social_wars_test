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
| 5B | Executar `AS3Probe` no Ruffle, testar a rota e registrar resultados | **Próximo** |
| 5C | Comparar caminhos reais, colisões e IA com cliente SWF | Pendente |
| 5D | Empacotar SWF modificado usando o servidor existente | Pendente |
| 6A | Replanejar evolução de mecânicas e interface | Futuro |

## Regras de trabalho

- Trabalhar em lotes pequenos e entregar código/documentação diretamente neste repo.
- Preservar a distribuição e os saves originais em diretório separado.
- Distinguir **P-code**, **AS3 reconstruído**, **equivalência em modelo** e **execução real**.
- Não declarar "recompilável" antes de um `mxmlc` bem-sucedido.
- Documentar os resultados dos testes com entradas, saídas e ferramentas.
- Preferir evoluir a árvore `as3/src/` ao invés de gerar ZIPs desconectados.
