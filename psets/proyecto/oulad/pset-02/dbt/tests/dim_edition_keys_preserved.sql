{{ config(tags=['gold']) }}
with missing as (
 select edition_key from {{ ref('slv_editions') }}
 minus select edition_key from {{ ref('dim_edition') }}
), extra as (
 select edition_key from {{ ref('dim_edition') }}
 minus select edition_key from {{ ref('slv_editions') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
