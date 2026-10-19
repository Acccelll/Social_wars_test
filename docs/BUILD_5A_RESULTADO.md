# Resultado do lote 5A — primeiro SWF construído

**Data:** 19/10/2026

## Compilação confirmada

- Repositório: `Acccelll/Social_wars_test`
- Workflow: `.github/workflows/as3-probe.yml`
- Execução de sucesso: https://github.com/Acccelll/Social_wars_test/actions/runs/39255285110
- Commit que corrigiu o script de instalação: `2e0bdb106dda4f580248a2570361063f8031a100`
- Plataforma CI: Ubuntu 24.04 + Java 8
- Compilador: Apache Flex SDK 4.16.1 / `mxmlc`
- Biblioteca Flash: `playerglobal.swc` 32.0
- Ponto de entrada: `as3/src/AS3Probe.as`
- Saída: `dist/AS3Probe.swf`
- Tamanho no log da compilação: **3.619 bytes**
- Assinatura dos primeiros bytes: `CWS` (SWF comprimido)
- Resultado do job: **success**
- Testes Python: **3/3** testes unittest passaram
- Artefato: `social-wars-as3-probe` (artifact ID `12187886426`), compactado pelo Actions (~3.762 bytes)
- Vencimento previsto do artifact: **02/11/2026** (14 dias após publicação)

## Primeira falha e correção

A primeira execução (ID `39255131905`) baixou o SDK com checksum válido, mas falhou por um `find` com profundidade de diretórios insuficiente.

A execução seguinte corrigiu a busca de `bin/mxmlc`, instalou `playerglobal.swc`, compilou o AS3 e fez upload do artefato.

## O que este resultado comprova

1. Nosso código de prova passou pela compilação de ActionScript 3.
2. Produzimos um binário SWF novo de forma reproduzível no CI.
3. Os tipos experimentais `AStarRecovered`, `IsoNodeRecovered`, `NodesPathRecovered` e `IsoUnitRouteBridge` são dependências do ponto de entrada compilado, embora testes funcionais ainda sejam necessários.

## O que ainda NÃO comprova

- O SWF não foi executado em runtime Flash/Ruffle.
- O SWF **não é o Social Wars completo**.
- O código recuperado não foi injetado nem comparado funcionalmente com a versão original.
- O caminho reconstruído não é comprovadamente equivalente ao jogo real.
- Nenhuma modificação foi feita na instalação do usuário ou em `saves/`.

## Próximo lote 5B

Executar `AS3Probe.swf` no Ruffle; coletar saída de `trace`, avaliar rota produzida e, depois, adaptar a porta para integração nominal ao cliente original.

O artifact do GitHub Actions é temporário. Para gerá-lo novamente, execute o workflow `AS3 Probe Build` na aba Actions.
