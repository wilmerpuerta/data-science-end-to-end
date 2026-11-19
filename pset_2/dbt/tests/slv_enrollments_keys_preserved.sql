{{ config(tags=['silver']) }}
with missing as (
 select enrollment_key from {{ ref('stg_student_info') }}
 minus select enrollment_key from {{ ref('slv_enrollments') }}
), extra as (
 select enrollment_key from {{ ref('slv_enrollments') }}
 minus select enrollment_key from {{ ref('stg_student_info') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
