# Social Wars — Lote 5D.8Z: registro dos quadros do Bushwacker e calibração controlada

**Conclusão:** cinco quadros raiz originais `ATAQUE 11–15` exportados **sem recorte por pose**, limites reais de pixels visíveis medidos e novo conversor matemático para aplicar `projectilePoint` ao PNG/Canvas **quando sua origem e escala forem medidas**. Um inspetor visual em `/calibration` permite avaliar hipóteses de registro sem alterar a arena. O ponto de registro nativo não está identificado, por isso **os projéteis do jogo continuam com o fallback visual existente**.

## Fonte, integridade e medição

- Fonte: `assets/sprites/1358_bushwacker.swf`, SHA-256 `e9db23f98dcaa5cf81cbcdac85154fcb1da92a205b7d9047a5d420fb9d068c5e`.
- `tools/bush_attack_registration_5d8z.py` faz extração somente leitura via FFDec 26.3.0: `-selectid 1092 -select 1092:11-15 -sublength 1 -format sprite:png -export sprite`. A ferramenta checa o hash e obtém os cinco PNGs raiz, não subframes do quadro 11.
- Todos possuem canvas de **1255 × 1140 pixels**, e cada quadro é visualmente distinto dos outros quatro.
- O novo atlas `bush_attack_root_11_15.png` tem **5 colunas**, com largura de célula 1255 e altura 1140, preservando o alinhamento (0,0) dos PNGs FFDec. **Não centraliza nem recorta pixels visíveis.**
- SHA-256 do atlas gerado: `037c23111207df255bc122c7b0f14bf63b9ec0ae1e8f9b5c931a7c9609cf016f`.

### Limites opacos observados em cada quadro raiz

| Pose / frame | Bbox [left, top, right, bottom] no PNG FFDec | Largura × altura visíveis |
|---|---|---|
| 1 / 11 | [485, 436, 771, 814] | 286 × 378 |
| 2 / 12 | [497, 409, 856, 813] | 359 × 404 |
| 3 / 13 | [525, 429, 790, 817] | 265 × 388 |
| 4 / 14 | [497, 418, 826, 813] | 329 × 395 |
| 5 / 15 | [490, 443, 780, 814] | 290 × 371 |

Esses limites são derivados do canal alfa e **não representam pivô, pés, cano ou origem de coordenadas do Flash**. O bitmap de exportação é maior que o desenho e pode conter a margem/offset do renderizador FFDec. É incorreto usar o centro do bitmap, a bbox ou o pixel do pé como registro comprovado.

## Marcadores originais e transformação em Canvas

O [lote 5D.8Y](LOTE_5D_8Y.md) recuperou os cinco marcadores `projectilePoint` em pixels **locais do DefineSprite 1092**:

| Pose | Local X | Local Y |
|---|---:|---:|
| 1 | +116,15 | −371,70 |
| 2 | +254,55 | −299,20 |
| 3 | +186,55 | −182,50 |
| 4 | +89,70 | −78,25 |
| 5 | −93,90 | −109,70 |

`rebuild/combat/src/sourceRegistration.ts` implementa o mapeamento explícito:

```
sourceX = ffdecRootX + (localMuzzleX × ffdecPixelsPerLocalPixel)
sourceY = ffdecRootY + (localMuzzleY × ffdecPixelsPerLocalPixel)
canvasX = imageDrawX + sourceX × imageDrawWidth / exportedImageWidth
canvasY = imageDrawY + sourceY × imageDrawHeight / exportedImageHeight
```

A direção esquerda aplica o espelhamento original **em torno do pivô raiz, não do centro da imagem**.

A API exige `ffdecImageRootOriginPx`, `ffdecPxPerSpriteLocalPx`, dimensões do PNG e retângulo de desenho no Canvas. Ela **recusa escala nula/inválida**. Não há valores padrão secretos para origem ou zoom.

## Novo inspetor experimental

Com o pacote de continuidade aberto em Node.js 22+, inicie:

```bash
cd rebuild/combat
node serve.mjs
```

Visite **http://127.0.0.1:5179/calibration**. A interface:
- mostra diretamente cada um dos cinco quadros raiz e sua caixa de pixels visíveis;
- permite selecionar pose 1–5 e inspecionar o marcador de ataque com as coordenadas originais;
- aguarda um **clique explícito** para selecionar um pivô proposto na imagem, além de campo para uma escala FFDec/pixel local;
- desenha a cruz da origem proposta e o ponto amarelo do marcador calculado; informa se caiu dentro da imagem;
- permite limpar o ajuste e voltar ao estado *não calibrado*;
- não salva esse ajuste nem muda disparos na arena.

A escala **1** mostrada inicialmente é apenas parâmetro de experimentação, **não uma medida recuperada**. O resultado de uma interação manual não equivale à validação científica do ponto de registro.

## Testes e evidências

- Workflow principal: [GitHub Actions 5D.8Z — 39475880764](https://github.com/Acccelll/Social_wars_test/actions/runs/39475880764), concluído **success**.
- **45 testes** Node/TypeScript aprovados, sem falhas: novos testes verificam conversão local → PNG → Canvas, espelhamento em torno do ponto raiz, coordenadas inválidas e escala obrigatória.
- Chromium executou `/calibration` e verificou cinco poses, estado inicial desconhecido, seleção manual, projeção, limpeza do ajuste, endpoints da imagem, acesso à arena, **13 imagens visuais anteriores** e **zero erros JavaScript**.
- Os testes de regressão de `/muzzle` (5D.8Y) continuaram passando.
- O atlas, o manifesto `registration_5d8z.json`, código, JS compilado e screenshots foram preservados no artefato `socialwars-bush-root-calibration-5d8z` do workflow. **Nenhum SWF foi comitado.**

## Status de fidelidade e próximo lote

**Verificado:** cinco quadros raiz reais, tamanho dos PNGs, alfa por pose, cadeia de matrizes do marker (5D.8Y), mapeamento matemático com transformação explicitamente fornecida, interface independente.

**Não verificado:** o ponto exato de registro do `DefineSprite 1092` dentro do bitmap FFDec, sua correspondência com `ghostBuilding` no runtime Flash, a escala nativa `bmd` e zoom/câmera, a localização final da boca da arma na arena. **Não declarar que a origem de disparo do jogo já foi recalibrada**.

**Próxima etapa — 5D.9A:** rastrear na execução real Ruffle a relação entre posição do `ghostBuilding`, quadro 11–15, matriz de exibição e registro dos pixels FFDec. Quando houver valores comprovados para origem e escala, conectar `calibratedFfdecBushShot()` ao renderizador de disparos, com testes visuais de alinhamento e rollback do fallback.
