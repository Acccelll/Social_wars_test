# Social Wars — Lote 5D.8W: recuperação das 25 poses do Reaper Drone

**Fonte:** Social Wars 0.02a, SWF original `assets/sprites/1376_reaperDrone.swf`, SHA-256 `c26e398f5f2209eb9ba8fc3ef84ed243b1032240c3e2f543a879330e77b64b83`. Extração somente leitura com FFDec 26.3.0 e análise de tags SWF; o cliente Flash não foi modificado.

## Principal descoberta

A exportação 5D.8V usava `-select 1654:1` com `-sublength 15` (equivalente para cada início de estado), obtendo **subframes de um único quadro raiz**. Como os filhos diretos do Reaper têm timelines estáticas de um quadro, isso gerou **uma pose repetida**.

A timeline raiz `DefineSprite 1654` contém realmente **25 frames**, divididos assim:

| Estado original | Frames do sprite raiz | Imagens distintas reexportadas | Interpretação confirmada |
|---|---|---|---|
| `QUIETO` | 1–5 | 5 | Cinco poses visuais diferentes |
| `ANDAR` | 6–10 | 5 | Cinco poses visuais diferentes |
| `ATAQUE` | 11–15 | 5 | Cinco poses visuais diferentes |
| `MUERTE` | 16–20 | 1 | Sem novas trocas de elementos nos quadros 17–20 |
| `PICAR` | 21–25 | 1 | Sem novas trocas de elementos nos quadros 22–25; efeito pode ser vazio |

A classificação das cinco poses como **possíveis orientações** é consistente com a estrutura e com outras animações direcionais, mas ainda **não há correspondência confirmada** entre índice 1–5, ângulo exato e lógica AVM2 de direção. **Não** tratá-las como cinco instantes de tempo.

O parser do SWF encontrou **5.090 eventos de mudança de display list** na timeline raiz: 2.576 `place` e 2.514 `remove`, sem erros de interpretação. A distribuição por estado reflete trocas gráficas expressivas em `QUIETO`, `ANDAR` e `ATAQUE`, enquanto os quadros posteriores em `MUERTE` e `PICAR` não contêm novas mudanças visuais.

### Pivô e pontos de disparo: ainda não resolvidos

O SWF raiz posiciona o sprite 1654 com transformação **(1393,3502) twips**, que corresponde a (69,65 px, 175,1 px) na unidade interna Flash. Esse ponto **não deve ser confundido** com a âncora dos pés nem com o ponto de origem do disparo. O pacote registra `alphaBounds` de cada quadro e mantém o canvas de exportação consistente para reduzir oscilação de escala; isso não identifica automaticamente muzzle/pivot.

## Implementação na arena independente

- `tools/reaper_root_frames_5d8w.py`: extrai os **25 quadros raiz reais** com `-selectid 1654 -select 1654:1-25 -sublength 1 -format sprite:png`. Se necessário, usa uma chamada por quadro; verifica SHA do SWF e os `FrameLabel` originais.
- `tools/merge_reaper_root_frames_5d8w.py`: substitui somente atlas do Reaper no pacote 5D.8V, preservando os demais 8 recursos anteriores (Bushwacker + FX); adiciona quinto estado `PICAR` e manifesto com proveniência/limitações.
- `rebuild/combat/demo/originalVisuals.js`: escolhe o quadro do Reaper explicitamente pelo controle de pose, sem girar imagens ao longo do tempo e **sem** alterar cálculo do motor TypeScript.
- `rebuild/combat/demo/arena.html`: controle **Reaper: direção 1/5** para alternar imagens. Não afirma qual índice corresponde a norte/sul/leste/oeste.
- `rebuild/combat/test/reaperRootFrames.browser.mjs`: confere em Chromium que a imagem no Canvas muda de pixels ao alternar a direção; testa também fallback vetorial, disparo manual, HP e vitória.
- `.github/workflows/reaper-root-frames-5d8w.yml`: exportação íntegra do SWF original, reconstrução do pacote, compilação independente, testes e screenshot.

**Os SWFs não são adicionados ao histórico do GitHub.** Os PNGs derivados ficam no artefato ZIP executável.

## Como executar

Extraia o pacote `SocialWars_5D8W_PACOTE_CONTINUIDADE.zip` e rode:

```bash
cd rebuild/combat
node serve.mjs
```

Com Node.js 22+ abra **http://127.0.0.1:5179/arena**. O pacote já inclui o JavaScript compilado. Para reexecutar os testes a partir de `src/`: `npm install && npm test`.

## Limitações e próxima etapa 5D.8X

Ainda faltam: relacionar direção 1–5 à orientação geométrica efetiva no motor original, recuperar pontos de origem de projéteis, ancoragem consistente entre unidades/estado, sincronia de disparo e FX 24 fps, além da IA de caminho e movimentação. **A existência de cinco quadros raiz não demonstra, por si só, que seja animação temporal.**

**Próximo 5D.8X:** instrumentar as mudanças de orientação em combate real no Ruffle/Flash e ligar a orientação do Canvas a coordenadas/ângulos com evidência, antes de automatizar a troca de pose ou implementar deslocamento.
