{{ config(tags=['gold']) }}
select f.enrollment_key
from {{ ref('fact_enrollment') }} f
join {{ ref('dim_enrollment') }} c on f.enrollment_key=c.enrollment_key
where f.id_student is distinct from c.id_student
   or f.edition_key is distinct from c.edition_key
