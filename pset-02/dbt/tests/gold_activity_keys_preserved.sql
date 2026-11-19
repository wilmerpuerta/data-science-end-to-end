{{ config(tags=['gold']) }}
with missing as (
    select code_module,code_presentation,id_student,id_site,activity_day
    from {{ ref('slv_activity_daily') }}
    minus
    select code_module,code_presentation,id_student,id_site,activity_day
    from {{ ref('fact_activity_daily') }}
), extra as (
    select code_module,code_presentation,id_student,id_site,activity_day
    from {{ ref('fact_activity_daily') }}
    minus
    select code_module,code_presentation,id_student,id_site,activity_day
    from {{ ref('slv_activity_daily') }}
)
select 'missing' as problem,* from missing
union all select 'extra',* from extra
