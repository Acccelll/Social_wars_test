# Execução local e Ruffle

## Jogo original — cenário que já funcionou

A distribuição do projeto de preservação [Social Warriors](https://github.com/AcidCaos/socialwarriors) contém o executável do servidor. A distribuição 0.02a foi executada com sucesso no ambiente Windows do usuário.

1. Obter e extrair a distribuição original separadamente.
2. Antes de modificar qualquer coisa, copiar o diretório `saves/` para outro local.
3. Iniciar `social-warriors.exe`.
4. Abrir `http://127.0.0.1:5055/`.
5. No navegador moderno, executar o cliente SWF pelo [Ruffle](https://ruffle.rs/) quando necessário.
6. Verificar mapa, movimentação, combate, salvamentos e reinício antes de modificações.

**Não versionar** `saves/`, executáveis e SWFs de terceiros neste repositório público.

## AS3 recuperado (experimental)

O protótipo recuperado é distinto do jogo original. Seu ponto de entrada é `as3/src/AS3Probe.as`. A intenção é produzir um SWF simples para testar `AStarRecovered`, não gerar o jogo completo.

Precisa de:
- Apache Flex SDK com `mxmlc` instalado;
- `playerglobal.swc` adequado ao alvo;
- runtime Flash/Ruffle compatível.

No Windows, executar `tools/build_probe_windows.bat`. Em Linux, `tools/build_probe_linux.sh`. Não há dependências do SDK incluídas no Git.

**Atualização 5A (19/10/2026):** compilação aprovada no GitHub Actions, [execução 39255285110](https://github.com/Acccelll/Social_wars_test/actions/runs/39255285110). O artefato `social-wars-as3-probe` contém `AS3Probe.swf` (3.619 bytes), ainda **não executado no Ruffle**. Abra a execução e obtenha o ZIP na seção *Artifacts* (retenção de 14 dias).

**Atualização 5B (19/10/2026):** o [workflow 39260961090](https://github.com/Acccelll/Social_wars_test/actions/runs/39260961090) gerou um SWF experimental e o executou com sucesso em Chromium/Ruffle: 8/8 testes ActionScript via `ExternalInterface` (o `traceObserver` não capturou mensagens). O artefato de evidências inclui `report.json` e captura de tela. **Isso não substitui o jogo original.**

## Diagnóstico

Se o jogo original funciona e o `AS3Probe` não, o bloqueio está na compilação/porta experimental; **não** representa falha do jogo original.

Se a porta 5055 estiver ocupada, verificar o servidor já aberto antes de iniciar outra instância.

## Lote 5C.1 — Prova de contrato nominal (isolada)

Foi validado outro SWF gerado pela compilação de `as3/contract_harness/src/ContractProbe.as`:

```bash
bash tools/build_contract_probe_linux.sh
SW_SMOKE_SWF=ContractProbe.swf SW_EXPECT_TESTS=15 npm run smoke --prefix tests/ruffle
```

Resultado da [execução CI 39262967632](https://github.com/Acccelll/Social_wars_test/actions/runs/39262967632): 15/15 no harness + 8/8 no probe de A*. Os **tipos fictícios com nomes iguais aos originais servem apenas para esse SWF de teste** e não devem ser combinados com os binários do jogo original.
