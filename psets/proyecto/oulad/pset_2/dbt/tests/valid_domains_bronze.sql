{{ config(tags=['bronze']) }}
select dataset, metric, value
from {{ ref('dq_bronze_profile') }}
where metric in ('negative_clicks', 'invalid_background', 'reversed_weeks', 'invalid_duration')
  and value <> 0
