{{ config(tags=['silver']) }}
with missing as (
 select enrollment_key from {{ ref('stg_student_registration') }}
 minus select enrollment_key from {{ ref('slv_registration') }}
), extra as (
 select enrollment_key from {{ ref('slv_registration') }}
 minus select enrollment_key from {{ ref('stg_student_registration') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
