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

**Resultado anterior:** nos lotes 3H–3I, a compilação era bloqueada pela ausência de `mxmlc`; as rotinas de teste eram apenas estáticas/modeladas. Qualquer SWF gerado posteriormente deve ser validado separadamente.

## Diagnóstico

Se o jogo original funciona e o `AS3Probe` não, o bloqueio está na compilação/porta experimental; **não** representa falha do jogo original.

Se a porta 5055 estiver ocupada, verificar o servidor já aberto antes de iniciar outra instância.
