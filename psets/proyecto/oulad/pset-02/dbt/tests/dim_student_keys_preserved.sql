{{ config(tags=['gold']) }}
with missing as (
 select id_student from {{ ref('slv_enrollments') }}
 minus select id_student from {{ ref('dim_student') }}
), extra as (
 select id_student from {{ ref('dim_student') }}
 minus select id_student from {{ ref('slv_enrollments') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
