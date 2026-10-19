# Catálogo dos arquivos gráficos exportados

Depois de extrair com o FFDec, execute:

```bash
python3 tools/visual_asset_manifest.py --root dist/visual-export
```

Ele gera `visual_files.csv` e `visual_files_summary.json`, com:

- fonte SWF identificada pelo caminho do pacote;
- subpasta de recurso exportado (quando disponível);
- formato, tamanho, checksum SHA-256;
- dimensões de PNG e GIF obtidas dos cabeçalhos, sem precisar de Pillow.

O CSV pode ser usado depois para substituição controlada de imagens.
Ele não reconstitui animações do Flash e não substitui uma revisão
visual dos recursos.

O script não modifica o SWF original nem os salvamentos, e seus
resultados permanecem na pasta local/temporária `dist/`.
