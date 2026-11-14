with e as (
    select count(*) as n, count_if(is_imd_missing) as missing_imd
    from {{ ref('slv_enrollments') }}
), r as (
    select count(*) as n, count_if(is_registration_missing) as missing_registration,
           count_if(is_registration_after_start) as late_registration,
           count_if(is_registered_at_start) as registered_at_start,
           count_if(is_registered_at_start and date_unregistration <= 0) as withdrawn_by_start
    from {{ ref('slv_registration') }}
), o as (
    select count(*) as n, count_if(target_class='Fail') as fail_count,
           count_if(target_class='Withdrawn') as withdrawn_count,
           count_if(target_class='Approved') as approved_count,
           count_if(is_withdrawn_without_date) as withdrawn_without_date,
           count_if(is_other_outcome_with_withdrawal) as other_outcome_with_date
    from {{ ref('slv_outcomes') }}
), a as (
    select count(*) as n, sum(click_count) as clicks, sum(source_row_count) as source_rows,
           sum(source_row_count - 1) as natural_excess,
           sum(source_row_count - distinct_source_value_count) as exact_excess,
           count_if(source_row_count > 1) as multiple_source_groups,
           count_if(is_prestart_activity) as prestart_groups,
           sum(case when is_prestart_activity then click_count else 0 end) as prestart_clicks
    from {{ ref('slv_activity_daily') }}
), sensitivity as (
    -- Equivale mecánicamente a colapsar observaciones fuente idénticas.
    -- Solo métrica: no sustituye la suma principal ni prueba error de captura.
    select sum(distinct_clicks) as clicks_if_exact_deduplicated
    from (
        select sum(distinct sum_click) as distinct_clicks
        from {{ ref('stg_student_vle') }}
        group by code_module, code_presentation, id_student, id_site, date
    )
), coverage as (
    select count(*) as n, count_if(a.enrollment_key is null) as no_activity,
           count_if(r.is_registered_at_start and a.enrollment_key is null) as initial_no_activity
    from {{ ref('slv_enrollments') }} e
    left join {{ ref('slv_registration') }} r on e.enrollment_key = r.enrollment_key
    left join (select distinct enrollment_key from {{ ref('slv_activity_daily') }}) a
        on e.enrollment_key = a.enrollment_key
), resources as (
    select count(*) as n, count_if(is_schedule_unknown) as unknown_schedule
    from {{ ref('slv_resources') }}
), editions as (select count(*) as n from {{ ref('slv_editions') }})
select 'enrollments' as dataset, 'rows' as metric, n as value, n as denominator from e
union all select 'enrollments', 'missing_imd', missing_imd, n from e
union all select 'registration', 'rows', n, n from r
union all select 'registration', 'missing_registration', missing_registration, n from r
union all select 'registration', 'late_registration', late_registration, n from r
union all select 'registration', 'registered_at_start', registered_at_start, n from r
union all select 'registration', 'withdrawn_by_start', withdrawn_by_start, registered_at_start from r
union all select 'outcomes', 'rows', n, n from o
union all select 'outcomes', 'Fail', fail_count, n from o
union all select 'outcomes', 'Withdrawn', withdrawn_count, n from o
union all select 'outcomes', 'Approved', approved_count, n from o
union all select 'outcomes', 'withdrawn_without_date', withdrawn_without_date, n from o
union all select 'outcomes', 'other_outcome_with_date', other_outcome_with_date, n from o
union all select 'activity_daily', 'rows', n, n from a
union all select 'activity_daily', 'clicks', clicks, null from a
union all select 'activity_daily', 'source_rows', source_rows, null from a
union all select 'activity_daily', 'natural_key_excess', natural_excess, source_rows from a
union all select 'activity_daily', 'exact_value_excess', exact_excess, source_rows from a
union all select 'activity_daily', 'multiple_source_groups', multiple_source_groups, n from a
union all select 'activity_daily', 'prestart_groups', prestart_groups, n from a
union all select 'activity_daily', 'prestart_clicks', prestart_clicks, clicks from a
union all select 'sensitivity', 'clicks_if_exact_deduplicated', clicks_if_exact_deduplicated, null from sensitivity
union all select 'enrollments', 'without_activity', no_activity, n from coverage
union all select 'enrollments', 'registered_at_start_without_activity', initial_no_activity, n from coverage
union all select 'resources', 'rows', n, n from resources
union all select 'resources', 'unknown_schedule', unknown_schedule, n from resources
union all select 'editions', 'rows', n, n from editions
