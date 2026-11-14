select resource_key, edition_key, id_site, code_module, code_presentation,
       activity_type, week_from, week_to,
       (week_from is null or week_to is null) as is_schedule_unknown,
       source_sha256, source_row_number, load_run_id, loaded_at
from {{ ref('stg_vle') }}
