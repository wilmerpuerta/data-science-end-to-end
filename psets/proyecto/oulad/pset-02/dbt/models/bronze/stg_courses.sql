with typed as (
    select
        nullif(trim(code_module), '') as code_module,
        nullif(trim(code_presentation), '') as code_presentation,
        {{ integer_or_null('module_presentation_length') }} as module_presentation_length,
        source_sha256,
        source_row_number,
        load_run_id,
        loaded_at,
        ({{ invalid_integer('module_presentation_length') }}) as has_type_error
    from {{ source('oulad_raw', 'courses') }}
)
select *,
    concat_ws('|', code_module, code_presentation) as edition_key
from typed
