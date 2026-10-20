# Social Wars — Lote 5D.8X: orientação original e origem do disparo

**Estado:** orientação original identificada no ActionScript e integrada ao motor TypeScript; marcadores dos dois sprites originais escaneados diretamente do SWF 0.02a, sem modificá-lo. A apresentação do Reaper na arena agora usa automaticamente a direção lógica, cinco poses e espelhamento; o modo manual do 5D.8W permanece para inspeção.

## 1. Mapeamento preciso do código original

As constantes de `core.Constants` decompiladas do arquivo original são:

| Nome lógico | Valor | Quadro dentro do grupo | `scaleX` |
|---|---:|---:|---:|
| `ORIENTATION_UP` | 1 | 1 | +1 |
| `ORIENTATION_UP_RIGHT` | 2 | 2 | +1 |
| `ORIENTATION_RIGHT` | 3 | 3 | +1 |
| `ORIENTATION_DOWN_RIGHT` | 4 | 4 | +1 |
| `ORIENTATION_DOWN` | 5 | 5 | +1 |
| `ORIENTATION_UP_LEFT` | 6 | 2 | −1 |
| `ORIENTATION_LEFT` | 7 | 3 | −1 |
| `ORIENTATION_DOWN_LEFT` | 8 | 4 | −1 |

`core.isoengine.IsoUnit.updateAnimation()` contém a regra:

```actionscript
frameDirection = this.currentDirection;
if (this.currentDirection > 5) {
    frameDirection -= 4;
    newScale = -1;
}
frame = this.iAnimation * 5 + frameDirection;
this.ghostBuilding.gotoAndStop(frame);
this.ghostBuilding.scaleX = newScale;
```

As animações raiz conhecidas usam `iAnimation = 0` (QUIETO), `1` (ANDAR), `2` (ATAQUE), `3` (MUERTE). Os seus respectivos frames raiz são 1–5, 6–10, 11–15, 16–20.

`IsoUnit.updateUnitDirectionTilePixel()` escolhe direção por comparação de **coordenadas de pixels do mapa** (`param1-x` e `param2-y`) e preserva direção anterior quando ambos os deslocamentos são inferiores a **um terço da largura/altura do tile em pixels**. `updateDirection()` pode usar `updateUnitDirectionTile(target.tx,target.ty)` quando a unidade está atacando, após a conversão original `Utils.TileToPixel()`.

**Distinção:** reproduzimos fielmente a lógica de **8 direções para 5 poses + espelhamento**, mas na cena própria 2D as posições atuais não passam pelo mapa isométrico completo `Utils.TileToPixel`; não afirmar paridade espacial fora da cena plana.

## 2. Marcadores `projectilePoint`: verificação nos binários

A função original `IsoFightingElement.getProjectilePoint("projectilePoint")`:

1. Procura `DisplayObjectContainer(bmd.getChildAt(0)).getChildByName(clipName)` como `MovieClip`.
2. Se existir, converte o ponto local da instância para global (`localToGlobal`) e volta ao espaço do parent (`parent.globalToLocal`).
3. Se não existir, retorna `(x, y - bmd.height * 0.6)`; se `bmd` também for nulo, `(x,y)`.

O `getHitPoint` é uma função **separada**: procura marcador diretamente no `ghostBuilding`; na ausência, usa o retângulo do alvo (`getBounds(this)`) e `ProjectileDefinition.verticalOffset`.

O novo [scanner binário 5D.8X](../tools/projectile_markers_5d8x.py) descompacta sem editar os dois SWFs, lê suas tags `PlaceObject/PlaceObject2/PlaceObject3` e enumera nomes de instâncias e matrizes.

| Unidade | Eventos com nomes correspondentes | Resultado |
|---|---:|---|
| Bushwacker 1358 | **26** | Marcador `projectilePoint` e `projectilePoint01` a `projectilePoint16`, em várias sub-timelines; cinco marcadores nas poses principais de ataque |
| Reaper Drone 1376 | **0** | Nenhum `projectilePoint` (ou variante semelhante) nomeado nas instâncias analisadas |

