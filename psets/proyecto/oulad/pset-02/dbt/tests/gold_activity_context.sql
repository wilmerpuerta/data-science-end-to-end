{{ config(tags=['gold']) }}
-- Una FK válida por sí sola no prueba que pertenezca a la misma matrícula/edición.
select a.enrollment_key,a.resource_key,a.activity_day
from {{ ref('fact_activity_daily') }} a
join {{ ref('dim_enrollment') }} c on a.enrollment_key=c.enrollment_key
join {{ ref('dim_resource') }} r on a.resource_key=r.resource_key
where a.id_student is distinct from c.id_student
   or a.edition_key is distinct from c.edition_key
   or a.edition_key is distinct from r.edition_key
   or a.id_site is distinct from r.id_site
   or a.code_module is distinct from c.code_module
   or a.code_presentation is distinct from c.code_presentation
