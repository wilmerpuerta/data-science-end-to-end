{{ config(tags=['gold']) }}
with missing as (
 select resource_key from {{ ref('slv_resources') }}
 minus select resource_key from {{ ref('dim_resource') }}
), extra as (
 select resource_key from {{ ref('dim_resource') }}
 minus select resource_key from {{ ref('slv_resources') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
