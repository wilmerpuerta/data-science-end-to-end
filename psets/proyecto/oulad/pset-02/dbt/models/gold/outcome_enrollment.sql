-- Uso retrospectivo: tabla separada del hecho y dimensiones de antecedentes.
select enrollment_key, final_result, target_class, target_fail,
       is_withdrawn_without_date, is_other_outcome_with_withdrawal,
       info_source_sha256, info_source_row_number,
       registration_source_sha256, registration_source_row_number
from {{ ref('slv_outcomes') }}
