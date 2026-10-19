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
