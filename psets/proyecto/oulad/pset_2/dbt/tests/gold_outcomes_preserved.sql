{{ config(tags=['gold']) }}
with before_gold as (
    select edition_key,final_result,target_class,count(*) as n
    from {{ ref('slv_outcomes') }} group by edition_key,final_result,target_class
), after_gold as (
    select f.edition_key,o.final_result,o.target_class,count(*) as n
    from {{ ref('outcome_enrollment') }} o
    join {{ ref('fact_enrollment') }} f on o.enrollment_key=f.enrollment_key
    group by f.edition_key,o.final_result,o.target_class
)
select coalesce(b.edition_key,a.edition_key) as edition_key,
       coalesce(b.final_result,a.final_result) as final_result
from before_gold b full outer join after_gold a using(edition_key,final_result,target_class)
where b.n is distinct from a.n
