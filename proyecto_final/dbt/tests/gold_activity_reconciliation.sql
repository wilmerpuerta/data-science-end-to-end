{{ config(tags=['gold']) }}
with before_gold as (
    select code_module,code_presentation,count(*) as n,sum(click_count) as clicks,
           sum(source_row_count) as source_rows
    from {{ ref('slv_activity_daily') }} group by code_module,code_presentation
), after_gold as (
    select code_module,code_presentation,count(*) as n,sum(click_count) as clicks,
           sum(source_row_count) as source_rows
    from {{ ref('fact_activity_daily') }} group by code_module,code_presentation
)
select coalesce(b.code_module,a.code_module) as code_module,
       coalesce(b.code_presentation,a.code_presentation) as code_presentation
from before_gold b full outer join after_gold a using(code_module,code_presentation)
where b.n is distinct from a.n or b.clicks is distinct from a.clicks
   or b.source_rows is distinct from a.source_rows
