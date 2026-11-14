-- Consolidación aditiva. No usar DISTINCT sobre las observaciones fuente.
with grouped as (
    select code_module, code_presentation, id_student, id_site, date as activity_day,
           sum(sum_click) as click_count,
           count(*) as source_row_count,
           count(distinct sum_click) as distinct_source_value_count,
           min(source_sha256) as source_sha256,
           count(distinct source_sha256) as source_version_count,
           min(source_row_number) as source_min_row_number,
           max(source_row_number) as source_max_row_number
    from {{ ref('stg_student_vle') }}
    group by code_module, code_presentation, id_student, id_site, date
)
select *, concat_ws('|', code_module, code_presentation) as edition_key,
       concat_ws('|', code_module, code_presentation, id_student) as enrollment_key,
       concat_ws('|', code_module, code_presentation, id_site) as resource_key,
       (activity_day < 0) as is_prestart_activity
from grouped
