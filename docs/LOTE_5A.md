# Lote 5A — Preparação da compilação ActionScript 3

## Objetivo

Produzir um **SWF mínimo compilado** a partir de `as3/src/AS3Probe.as`, usando a porta experimental do A*.

**Isto NÃO recompila o Social Wars inteiro.** O cliente de referência possui milhares de métodos, recursos Flash e dependências que ainda precisam de descompilação/integração.

## Compilação reproduzível

O workflow `.github/workflows/as3-probe.yml`:

1. Usa Ubuntu e Java 8.
2. Executa os testes Python do cálculo `g`.
3. Baixa o Apache Flex SDK 4.16.1 de `dlcdn.apache.org` (arquivo tar.gz), conferindo o checksum MD5 publicado pelo Apache.
4. Baixa o Adobe `playerglobal32_0.swc` e valida que é um arquivo SWC/ZIP.
5. Invoca o compilador `mxmlc` apontando ao `AS3Probe.as`.
6. Examina o cabeçalho `FWS/CWS/ZWS` e, se tudo funcionar, publica `social-wars-as3-probe` como artefato do Actions.

Não versionar o SDK, `playerglobal.swc` nem binários do Flash — ver `.gitignore`.

### Executar localmente (Linux)

```bash
bash tools/bootstrap_flex_linux.sh
export FLEX_HOME="${FLEX_SDK_DEST:-${TMPDIR:-/tmp}/social-wars-flex-sdk}"
bash tools/build_probe_linux.sh
```

### Executar no Windows

Instalar o Apache Flex SDK com playerglobal.swc para Flash 32.0, apontar `FLEX_HOME` para a pasta do SDK e executar:

```cmd
tools\build_probe_windows.bat
```

## Referências

- Documentação de instalação: https://cwiki.apache.org/confluence/spaces/FLEX/pages/34841996/Installation%2Bhelp
- Download Apache Flex: https://dlcdn.apache.org/flex/4.16.1/binaries/
- Playerglobal 32: https://fpdownload.macromedia.com/get/flashplayer/updaters/32/playerglobal32_0.swc

## Status da validação

**Concluído em 19/10/2026.** Após corrigir a detecção do SDK, a execução [39255285110](https://github.com/Acccelll/Social_wars_test/actions/runs/39255285110) terminou com **success**. O compilador gerou `dist/AS3Probe.swf` de **3.619 bytes**, cabeçalho `CWS` válido, e o Actions publicou o artefato `social-wars-as3-probe` (ID 12187886426; retenção de 14 dias). Os três testes Python também passaram.

O ambiente local deste chat segue sem `mxmlc`, mas a compilação **real em CI** foi confirmada. O SWF é somente o probe; sua execução no Ruffle e a integração no jogo original permanecem pendentes. Veja [BUILD_5A_RESULTADO.md](BUILD_5A_RESULTADO.md).