Os principais marcadores do Bushwacker (em **twips locais**, 20 twips = 1 pixel) incluem:

| DefineSprite da pose | Frame da sua timeline | `tx` twips | `ty` twips |
|---:|---:|---:|---:|
| 643 | 11 | −2.150 | −7.903 |
| 675 | 11 | −3.943 | −6.910 |
| 716 | 11 | −2.551 | −4.658 |
| 752 | 11 | −650 | −2.469 |
| 786 | 11 | 2.197 | −2.610 |

**Esses valores não são coordenadas do disparo na tela**: falta compor as transformações de cada pai e confirmar a hierarquia acessada por `getChildAt(0)`. Usá-los diretamente no Canvas deslocaria os efeitos incorretamente.

A ausência de marcador no SWF do Reaper é compatível com a utilização do fallback do ActionScript, mas não exclui logicamente um marcador criado ou modificado em tempo de execução. O Canvas usa esse fallback **como aproximação**, com a altura **161 px definida na demo** — ainda não temos o `bmd.height` efetivo sob zoom do cliente Flash. Portanto não é uma afirmação de precisão absoluta do ponto de saída.

[Resultado auditável do scanner, com 26 eventos completos, nomes, IDs e matrizes](https://github.com/Acccelll/Social_wars_test/actions/runs/39462223812/artifacts/12283137586) · [dados resumidos versionados](../data/rebuild/original_facing_projectile_5d8x.json).

## 3. Implementação independente

- `rebuild/combat/src/originalDirection.ts`: `originalFacingFrame`, `originalSpriteFrame`, `originalDirectionToward`, `originalProjectileStart` e `originalProjectileHitPoint`, validados de forma determinística.
- `rebuild/combat/src/scene.ts`: mantém `facing` por unidade e calcula a orientação ao atirar no oponente; no cenário inicial Bushwacker **RIGHT 3**, Reaper **LEFT 7**.
- `rebuild/combat/demo/originalVisuals.js`: para o Reaper, seleciona automaticamente frame gráfico **3** e aplica `scaleX=-1` quando ele encara o Bushwacker à esquerda. Oferece opção manual de pose e retorno a automático.
- `rebuild/combat/demo/arena.js` e `arena.html`: controles em navegador, origem visual da bala/laser, transições de HP e morte preservadas.
- `rebuild/combat/serve.mjs`: entrega o módulo de direção compilado.
- `rebuild/combat/test/originalDirection.test.mjs`: prova casos de 8 orientações, 5 frames + mirror, frames de ataque/morte, dead zone, marcadores/fallback e direção automática da cena.
- `rebuild/combat/test/originalDirection.browser.mjs`: Chromium real com atlas originais, alternância manual/automática, origem do Reaper, acerto, HP e vitória.
- `.github/workflows/original-facing-5d8x.yml`: dois jobs separados: scanner original + validação TypeScript/browser.

Esta etapa não altera as estatísticas do catálogo comunitário, a lógica de dano/defesa, nem os sprites SWF originais. Seu objetivo é **reduzir a arbitrariedade visual da apresentação**.

## 4. Limites e próximo lote — 5D.8Y

**Pendente para paridade:** reconstruir a cadeia de transformações dos cinco `projectilePoint` do Bushwacker até o espaço do mapa, aplicar `Utils.TileToPixel` real para converter orientação em mundo isométrico, confirmar a altura gráfica nativa e registrar a temporização entre frame de ataque e efeito de tiro. Sem esses passos, a trajetória e os pivôs são **parcialmente aproximados**.

**Próximo 5D.8Y:** percorrer a árvore de `DefineSprite` e `PlaceObject` para calcular posições de marcadores do Bushwacker em coordenadas normalizadas por pose, então comparar com imagens originais de disparo e ajustar os offsets comprovadamente.
