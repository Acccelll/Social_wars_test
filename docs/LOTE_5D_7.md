# Lote 5D.7 — Revisão visual e classificação por evidência

Esta etapa verifica as 17 prévias GIF de 14 SWFs geradas no lote 5D.6, sem alterar o jogo original.

A auditoria calcula duplicatas exatas usando SHA-256 do arquivo, equivalências por pixels decodificados e possíveis semelhanças visuais usando assinaturas perceptuais. Uma semelhança candidata NÃO comprova reutilização e não autoriza apagar o recurso.

Os estados esperados são espera, movimento, ataque, dano, destruição e construção. Cada estado só é sugerido quando nomes de símbolos, instâncias ou labels de quadros do sprite selecionado ou de seus filhos imediatos contêm indícios específicos. Nomes do arquivo ou quantidade de quadros nunca bastam para confirmar ação.

Todos os resultados recebem o estado de revisão original_runtime_confirmation_pending. O modo unclassified significa que o SWF não trouxe evidência suficiente. Nenhuma ação é declarada confirmada sem execução do cliente original.

Saídas: data/visual/animation_review_5d7.csv e .json no repositório; galeria review.html com GIFs e filtros no artefato temporário do GitHub Actions.

O sistema de seleção de ações ainda não foi ligado à IA ou ao gameplay. Os IDs dos sprites são válidos dentro do SWF de origem e não são globais.

## Resultado real — 19/10/2026

A execução [39304404150](https://github.com/Acccelll/Social_wars_test/actions/runs/39304404150)
terminou com sucesso e **quatro testes Python aprovados**.
Contagens: 14 SWFs, 17 GIFs, 1 grupo exato de duplicação,
0 grupos adicionais com pixels equivalentes por assinatura normalizada,
0 pares próximos dentro do limiar definido.

Par exato (mesmo checksum de GIF renderizado):
`0022_tower_1_m.swf#52` ⇔ `0040_workshop_1_m.swf#52`.
**Não excluir nenhum dos dois recursos automaticamente**: podem
compartilhar animação deliberadamente e ainda ter outros assets
e comportamentos diferentes em runtime.

O resultado de classificação foi `metadata_hints=0`,
`unclassified=17` e `runtime_confirmed=0`.
Os nomes de instâncias e os `FrameLabel` disponíveis não provaram
nenhum dos estados de ação solicitados. Isso **não significa que
as unidades não tenham animações**: significa que este método
estático não consegue identificá-las.

### Arquivos

- [Auditoria completa JSON](../data/visual/animation_review_5d7.json)
- [Auditoria tabular CSV](../data/visual/animation_review_5d7.csv)
- [Fila de inspeção no runtime](../data/visual/animation_review_5d7_queue.csv)
- [Pacote GIF de revisão](https://github.com/Acccelll/Social_wars_test/actions/runs/39304404150/artifacts/12212991791),
  aproximadamente 2 MB, expiração prevista para 02/11/2026.

## Próxima etapa — 5D.8

Instrumentar em ambiente de teste o cliente original com Ruffle,
observar as ações disparadas (parado, deslocamento, ataque, dano,
destruição, produção) e registrar eventos/mapeamento por
`source SWF` + `character_id` + estado. Preencher o CSV
**somente com evidência observada**; deixar sem estado o que
não for possível validar. Não tocar no executável nem nos salvamentos.
