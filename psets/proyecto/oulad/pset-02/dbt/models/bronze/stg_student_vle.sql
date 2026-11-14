with typed as (
    select
        nullif(trim(code_module), '') as code_module,
        nullif(trim(code_presentation), '') as code_presentation,
        {{ integer_or_null('id_student') }} as id_student,
        {{ integer_or_null('id_site') }} as id_site,
        {{ integer_or_null('date') }} as date,
        {{ integer_or_null('sum_click') }} as sum_click,
        source_sha256,
        source_row_number,
        load_run_id,
        loaded_at,
        ({{ invalid_integer('id_student') }} or {{ invalid_integer('id_site') }} or {{ invalid_integer('date') }} or {{ invalid_integer('sum_click') }}) as has_type_error
    from {{ source('oulad_raw', 'studentvle') }}
)
select *,
    concat_ws('|', code_module, code_presentation) as edition_key,
    concat_ws('|', code_module, code_presentation, id_student) as enrollment_key,
    concat_ws('|', code_module, code_presentation, id_site) as resource_key
from typed
