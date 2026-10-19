# Lote 5D.7 — Revisão visual e classificação por evidência

Esta etapa verifica as 17 prévias GIF de 14 SWFs geradas no lote 5D.6, sem alterar o jogo original.

A auditoria calcula duplicatas exatas usando SHA-256 do arquivo, equivalências por pixels decodificados e possíveis semelhanças visuais usando assinaturas perceptuais. Uma semelhança candidata NÃO comprova reutilização e não autoriza apagar o recurso.

Os estados esperados são espera, movimento, ataque, dano, destruição e construção. Cada estado só é sugerido quando nomes de símbolos, instâncias ou labels de quadros do sprite selecionado ou de seus filhos imediatos contêm indícios específicos. Nomes do arquivo ou quantidade de quadros nunca bastam para confirmar ação.

Todos os resultados recebem o estado de revisão original_runtime_confirmation_pending. O modo unclassified significa que o SWF não trouxe evidência suficiente. Nenhuma ação é declarada confirmada sem execução do cliente original.

Saídas: data/visual/animation_review_5d7.csv e .json no repositório; galeria review.html com GIFs e filtros no artefato temporário do GitHub Actions.

O sistema de seleção de ações ainda não foi ligado à IA ou ao gameplay. Os IDs dos sprites são válidos dentro do SWF de origem e não são globais.
