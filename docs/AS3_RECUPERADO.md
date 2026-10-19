# Código AS3 recuperado — instruções para manutenção

## O que está em `as3/src`

Uma **porta experimental independente** de A* (não um cliente Social Wars completo):

- `IsoNodeRecovered.as`: nó `f,g,h,parentNode,xPos,yPos,terrain,occupied`.
- `NodesPathRecovered.as`: `flash.utils.Proxy`, array interno, índice `route[0]`, `isAI`.
- `AStarRecovered.as`: busca/terrenos/cantos, g literal, tempo limite e interface de rota.
- `IsoUnitRouteBridge.as`: imita parte do fluxo de atribuição do caminho.
- `AS3Probe.as`: prova experimental **compilada e executada** no Ruffle com 8/8 verificações runtime aprovadas, via ExternalInterface.

**Não renomear** os tipos para os originais e injetar no SWF sem teste. `IsoUnit.aNodes` exige o tipo nominal original `com.socialpoint.astar.NodesPath`.

## Fidelidade conhecida

- `AStar.CANCEL_TIME = 50` e buscas encerradas por temporização.
- `AStar.Sort()` usa `Array.sortOn("f", Array.NUMERIC)`.
- Custo `g` observado: `Boolean(current.g + Number(diagonal)) ? 14 : 10`, NÃO a soma convencional.
- `h = 10 * (abs(destX-x) + abs(destY-y))`; `f = g + h`.
- Na atualização de nó aberto, o AVM2 não recalcula `f` imediatamente.
- `ResolvePath` tem partes de confiança média.
- Rota de voo delegada a `getLinePath` no jogo original; a porta usa um callback externo.
- Os IDs dos terrenos dependem das constantes do cliente; esta porta não os presume.
- `paintedNodes` pode ser configurado externamente; ausência usa atalho de desenvolvimento.

## Teste e compilação

```bash
python tools/test_astar_cost.py
bash tools/build_probe_linux.sh
```

No Windows, usar `tools\build_probe_windows.bat`.

Os testes Python apenas exercitam a fórmula. A compilação `mxmlc` e a execução real do `AS3Probe.swf` no Ruffle foram aprovadas na execução CI [39260961090](https://github.com/Acccelll/Social_wars_test/actions/runs/39260961090); a validação é restrita ao protótipo.

## Próximo passo técnico

Fazer testes de equivalência contra o caminho original e produzir um adaptador de tipo nominal `com.socialpoint.astar.NodesPath` / `core.isoengine.IsoUnit`. A prova de execução isolada já foi concluída.
