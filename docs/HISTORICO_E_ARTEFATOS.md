# Artefatos históricos (ainda não importados integralmente)

Os ZIPs de engenharia reversa foram entregues em uma conversa anterior. Este documento é um inventário para conciliar o repositório com os artefatos locais do usuário.

| Lote | Arquivo histórico | Conteúdo aproximado |
|---|---|---|
| 3C | `Social_Wars_0.02a_AVM2_Lote3C.zip` | SWF, ABC, índices e P-code geral |
| 3D | `Social_Wars_0.02a_ActionScript_Lote3D.zip` | Trechos AS3 e P-code de combate/IA |
| 3E | `Social_Wars_0.02a_Lote3E_Combate_AStar.zip` | Análises de ataque, rota e 18 métodos |
| 3F | `Social_Wars_0.02a_Lote3F_AStar_Reconstruido.zip` | Três fragmentos AS3 de A* |
| 3G | `Social_Wars_0.02a_Lote3G_AStar_Fidelidade.zip` | Porta isolada e análise do custo g |
| 3H | `Social_Wars_0.02a_Lote3H_Integracao_IsoUnit.zip` | Proxy, bridge e scripts de compilação |
| 3I | `Social_Wars_0.02a_Lote3I_Contrato_NodesPath.zip` | Contratos de movimento e testes |

**Não afirmar que esses arquivos fazem parte do repositório.** Não foram transferidos integralmente para o Git. Para consolidá-los posteriormente, primeiro extrair os ZIPs locais e selecionar os **arquivos de código próprios**, relatórios e índices redistribuíveis. Excluir binários, imagens, áudio, dados e salvamentos de terceiros.

## Identidade da referência analisada

```text
Pacote: social-warriors_0.02a(3).zip
SWF: assets/flash/Basesec_1.5.4.swf
SHA-256: e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77
```

Antes de usar outra versão do jogo, verifique esse hash e atualize as referências ABC.

## Escopo desta primeira publicação

README, documentação técnica, scripts mínimos de build/testes e uma porta AS3 reconstruída a partir das análises anteriores. A geração compilada e os binários originais permanecem fora deste repo.
