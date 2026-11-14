{{ config(tags=['silver']) }}
with missing as (
 select enrollment_key from {{ ref('stg_student_info') }}
 minus select enrollment_key from {{ ref('slv_outcomes') }}
), extra as (
 select enrollment_key from {{ ref('slv_outcomes') }}
 minus select enrollment_key from {{ ref('stg_student_info') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
