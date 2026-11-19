{{ config(tags=['silver']) }}
with missing as (
 select edition_key from {{ ref('stg_courses') }}
 minus select edition_key from {{ ref('slv_editions') }}
), extra as (
 select edition_key from {{ ref('slv_editions') }}
 minus select edition_key from {{ ref('stg_courses') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
