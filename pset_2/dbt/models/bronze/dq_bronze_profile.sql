{{ config(materialized='table') }}
-- Instantánea agregada de calidad: las cinco vistas no eliminan observaciones.
with info as (
    select count(*) as n_rows, count(distinct id_student) as people,
           count_if(imd_band is null) as missing_imd,
           count_if(studied_credits < 0 or num_of_prev_attempts < 0) as invalid_background
    from {{ ref('stg_student_info') }}
), registration as (
    select count(*) as n_rows, count_if(date_registration is null) as missing_registration,
           count_if(date_registration > 0) as late_registration,
           count_if(date_unregistration is null) as no_recorded_withdrawal,
           count_if(date_unregistration < date_registration) as withdrawal_before_registration
    from {{ ref('stg_student_registration') }}
), resources as (
    select count(*) as n_rows, count_if(week_from is null) as missing_week_from,
           count_if(week_to is null) as missing_week_to,
           count_if(week_from > week_to) as reversed_weeks
    from {{ ref('stg_vle') }}
), events as (
    select count(*) as n_rows, sum(sum_click) as total_clicks,
           count(distinct code_module,code_presentation,id_student,id_site,date) as natural_keys,
           count(distinct code_module,code_presentation,id_student,id_site,date,sum_click) as exact_values,
           count_if(date < 0) as prestart_rows, min(date) as min_day, max(date) as max_day,
           count_if(sum_click < 0) as negative_clicks, count_if(sum_click = 0) as zero_clicks
    from {{ ref('stg_student_vle') }}
), outcomes as (
    select count(*) as n_rows,
           count_if(i.final_result = 'Withdrawn' and r.date_unregistration is null) as withdrawn_without_date,
           count_if(i.final_result <> 'Withdrawn' and r.date_unregistration is not null) as other_outcome_with_date
    from {{ ref('stg_student_info') }} i
    join {{ ref('stg_student_registration') }} r using(enrollment_key)
), editions as (
    select count(*) as n_rows, count_if(module_presentation_length <= 0 or module_presentation_length is null) as invalid_duration
    from {{ ref('stg_courses') }}
)
select 'student_info' as dataset, 'rows' as metric, n_rows as value, n_rows as denominator from info
union all select 'student_info','unique_people',people,n_rows from info
union all select 'student_info','missing_imd',missing_imd,n_rows from info
union all select 'student_info','invalid_background',invalid_background,n_rows from info
union all select 'registration','rows',n_rows,n_rows from registration
union all select 'registration','missing_registration',missing_registration,n_rows from registration
union all select 'registration','late_registration',late_registration,n_rows from registration
union all select 'registration','no_recorded_withdrawal',no_recorded_withdrawal,n_rows from registration
union all select 'registration','withdrawal_before_registration',withdrawal_before_registration,n_rows from registration
union all select 'vle','rows',n_rows,n_rows from resources
union all select 'vle','missing_week_from',missing_week_from,n_rows from resources
union all select 'vle','missing_week_to',missing_week_to,n_rows from resources
union all select 'vle','reversed_weeks',reversed_weeks,n_rows from resources
union all select 'student_vle','rows',n_rows,n_rows from events
union all select 'student_vle','total_clicks',total_clicks,null from events
union all select 'student_vle','repeated_natural_key_excess',n_rows-natural_keys,n_rows from events
union all select 'student_vle','repeated_exact_value_excess',n_rows-exact_values,n_rows from events
union all select 'student_vle','prestart_rows',prestart_rows,n_rows from events
union all select 'student_vle','min_day',min_day,null from events
union all select 'student_vle','max_day',max_day,null from events
union all select 'student_vle','negative_clicks',negative_clicks,n_rows from events
union all select 'student_vle','zero_clicks',zero_clicks,n_rows from events
union all select 'outcomes','withdrawn_without_date',withdrawn_without_date,n_rows from outcomes
union all select 'outcomes','other_outcome_with_date',other_outcome_with_date,n_rows from outcomes
union all select 'courses','rows',n_rows,n_rows from editions
union all select 'courses','invalid_duration',invalid_duration,n_rows from editions
