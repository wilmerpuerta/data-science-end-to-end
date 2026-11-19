{{ config(tags=['silver']) }}
select enrollment_key, resource_key, activity_day
from {{ ref('slv_activity_daily') }}
where click_count < 0 or source_row_count < 1 or source_version_count <> 1
   or distinct_source_value_count < 1 or distinct_source_value_count > source_row_count
   or source_min_row_number < 1 or source_max_row_number < source_min_row_number
   or is_prestart_activity is distinct from (activity_day < 0)
