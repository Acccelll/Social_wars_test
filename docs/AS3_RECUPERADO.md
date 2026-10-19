# Código AS3 recuperado — instruções para manutenção

## O que está em `as3/src`

Uma **porta experimental independente** de A* (não um cliente Social Wars completo):

- `IsoNodeRecovered.as`: nó `f,g,h,parentNode,xPos,yPos,terrain,occupied`.
- `NodesPathRecovered.as`: `flash.utils.Proxy`, array interno, índice `route[0]`, `isAI`.
- `AStarRecovered.as`: busca/terrenos/cantos, g literal, tempo limite e interface de rota.
- `IsoUnitRouteBridge.as`: imita parte do fluxo de atribuição do caminho.
- `AS3Probe.as`: demonstração mínima compilável **ainda não validada**.

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

Os testes Python apenas exercitam a fórmula; `mxmlc` e a execução real do SWF continuam necessários.

## Próximo passo técnico

Obter Flex SDK/compilador, compilar `AS3Probe.as`, executar o SWF de prova, corrigir erro por erro e só depois criar um adaptador tipado para `IsoUnit` original.
