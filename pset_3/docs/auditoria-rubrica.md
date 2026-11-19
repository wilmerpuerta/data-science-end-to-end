# Auditoría final PSet 3 - reconstrucción v2

Resultado: **verified_with_declared_limitations**. No se asigna nota ni se afirma 100 % de cumplimiento literal. Se auditan evidencias y se conservan las limitaciones declaradas.

| Comprobación | Resultado |
|---|---|
| CSV_vs_servidor | PASA |
| snapshot_splits_y_CV | PASA |
| metadata_todas_corridas | PASA |
| commits_Git_reales | PASA |
| dos_baselines_y_seis_familias | PASA |
| baselines_antes_de_candidatos | PASA |
| tres_por_treinta | PASA |
| top3_por_negocio | PASA |
| tuning_nested | PASA |
| grafico_tuning_documento_y_notebook | PASA |
| pipelines_firma_y_ejemplo | PASA |
| decision_previa_integra | PASA |
| aliases_registry | PASA |
| reproduccion_exacta_proceso_limpio | PASA |
| seis_notebooks_ejecutados_y_hashed | PASA |
| anticipacion_y_un_solo_cupo | PASA |
| ausencia_registros_asociacion_ablacion | PASA |
| estaticos_no_Dummy_y_reactiva_acotada | PASA |
| PDF_seis_paginas_y_revision_visual | PASA |
| prompting_conclusion_negocio | PASA |
| presupuesto_incluye_intentos | PASA |

Servidor: 382 runs; 379 FINISHED; 3 FAILED. Se comprobaron firma, ejemplo y flavor de 370 pipelines reales, sin confundir fallos o padres lógicos con configuraciones válidas.

## Límites de interpretación y reproducción

- 2014J observed in v1: retrospective reused benchmark, not newly independent hold-out
- No demonstrated stable superiority or causal effect of tutoring; maturation and publication of labels unverified
- Private snapshot, native models, LLM responses and MLflow volumes excluded from public package; exact runtime reproduction conditional on private backup
- Filename Puerta_Wilmer follows author authorization; delivery uses real files directly under pset_3
- Auxiliary multi-cut policy inherits cutoff_day=56 from the common logger; actual rounds 14/28/42 are explicit in its policy artifact; it is not a fitted cutoff-56 estimator

La conclusión del memo responde a prompting: se ensayó y es factible; la adopción de un LLM externo es una decisión posterior de costo-beneficio con la Universidad. El consumo experimental medido no sustituye una estimación de escala productiva.

Detalle: [auditoria-rubrica.json](auditoria-rubrica.json). Artefactos: [auditoria-modelos.json](auditoria-modelos.json). Ejecución: `scripts/auditar_entrega.py` desde el entorno propio de `pset_3` y con el servidor/snapshot privados disponibles.
