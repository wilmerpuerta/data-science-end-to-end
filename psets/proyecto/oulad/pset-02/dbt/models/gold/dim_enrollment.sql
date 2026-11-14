-- Contexto observado por matrícula, sin resultado ni fecha de retiro.
select enrollment_key, edition_key, id_student, code_module, code_presentation,
       gender, region, highest_education, imd_band, age_band,
       num_of_prev_attempts, studied_credits, disability, is_imd_missing,
       source_sha256, source_row_number, load_run_id, loaded_at
from {{ ref('slv_enrollments') }}
