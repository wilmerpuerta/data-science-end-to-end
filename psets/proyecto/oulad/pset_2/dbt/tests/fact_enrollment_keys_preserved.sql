{{ config(tags=['gold']) }}
with missing as (
 select enrollment_key from {{ ref('slv_enrollments') }}
 minus select enrollment_key from {{ ref('fact_enrollment') }}
), extra as (
 select enrollment_key from {{ ref('fact_enrollment') }}
 minus select enrollment_key from {{ ref('slv_enrollments') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
