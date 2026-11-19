-- Fechas para elegibilidad posterior. No unir retiro futuro a features.
select enrollment_key, edition_key, id_student, code_module, code_presentation,
       date_registration, date_unregistration,
       (date_registration is null) as is_registration_missing,
       coalesce(date_registration > 0, false) as is_registration_after_start,
       coalesce(date_registration <= 0, false) as is_registered_at_start,
       (date_unregistration is null) as has_no_recorded_withdrawal,
       case when date_registration is null then 'missing_registration'
            when date_registration > 0 then 'registered_after_start'
            else 'registered_by_start' end as initial_registration_status,
       source_sha256, source_row_number, load_run_id, loaded_at
from {{ ref('stg_student_registration') }}
