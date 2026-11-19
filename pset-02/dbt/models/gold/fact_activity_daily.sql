select enrollment_key, edition_key, resource_key, id_student, id_site,
       code_module, code_presentation, activity_day,
       click_count, source_row_count, distinct_source_value_count,
       source_sha256, source_version_count, source_min_row_number, source_max_row_number
from {{ ref('slv_activity_daily') }}
