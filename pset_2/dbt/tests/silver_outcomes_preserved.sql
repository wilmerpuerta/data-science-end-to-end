{{ config(tags=['silver']) }}
-- Clases por edición: una unión no puede multiplicar ni perder etiquetas.
with before_join as (
    select code_module, code_presentation, final_result, count(*) as n
    from {{ ref('stg_student_info') }}
    group by code_module,code_presentation,final_result
), after_join as (
    select code_module, code_presentation, final_result, count(*) as n
    from {{ ref('slv_outcomes') }}
    group by code_module,code_presentation,final_result
)
select coalesce(b.code_module,a.code_module) as code_module,
       coalesce(b.code_presentation,a.code_presentation) as code_presentation,
       coalesce(b.final_result,a.final_result) as final_result
from before_join b full outer join after_join a
  using(code_module,code_presentation,final_result)
where b.n is distinct from a.n
