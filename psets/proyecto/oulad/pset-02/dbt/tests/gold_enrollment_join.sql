{{ config(tags=['gold']) }}
with original as (
    select edition_key,count(*) as n from {{ ref('slv_enrollments') }} group by edition_key
), joined as (
    select f.edition_key,count(*) as n,sum(f.enrollment_count) as enrollments
    from {{ ref('fact_enrollment') }} f
    join {{ ref('dim_student') }} s on f.id_student=s.id_student
    join {{ ref('dim_edition') }} e on f.edition_key=e.edition_key
    join {{ ref('dim_enrollment') }} c on f.enrollment_key=c.enrollment_key
    group by f.edition_key
)
select coalesce(o.edition_key,j.edition_key) as edition_key
from original o full outer join joined j using(edition_key)
where o.n is distinct from j.n or o.n is distinct from j.enrollments
