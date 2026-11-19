{{ config(tags=['silver']) }}
-- Comparación por edición: evita que pérdidas y duplicaciones se compensen
-- entre distintas ediciones aunque el total global coincida.
with original as (
    select code_module, code_presentation, count(*) as n_rows,
           sum(sum_click) as clicks,
           count(distinct id_student, id_site, date) as daily_keys
    from {{ ref('stg_student_vle') }}
    group by code_module, code_presentation
), consolidated as (
    select code_module, code_presentation, count(*) as daily_keys,
           sum(source_row_count) as n_rows, sum(click_count) as clicks
    from {{ ref('slv_activity_daily') }}
    group by code_module, code_presentation
)
select coalesce(o.code_module,s.code_module) as code_module,
       coalesce(o.code_presentation,s.code_presentation) as code_presentation
from original o
full outer join consolidated s using (code_module,code_presentation)
where o.n_rows is distinct from s.n_rows
   or o.clicks is distinct from s.clicks
   or o.daily_keys is distinct from s.daily_keys
