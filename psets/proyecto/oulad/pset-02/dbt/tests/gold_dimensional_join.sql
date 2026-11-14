{{ config(tags=['gold']) }}
with original as (
    select edition_key,count(*) as n,sum(click_count) as clicks
    from {{ ref('fact_activity_daily') }} group by edition_key
), joined as (
    select a.edition_key,count(*) as n,sum(a.click_count) as clicks
    from {{ ref('fact_activity_daily') }} a
    join {{ ref('dim_student') }} s on a.id_student=s.id_student
    join {{ ref('dim_edition') }} e on a.edition_key=e.edition_key
    join {{ ref('dim_resource') }} r on a.resource_key=r.resource_key
    join {{ ref('dim_enrollment') }} c on a.enrollment_key=c.enrollment_key
    join {{ ref('dim_relative_day') }} d on a.activity_day=d.relative_day
    group by a.edition_key
)
select coalesce(o.edition_key,j.edition_key) as edition_key
from original o full outer join joined j using(edition_key)
where o.n is distinct from j.n or o.clicks is distinct from j.clicks
