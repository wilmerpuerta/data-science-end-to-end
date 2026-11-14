{{ config(tags=['gold']) }}
with observed as (
    select count(*) as n,min(relative_day) as lo,max(relative_day) as hi,
           count_if(is_observation_cutoff) as cutoffs,
           count_if(is_observation_cutoff and relative_day in (14,28,42,56)) as expected_cutoffs
    from {{ ref('dim_relative_day') }}
)
select 'range_or_cutoffs' as problem from observed
where n <> hi-lo+1 or lo > 0 or hi < 56 or cutoffs <> 4 or expected_cutoffs <> 4
