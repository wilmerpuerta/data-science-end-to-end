{{ config(tags=['silver']) }}
-- Igualdad bidireccional de claves, además de los conteos y totales.
with missing as (
    select code_module,code_presentation,id_student,id_site,date as activity_day
    from {{ ref('stg_student_vle') }}
    minus
    select code_module,code_presentation,id_student,id_site,activity_day
    from {{ ref('slv_activity_daily') }}
), extra as (
    select code_module,code_presentation,id_student,id_site,activity_day
    from {{ ref('slv_activity_daily') }}
    minus
    select code_module,code_presentation,id_student,id_site,date as activity_day
    from {{ ref('stg_student_vle') }}
)
select 'missing' as problem, * from missing
union all select 'extra', * from extra
