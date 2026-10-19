# Social Wars Test

Projeto de preservação técnica, estudo e evolução do **Social Wars 0.02a**.

> **Estado atual:** o jogo original está funcionando localmente no Windows, com servidor na porta `5055` e execução confirmada pelo usuário no navegador com Ruffle. **Ainda não reconstruímos nem recompilamos o cliente completo.**

## Objetivo

Consolidar em um único repositório o conhecimento e os protótipos obtidos a partir do cliente `Basesec_1.5.4.swf`, e evoluir gradualmente até uma versão editável, compilável e testável.

### O que já foi obtido

- Execução da distribuição `social-warriors_0.02a` com servidor local.
- Extração/análise do bytecode AVM2 do cliente.
- Reconstrução parcial dos métodos de dano, inteligência artificial e movimentação.
- Port experimental do algoritmo A* em ActionScript 3, com verificação específica da regra de custo `g`.
- Adaptação experimental do contrato `NodesPath` / `IsoUnit`.
- Pipeline reproduzível de compilação e **execução de um SWF experimental em Ruffle/Chromium, com 8/8 testes AS3 aprovados** (Lote 5B).

Leia [STATUS.md](docs/STATUS.md), [ARQUITETURA.md](docs/ARQUITETURA.md) e [ROADMAP.md](docs/ROADMAP.md).

## Estrutura

| Diretório | Conteúdo |
|---|---|
| `as3/src/com/socialpoint/astar/recovered/` | Reconstituições experimentais em ActionScript 3 |
| `tools/` | Scripts de verificação e compilação |
| `tests/ruffle/` | Teste de execução do SWF real em Chromium/Ruffle, com relatório e captura de tela |
| `docs/` | Resultados dos lotes, limitações, roteiro de continuidade |

## Executar o jogo original

A distribuição original, necessária à execução, **não está incluída neste repositório**.

1. Obtenha a versão `0.02a` do projeto de preservação [Social Warriors](https://github.com/AcidCaos/socialwarriors).
2. Extraia localmente e execute `social-warriors.exe`.
3. Abra `http://127.0.0.1:5055/`; se necessário, use [Ruffle](https://ruffle.rs/).
4. **Preserve e faça backup da pasta `saves/` antes de qualquer teste.**

Ver [EXECUCAO.md](docs/EXECUCAO.md).

## Integridade da fonte analisada

- SWF original: `assets/flash/Basesec_1.5.4.swf`
- SHA-256: `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`
- Os números de método e instruções nos relatórios referem-se a **esse SWF**, não necessariamente a outras versões.

## Limites e propriedade intelectual

Este repositório **não inclui** o jogo, o servidor original, recursos gráficos/áudio, salvamentos ou binários de terceiros. Disponibiliza apenas documentação e código experimental de análise/portabilidade; isso não implica autorização para redistribuir os ativos do jogo. Não há declaração de equivalência ou compatibilidade integral.

## Próximo passo

**Lotes 5A e 5B concluídos:** o SWF experimental foi compilado com Flex e executado em Chromium/Ruffle: **8/8 testes AS3 aprovados** na [execução CI 39260961090](https://github.com/Acccelll/Social_wars_test/actions/runs/39260961090). Veja [LOTE_5B.md](docs/LOTE_5B.md). **Próximo lote 5C:** confrontar a lógica com o SWF original e preparar o adaptador tipado. Ainda não recompilamos o jogo completo.
