{{ config(tags=['gold']) }}
with missing as (
 select enrollment_key from {{ ref('slv_registration') }}
 minus select enrollment_key from {{ ref('enrollment_withdrawal') }}
), extra as (
 select enrollment_key from {{ ref('enrollment_withdrawal') }}
 minus select enrollment_key from {{ ref('slv_registration') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
