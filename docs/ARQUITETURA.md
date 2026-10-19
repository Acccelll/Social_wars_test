# Arquitetura e pontos de integração

```text
social-warriors.exe                  [distribuição original — fora do Git]
    └── servidor local HTTP :5055
        ├── páginas / API do jogo
        └── SWF ActionScript 3
             ├── core.isoengine.IsoUnit
             │    ├── setMove(...) -> Base.Main.objAstar.findPath(...)
             │    ├── aNodes = objAstar.walkPath
             │    └── updateMove() -> aNodes[0], TileToPixel, splice
             ├── com.socialpoint.astar.AStar
             │    └── NodesPath : flash.utils.Proxy
             └── core.isoengine.IsoFightingElement
                  └── recibirAtaque / calculateDamage
```

## Cliente e métodos identificados

| Método | ABC method ID | Bytecode |
|---|---:|---:|
| `AStar.findPath` | 558 | 685 bytes |
| `AStar.look` | 553 | 449 bytes |
| `AStar.searchNode` | 555 | 837 bytes |
| `AStar.isWalkable` | 551 | 256 bytes |
| `AStar.Sort` | 554 | 32 bytes |
| `IsoUnit.setMove` | 1723 | 1.623 bytes |
| `IsoUnit.updateMove` | 1716 | 1.727 bytes |
| `IsoUnit.IA_Move` | 1741 | 331 bytes |
| `IsoUnit.aNodes` (setter) | 1788 | 54 bytes |
| `IsoFightingElement.calculateDamage` | 1492 | 198 bytes |
| `IsoFightingElement.recibirAtaque` | 1499 | 1.860 bytes |

## Contrato de movimentação

- `AStar.findPath` prepara a rota, que fica disponível por `walkPath:NodesPath`.
- `IsoUnit.aNodes` usa como **tipo nominal** `com.socialpoint.astar.NodesPath`. Não aceita automaticamente `recovered.NodesPathRecovered`.
- O setter `aNodes` chama `delegate.onMoveStart(route.isAI)` quando a rota contém pontos.
- `IA_Move` marca `walkPath.isAI = true` antes de atribuir a rota.
- `setMove` recebe caminho, lê `aNodes[0].x/y`, converte o tile para pixel, retira o primeiro ponto e trata o destino conforme o ramo.
- `updateMove` usa `uiSpeed`, transições de tile, eventos e estado de chegada.
- `NodesPath` herda `flash.utils.Proxy` e delega indexação ao Array interno.

## Particularidade comprovada do A* original

Trechos alcançáveis de `searchNode` fazem, em notação equivalente:

```actionscript
var g:Number = Boolean(current.g + Number(diagonal)) ? 14 : 10;
```

Isso é **diferente** de `current.g + (diagonal ? 14 : 10)`. O ramo de atualização também altera `g` e `parentNode` sem atualizar imediatamente `f`. Mantenha a semântica literal separada de uma versão normalizada.

## Limite de integração

Os arquivos em `as3/recovered` compõem uma porta isolada para investigação. Eles não substituem diretamente as classes do SWF original. Uma troca exige compilar, manter contratos de tipo, confrontar execução e preservar servidor/protocolo/salvamentos.
