# Lote 5D.4 — Timelines SWF e relações entre sprites

**Status:** extração estrutural de todos os SWFs aprovada em 19/10/2026.
É um inventário de quadros e eventos, NÃO um vídeo nem uma recriação
jogável de todas as animações.

## Execução real

[GitHub Actions 39297155116](https://github.com/Acccelll/Social_wars_test/actions/runs/39297155116):
**success**. Foram analisados 1.118 SWFs, sem nenhum erro de arquivo.

| Elemento | Contagem |
|---|---:|
| SWFs verificados | 1.118 |
| Definições de DefineSprite | 43.426 |
| Quadros de sprite declarados | 400.023 |
| Quadros de sprite efetivamente observados | 400.023 |
| Eventos PlaceObject nas timelines dos sprites | 2.782.788 |
| Eventos RemoveObject nas timelines dos sprites | 109.884 |
| Advertências de interpretação de colocação | 2 |

As duas advertências são **de interpretação dos campos de PlaceObject**,
não erros na leitura geral dos SWFs. O processamento dos 1.118
arquivos foi aprovado, mas a fidelidade detalhada dessas duas operações
depende de diagnóstico adicional.

## O que extraímos

A ferramenta `tools/visual_timelines.py` lê os próprios bytes FWS/CWS
da distribuição 0.02a (sem modificar o arquivo original) e identifica:

- frequência de quadros (fps) e duração declarada da timeline raiz;
- identificadores dos sprites `DefineSprite` e seus quadros;
- eventos `PlaceObject` e `RemoveObject`, profundidade e referências;
- transformações `MATRIX` quando decodificadas (twips e escalas);
- rótulos `FrameLabel`, nomes de instância e símbolos exportados;
- lista de sprites/recursos filhos por character ID.

O CSV geral abrange os 1.118 SWFs. Há relatórios detalhados compactados
em `*.timeline.json.gz` para seis fontes de prova:

- `Basesec_1.5.4.swf` — cliente principal;
- `1212_tetrapod_mech.swf` e `1313_splinterMech.swf` — unidades;
- `good_10_m.swf` — personagem;
- `0022_tower_1_m.swf` e `0026_command_center_1_m.swf` — construções.

[Baixar o artefato temporário do GitHub](https://github.com/Acccelll/Social_wars_test/actions/runs/39297155116/artifacts/12209232091)
(retenção prevista de 14 dias).

## Como repetir localmente

```powershell
py -3 tools/visual_timelines_test.py

py -3 tools/visual_timelines.py --archive "social-warriors_0.02a.zip" --out "dist/timeline-catalog" --details "Basesec_1.5.4.swf,1212_tetrapod_mech.swf,0022_tower_1_m.swf" --strict
```

O script usa exclusivamente a biblioteca padrão do Python.

## Limitações importantes

1. **Eventos estáticos não são estados dinâmicos da animação.** O AS3
   pode mover, gerar ou alterar elementos em runtime, inclusive fora
   de eventos registrados nos tags.
2. **Não há áudio sincronizado, montagem de atlas nem spritesheet final**
   nesse lote.
3. A identidade do recurso é `character_id` **dentro do mesmo SWF**;
   IDs de SWFs diferentes não são intercambiáveis.
4. Para reconstruir animações editáveis, ainda precisaremos comparar
   a timeline com a execução no Ruffle e/ou exportar amostras de
   frames/GIF/APNG via FFDec. Consulte a
   [documentação do FFDec](https://github.com/jindrapetrik/jpexs-decompiler/wiki/Commandline-arguments).

**Próximo micro-lote 5D.5:** criar prévias curtas por sprite,
vinculadas ao SWF e `character_id`, e um catálogo navegável de
unidades, construções e interface. Não é necessária uma nova
exportação massiva de todos os frames do jogo.
