with students as (select count(*) as n from {{ ref('dim_student') }}),
editions as (select count(*) as n from {{ ref('dim_edition') }}),
resources as (select count(*) as n from {{ ref('dim_resource') }}),
contexts as (select count(*) as n from {{ ref('dim_enrollment') }}),
days as (
    select count(*) as n, min(relative_day) as min_day, max(relative_day) as max_day,
           count_if(is_observation_cutoff) as cutoffs
    from {{ ref('dim_relative_day') }}
), enrollment as (
    select count(*) as n, sum(enrollment_count) as enrollments,
           count_if(is_registered_at_start) as registered_at_start
    from {{ ref('fact_enrollment') }}
), activity as (
    select count(*) as n, sum(click_count) as clicks, sum(source_row_count) as source_rows
    from {{ ref('fact_activity_daily') }}
), joined_activity as (
    select count(*) as n, sum(a.click_count) as clicks
    from {{ ref('fact_activity_daily') }} a
    join {{ ref('dim_student') }} s on a.id_student = s.id_student
    join {{ ref('dim_edition') }} e on a.edition_key = e.edition_key
    join {{ ref('dim_resource') }} r on a.resource_key = r.resource_key
    join {{ ref('dim_enrollment') }} c on a.enrollment_key = c.enrollment_key
    join {{ ref('dim_relative_day') }} d on a.activity_day = d.relative_day
), no_activity as (
    select count(*) as n
    from {{ ref('fact_enrollment') }} e
    left join (select distinct enrollment_key from {{ ref('fact_activity_daily') }}) a
        on e.enrollment_key=a.enrollment_key
    where a.enrollment_key is null
), withdrawals as (select count(*) as n from {{ ref('enrollment_withdrawal') }}),
outcomes as (
    select count(*) as n, count_if(target_class='Fail') as fails,
           count_if(target_class='Withdrawn') as withdrawn, count_if(target_class='Approved') as approved
    from {{ ref('outcome_enrollment') }}
), eligible as (
    -- Referencia independiente para verificar después la población de Spark.
    -- Se forma sin consultar resultados finales.
    select d.relative_day as cutoff_day, count(*) as n
    from {{ ref('fact_enrollment') }} e
    join {{ ref('enrollment_withdrawal') }} w on e.enrollment_key = w.enrollment_key
    cross join {{ ref('dim_relative_day') }} d
    where d.is_observation_cutoff and e.date_registration <= 0
      and (w.date_unregistration is null or w.date_unregistration > d.relative_day)
    group by d.relative_day
)
select 'dim_student' as dataset, 'rows' as metric, n as value, n as denominator from students
union all select 'dim_edition','rows',n,n from editions
union all select 'dim_resource','rows',n,n from resources
union all select 'dim_enrollment','rows',n,n from contexts
union all select 'dim_relative_day','rows',n,n from days
union all select 'dim_relative_day','min_day',min_day,null from days
union all select 'dim_relative_day','max_day',max_day,null from days
union all select 'dim_relative_day','cutoffs',cutoffs,null from days
union all select 'fact_enrollment','rows',n,n from enrollment
union all select 'fact_enrollment','enrollment_count',enrollments,n from enrollment
union all select 'fact_enrollment','registered_at_start',registered_at_start,n from enrollment
union all select 'fact_activity_daily','rows',n,n from activity
union all select 'fact_activity_daily','clicks',clicks,null from activity
union all select 'fact_activity_daily','source_rows',source_rows,null from activity
union all select 'dimensional_join','rows',n,n from joined_activity
union all select 'dimensional_join','clicks',clicks,null from joined_activity
union all select 'fact_enrollment','without_activity',n,null from no_activity
union all select 'enrollment_withdrawal','rows',n,n from withdrawals
union all select 'outcome_enrollment','rows',n,n from outcomes
union all select 'outcome_enrollment','Fail',fails,n from outcomes
union all select 'outcome_enrollment','Withdrawn',withdrawn,n from outcomes
union all select 'outcome_enrollment','Approved',approved,n from outcomes
union all select 'eligibility_day_' || cutoff_day::varchar, 'expected_enrollments', n, null from eligible
