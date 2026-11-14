with typed as (
    select
        nullif(trim(code_module), '') as code_module,
        nullif(trim(code_presentation), '') as code_presentation,
        {{ integer_or_null('id_student') }} as id_student,
        {{ integer_or_null('date_registration') }} as date_registration,
        {{ integer_or_null('date_unregistration') }} as date_unregistration,
        source_sha256,
        source_row_number,
        load_run_id,
        loaded_at,
        ({{ invalid_integer('id_student') }} or {{ invalid_integer('date_registration') }} or {{ invalid_integer('date_unregistration') }}) as has_type_error
    from {{ source('oulad_raw', 'studentregistration') }}
)
select *,
    concat_ws('|', code_module, code_presentation) as edition_key,
    concat_ws('|', code_module, code_presentation, id_student) as enrollment_key
from typed
