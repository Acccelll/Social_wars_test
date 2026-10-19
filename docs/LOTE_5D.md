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
