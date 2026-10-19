# Lote 5D — Inventário e extração visual

## Política de preservação

Os arquivos de imagem originais, sprites, vetores e áudio pertencem
aos seus respectivos titulares. Este repositório público guarda
**scripts e inventários de metadados**, não os recursos extraídos.

## Inventário

O arquivo `tools/visual_inventory.py` percorre o ZIP completo
Social Warriors 0.02a, enumerando imagens externas (PNG/JPEG/GIF/WebP/SVG)
e definições gráficas embutidas em arquivos SWF.

Conta `DefineBits`, `DefineShape`, `DefineMorphShape`,
`DefineSprite` e `DefineButton`. Em SWF, uma definição pode
representar múltiplos quadros de uma animação. Definições **não são**
imagens PNG já exportadas.

### Executar sem modificar o jogo

```powershell
py -3 tools/visual_inventory.py --archive "C:\\Jogos\\social-warriors_0.02a.zip" --out "dist\\visual-inventory"
```

A workflow [Visual Assets Inventory 0.02a](../.github/workflows/visual-inventory.yml)
usa a distribuição oficial pública, verifica o tamanho de arquivo e
produz três arquivos de metadados:

- `summary.json`: contagens por categoria, os SWFs mais relevantes e erros.
- `swfs.csv`: um registro por SWF e suas contagens de recursos.
- `external_images.csv`: imagens externas no ZIP.

Ainda não há promessa de que todas as animações tenham sido renderizadas,
nem de que arquivos SWF importem imagens adicionais dinamicamente.

## Exportação real (FFDec)

FFDec/JPEXS exporta imagens, formas vetoriais, morphshapes, sprites,
botões e animações via CLI. Referência:
https://github.com/jindrapetrik/jpexs-decompiler/wiki/Commandline-arguments

O exportador e sua execução serão adicionados ao lote após
validarmos as quantidades reais do inventário. Os arquivos gráficos
serão colocados fora do Git, em diretório `dist/` local do usuário.

## Exportador de recursos disponível

O script `tools/visual_extract.py` aceita o pacote original e a biblioteca
`ffdec.jar` do JPEXS. **Não é necessário descompilar todo o código antes.**

O modo padrão exporta as imagens internas, SVGs de formas,
morphshapes, sprites estáticos e botões de cada SWF.

### Windows — extração local em lotes

Baixe o [FFDec](https://github.com/jindrapetrik/jpexs-decompiler/releases)
e aponte para seu `ffdec.jar`:

```powershell
py -3 tools/visual_extract.py --archive "C:\\Jogos\\social-warriors_0.02a.zip" --ffdec "C:\\Ferramentas\\FFDec\\ffdec.jar" --out "dist\\visual-export" --start 0 --limit 30 --external
```

Para avançar ao lote seguinte, use `--start 30 --limit 30`, depois
`--start 60 --limit 30`, até os 1.118 SWFs serem processados.
Para todos numa única execução, use `--start 0 --limit 0`, mas este
trabalho pode ser pesado. O script grava `export_results.csv` e
`export_summary.json`, anotando falhas por SWF sem interromper o lote.

`--types images` exporta somente bitmaps. `--types visual` exporta
também vetores, sprites estáticos e botões. O modo `sprites` limita-se
a sprites; a conversão de TODOS os quadros animados ainda exige
um processo separado.

### Prova de exportação no GitHub Actions

Workflow [Visual Export Sample 0.02a](../.github/workflows/visual-export.yml)
recebe o nome de um SWF e a classe de recursos. Os arquivos exportados
são enviados como artefato **temporário por 1 dia**, fora do
histórico do Git. Não publique esses recursos no repositório público.

## Resultado verificado do inventário (5D.1)

GitHub Actions: https://github.com/Acccelll/Social_wars_test/actions/runs/39277345729

| Categoria | Quantidade |
|---|---:|
| Arquivos totais no ZIP | 3.272 |
| SWFs | 1.118 |
| Arquivos de imagem externos | 1.899 |
| Bitmaps embutidos (definições SWF) | 41.069 |
| Formas vetoriais | 62.318 |
| Morphshapes | 316 |
| Sprites (definições) | 43.426 |
| Botões | 53 |
| Quadros declarados nas timelines dos sprites | 400.023 |
| Erros de análise | **0** |

SWF principal `Basesec_1.5.4.swf`: **369 bitmaps**, **1.468 shapes**,
**1.224 sprites**, **52 buttons**, **4 morphshapes** e **420 nomes de símbolos**.
SHA-256 verificado: `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`.

Os arquivos CSV e JSON de metadados estão no artefato
`social-wars-visual-inventory` (artifact ID 12197443842).

**Atenção:** sprites, shapes e quadros do Flash são entidades diferentes.
Somar as contagens não equivale ao número de PNGs a serem gerados.
Uma extração de sprites em PNG captura quadros estáticos; a recuperação
das timelines completas será tratada separadamente.

## Inicializador Windows incluído

[`tools/EXTRAIR_IMAGENS_WINDOWS.bat`](../tools/EXTRAIR_IMAGENS_WINDOWS.bat)
facilita a exportação em pequenos lotes. Coloque o ZIP oficial na raiz
do repositório e `ffdec.jar` em `tools/`, além de ter Python 3 e
Java disponíveis no PATH. Clique duas vezes no BAT ou execute no CMD.

Por padrão, processa os primeiros 30 SWFs. Para avançar:

```cmd
set SW_START=30
set SW_LIMIT=30
tools\EXTRAIR_IMAGENS_WINDOWS.bat
```

Os arquivos extraídos ficam em `dist/visual-export/` e nunca
alteram a pasta original do jogo. O primeiro lote também extrai os
1.899 arquivos de imagem diretamente armazenados no ZIP.

## Extração das 1.899 imagens externas — sem FFDec

O script `tools/extract_external_images.py` copia do ZIP oficial
todos os arquivos PNG, JPEG, WebP, GIF, BMP, SVG e APNG para
`dist/visual-external/`, preservando pastas e acrescentando SHA-256
de cada arquivo no `external_manifest.csv`. Isso não extrai bitmaps
**embutidos** nos SWFs, que são tratados pelo FFDec.

Executar localmente:

```powershell
py -3 tools/extract_external_images.py --archive "social-warriors_0.02a.zip" --out "dist/visual-external"
```

O GitHub Actions [Export Direct Image Files 0.02a](../.github/workflows/visual-external.yml)
também gera um artefato temporário de imagens separado do código.
