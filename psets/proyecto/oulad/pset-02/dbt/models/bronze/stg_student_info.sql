with typed as (
    select
        nullif(trim(code_module), '') as code_module,
        nullif(trim(code_presentation), '') as code_presentation,
        {{ integer_or_null('id_student') }} as id_student,
        nullif(trim(gender), '') as gender,
        nullif(trim(region), '') as region,
        nullif(trim(highest_education), '') as highest_education,
        nullif(trim(imd_band), '') as imd_band,
        nullif(trim(age_band), '') as age_band,
        {{ integer_or_null('num_of_prev_attempts') }} as num_of_prev_attempts,
        {{ integer_or_null('studied_credits') }} as studied_credits,
        nullif(trim(disability), '') as disability,
        nullif(trim(final_result), '') as final_result,
        source_sha256,
        source_row_number,
        load_run_id,
        loaded_at,
        ({{ invalid_integer('id_student') }} or {{ invalid_integer('num_of_prev_attempts') }} or {{ invalid_integer('studied_credits') }}) as has_type_error
    from {{ source('oulad_raw', 'studentinfo') }}
)
select *,
    concat_ws('|', code_module, code_presentation) as edition_key,
    concat_ws('|', code_module, code_presentation, id_student) as enrollment_key
from typed
