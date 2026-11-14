with bounds as (
    select least(coalesce(min(activity_day),0),0) as lo,
           greatest(coalesce(max(activity_day),56),56) as hi
    from {{ ref('slv_activity_daily') }}
), days as (
    select f.value::integer as relative_day
    from bounds, lateral flatten(input => array_generate_range(lo::integer,(hi+1)::integer)) f
)
select relative_day, (relative_day < 0) as is_prestart,
       (relative_day = 0) as is_start_day,
       (relative_day in (14,28,42,56)) as is_observation_cutoff,
       case when relative_day between 1 and 14 then 1
            when relative_day between 15 and 28 then 2
            when relative_day between 29 and 42 then 3
            when relative_day between 43 and 56 then 4 end as early_window_index
from days
