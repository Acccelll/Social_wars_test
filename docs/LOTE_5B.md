# Lote 5B — Execução real do AS3Probe no Ruffle

## Critério de aceite

O teste não pode aprovar somente com SWF compilado. Deve executar o SWF
**no Chromium headless, via Ruffle**, capturar a resposta AS3 pela API `ExternalInterface` (ou `traceObserver`, quando disponível) e receber:

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
5. `ExternalInterface.call("swProbeSignal", message)` devolve os resultados do ActionScript à página JavaScript. `traceObserver` também é instalado como canal alternativo, mas não recebeu mensagens na execução aprovada.
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

## Resultado REAL — 19/10/2026

- Workflow CI aprovado: https://github.com/Acccelll/Social_wars_test/actions/runs/39260961090
- Commit do código sob teste: `60f56fd39a4142974528df0e7d296e6ff08f2825`.
- Runtime: Chromium headless com Ruffle **0.7.1** (renderizador wgpu-webgl).
- SWF carregado e reconhecido: 1 quadro, AVM2 / ActionScript 3, SWF 38.
- Bytes SWF carregados: **7.628**.
- `SWTEST:SUMMARY pass=8 fail=0` por **ExternalInterface**.
- Capturados **11 sinais**: BOOT, 8 PASS, tamanho de caminho longo = 5, SUMMARY.
- `traceObserver`: **0 sinais**; por isso não é usado como confirmação de sucesso neste runtime.
- Erros de navegador/redes durante a execução aprovada: **0**.
- Artefato SWF: `social-wars-as3-probe` (ID `12190282061`).
- Evidências: `social-wars-ruffle-smoke` (ID `12189857476`), contendo `report.json` e `screenshot.png`.
- Retenção de 14 dias (artefatos do GitHub Actions): download na execução indicada.

A primeira tentativa com caminho de arquivo carregado como URL não executou o probe; carregar bytes com `DataLoadOptions` passou a expor metadados SWF. Preservar `trace()` em compilação debug não foi suficiente para o observer; a instrumentação `ExternalInterface` permitiu verificar **a execução efetiva do ActionScript**.

**Conclusão:** Lote 5B **concluído**. Este resultado valida os oito casos de contrato da porta de A*, não a equivalência integral com a implementação original de Social Wars.

A execução é aberta no GitHub Actions após alterações na árvore do teste.

Referência API Ruffle:
https://ruffle.rs/js-docs/master/interfaces/Player.PlayerV1.html
