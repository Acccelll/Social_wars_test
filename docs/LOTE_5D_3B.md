# 5D.3B — Personagens da pasta characters_2

## Escopo

Depois da exportação de cinco mechas (14.436 arquivos, 0 erros),
o próximo passo separa **os bitmaps embutidos** de todos os SWFs na
pasta `assets/characters_2/`, sem gerar dezenas de milhares de
quadros renderizados de animação.

Workflow: [Visual Characters 2 Bitmaps 5D.3](../.github/workflows/visual-characters-2.yml).

### Procedimento

1. Baixa a distribuição 0.02a original.
2. Filtra os SWFs cujo caminho de origem começa por `assets/characters_2/`.
3. Executa JPEXS FFDec no modo `images`.
4. Salva `export_results.csv`, um registro por SWF.
5. Publica dois artefatos temporários: **imagens** (1 dia) e
   **manifesto CSV/JSON** (14 dias).
6. Trata SWFs sem bitmap como `EMPTY_CATEGORY` (não é necessariamente erro).
7. Reprova caso algum SWF gere erro de extração.

### Limites

O resultado não inclui vetores nem reprodução fiel de timelines.
A pasta `characters_2` foi definida a partir da estrutura original,
não por uma taxonomia funcional de unidades do jogo.

O pacote é temporário; nenhuma imagem original é incorporada ao
repositório público. O script local permite repetir a extração.

## Resultado confirmado

[Execução 39294770739](https://github.com/Acccelll/Social_wars_test/actions/runs/39294770739):
**26/26 SWFs processados, 61 bitmaps exportados, 0 erros.**
Arquivo de imagens temporário
[characters2-bitmaps](https://github.com/Acccelll/Social_wars_test/actions/runs/39294770739/artifacts/12207640982)
e [manifesto](https://github.com/Acccelll/Social_wars_test/actions/runs/39294770739/artifacts/12207675863).

As imagens-base dessa pasta foram extraídas. **Não** significa que os
vetores e animações dos 26 SWFs tenham sido totalmente recompostos.
