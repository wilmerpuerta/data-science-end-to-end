-- Uso retrospectivo. Nunca usar estas columnas para predecir ni fijar cortes.
select i.enrollment_key, i.edition_key, i.id_student, i.code_module, i.code_presentation,
       i.final_result,
       case when i.final_result in ('Pass', 'Distinction') then 'Approved'
            else i.final_result end as target_class,
       (i.final_result = 'Fail') as target_fail,
       (i.final_result = 'Withdrawn' and r.date_unregistration is null) as is_withdrawn_without_date,
       (i.final_result <> 'Withdrawn' and r.date_unregistration is not null) as is_other_outcome_with_withdrawal,
       i.source_sha256 as info_source_sha256,
       i.source_row_number as info_source_row_number,
       r.source_sha256 as registration_source_sha256,
       r.source_row_number as registration_source_row_number
from {{ ref('stg_student_info') }} i
left join {{ ref('slv_registration') }} r on i.enrollment_key = r.enrollment_key
