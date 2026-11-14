{{ config(tags=['bronze']) }}
select 'type_error' as problem, count(*) as failures
from {{ ref('stg_student_vle') }} where has_type_error having count(*) > 0
union all
select 'row_count', abs((select count(*) from {{ ref('stg_student_vle') }}) - (select count(*) from {{ source('oulad_raw', 'studentvle') }})) as failures
where failures > 0
