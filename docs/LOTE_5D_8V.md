# Social Wars — Lote 5D.8V: imagens originais na arena independente

**Resultado:** integração funcional com os quadros e efeitos do Social Wars 0.02a, sem executar o cliente Flash. **25 testes passaram** e o Chromium validou **12 atlas originais**, disparo com dano, alternância para desenho vetorial e morte do Reaper Drone.

## Entregas

- `rebuild/combat/demo/originalVisuals.js`: carregador de atlas PNG com fallback automático de sprites vetoriais e alternância em tela.
- `rebuild/combat/demo/arena.js`: estados `QUIETO`, `ATAQUE` e `MUERTE` ligados à representação visual; bala, laser e explosões originais nas posições do modelo 2D.
- `rebuild/combat/demo/arena.html`: botão **Estilo: original/vetorial** e informação de disponibilidade dos recursos.
- `rebuild/combat/serve.mjs`: distribuição segura em loopback de arquivos do pacote opcional `original-visual/`, sem possibilidade de navegar fora dos arquivos permitidos.
- `tools/prepare_original_visuals_5d8v.py`: converte GIFs FFDec de 5D.8K/5D.8M em 12 atlas PNG verificáveis e um manifesto de fonte.
- `rebuild/combat/test/originalVisuals.browser.mjs`: Playwright carrega os sprites, verifica o efeito do projétil e a perda de HP; confere o fallback vetorial, a vitória e quatro screenshots.
- `.github/workflows/original-sprite-arena-5d8v.yml`: baixa **artefatos históricos de read-only FFDec dos próprios lotes 5D.8K e 5D.8M**, constrói PNGs, compila TypeScript e verifica a arena real no Chromium.

## Artefatos originais usados

Não há cópias de SWF, GIF ou atlas PNG no histórico do GitHub. Os recursos visuais são derivados da distribuição original e disponibilizados **somente no pacote de execução**. Os scripts são versionados.

| Personagem | Fonte original | Sprite principal | GIFs exportados | Diversidade de frames |
|---|---|---:|---|---|
| Bushwacker 1358 | `1358_bushwacker.swf` | 1092 | QUIETO, ANDAR, ATAQUE, MUERTE | 12, 15, 15, 14 imagens visuais diferentes |
| Reaper Drone 1376 | `1376_reaperDrone.swf` | 1654 | QUIETO, ANDAR, ATAQUE, MUERTE | **1 pose renderizada em cada estado** |

**Atenção:** cada GIF exportado possui 15 frames de sub-timeline interna FFDec, não todos os frames do filme Flash da unidade; no caso do Reaper Drone, foram exportadas poses estáticas por estado, embora o SWF possua seus próprios timelines internos. Não afirmar que esses GIFs recuperam o controlador completo de animação.

| Unidade | Projétil original | Impacto original | Como a arena usa |
|---|---|---|---|
| Bushwacker | `p.bulletAirBig.swf` | `b.bazookaSmall.swf` | efeito original PNG seguindo trajetória aproximada de bala e explosão no impacto |
| Reaper Drone | `p.laserMassiveDrone.swf` | `b.laserBlue.swf` | sprite interno **DefineSprite 3** visível para o laser (o contêiner público exportado fica transparente), anel azul no impacto |

A associação foi recuperada do ActionScript original em [5D.8M](LOTE_5D_8M.md). **A duração do voo, ângulo, centralização do corpo e taxa de disparo na demo continuam aproximações** e não foram recuperados frame a frame do Flash em execução.

## Executar sem Flash

No pacote final, entre em `rebuild/combat` e rode:

```bash
node serve.mjs
```

Abra **http://127.0.0.1:5179/arena**. O pacote fornece `dist/`, `original-visual/`, `demo/` e o servidor. Não precisa instalar pacotes adicionais para executar a build já compilada. Node.js 22+ é recomendado.

Para recompilar:

```bash
cd rebuild/combat
npm install
npm test
npm run demo
```

A arena é **um protótipo parcial**. Embora os visuais e FX sejam derivados do jogo, o motor continua independente e não implementa ainda IA completa, colisões, pathfinding, terreno original, navegação, outros objetos, animações dinâmicas completas do Reaper, áudio ou mundo persistente.

Os valores HP/ataque/defesa são do patch ativo do **servidor comunitário AcidCaos**, não foram verificados como atributos dos servidores históricos da Social Point.

## Evidências automáticas

[CI #39442496371](https://github.com/Acccelll/Social_wars_test/actions/runs/39442496371) — sucesso: **25/25** testes TypeScript/Node, **12 imagens carregadas** no navegador, disparo manual diminui HP, alternância original/vetorial, vitória automática, **zero erros de página**.

Foram geradas quatro capturas: `5d8v-original-initial.png`, `5d8v-original-hit.png`, `5d8v-original-death.png` e `5d8v-vector-fallback.png`. O ZIP de artefatos contém PNGs, manifesto, código TypeScript e compilado.

## Próximo lote — 5D.8W

Aprofundar o pipeline de animações **do Reaper Drone (subsprites internos)** para além de poses estáticas, mapear direções/origens de disparo, pontos de ancoragem, atualização em 30fps e diferenças entre assets 24fps. Substituir temporizações estimadas onde for possível extrair os valores do código original; preservar o fallback no Canvas.
