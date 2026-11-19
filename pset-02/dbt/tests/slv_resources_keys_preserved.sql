{{ config(tags=['silver']) }}
with missing as (
 select resource_key from {{ ref('stg_vle') }}
 minus select resource_key from {{ ref('slv_resources') }}
), extra as (
 select resource_key from {{ ref('slv_resources') }}
 minus select resource_key from {{ ref('stg_vle') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
