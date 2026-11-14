{{ config(tags=['gold']) }}
with missing as (
 select enrollment_key from {{ ref('slv_outcomes') }}
 minus select enrollment_key from {{ ref('outcome_enrollment') }}
), extra as (
 select enrollment_key from {{ ref('outcome_enrollment') }}
 minus select enrollment_key from {{ ref('slv_outcomes') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
