-- Contexto para elegibilidad as-of. No es un predictor ni una etiqueta imputada.
select enrollment_key, date_unregistration, has_no_recorded_withdrawal,
       source_sha256, source_row_number, load_run_id, loaded_at
from {{ ref('slv_registration') }}
