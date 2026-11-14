with typed as (
    select
        {{ integer_or_null('id_site') }} as id_site,
        nullif(trim(code_module), '') as code_module,
        nullif(trim(code_presentation), '') as code_presentation,
        nullif(trim(activity_type), '') as activity_type,
        {{ integer_or_null('week_from') }} as week_from,
        {{ integer_or_null('week_to') }} as week_to,
        source_sha256,
        source_row_number,
        load_run_id,
        loaded_at,
        ({{ invalid_integer('id_site') }} or {{ invalid_integer('week_from') }} or {{ invalid_integer('week_to') }}) as has_type_error
    from {{ source('oulad_raw', 'vle') }}
)
select *,
    concat_ws('|', code_module, code_presentation) as edition_key,
    concat_ws('|', code_module, code_presentation, id_site) as resource_key
from typed
