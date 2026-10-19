# Lote 5B — Execução real do AS3Probe no Ruffle

## Critério de aceite

O teste não pode aprovar somente com SWF compilado. Deve executar o SWF
**no Chromium headless, via Ruffle**, capturar `trace()` da AVM2 e receber:

- `SWTEST:BOOT`
- Pelo menos oito casos `SWTEST:nome:PASS`
- Zero casos `SWTEST:nome:FAIL`
- `SWTEST:SUMMARY pass=8 fail=0`

O teste também gera `dist/ruffle-smoke/report.json` e `screenshot.png`.

## Fluxo

1. `mxmlc` compila `AS3Probe.as`.
2. Node instala pacote Ruffle selfhosted e Playwright.
3. `python3 -m http.server` hospeda o SWF e o Ruffle apenas na interface loopback.
4. Chromium executa a página `tests/ruffle/index.html`.
5. `player.ruffle().traceObserver` captura mensagens de ActionScript.
6. O teste do Node compara os casos, produz relatório e reprova se houver falha.
7. GitHub Actions preserva os logs de execução e artefatos.

## Testes ActionScript

- Rota adjacente, índice do Proxy, alvo em pixel, remoção/anexo de tiles,
  flag de movimento da IA, destino ocupado, caminho longo e `popNextTile`.

## Limitações

- Testa **classes experimentais `Recovered`**, e não o `IsoUnit` real.
- `tileToPixel` no probe usa escala fictícia e não a projeção original.
- O jogo original e os salvamentos não são acessados.
- Passar no teste não comprova paridade do comportamento do cliente original.

## Repetição local

```bash
bash tools/bootstrap_flex_linux.sh
export FLEX_HOME="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/social-wars-flex-sdk"
bash tools/build_probe_linux.sh
npm install --prefix tests/ruffle
cd tests/ruffle
npx playwright install chromium --with-deps
npm run smoke
```

A execução é aberta no GitHub Actions após alterações na árvore do teste.

Referência API Ruffle:
https://ruffle.rs/js-docs/master/interfaces/Player.PlayerV1.html
