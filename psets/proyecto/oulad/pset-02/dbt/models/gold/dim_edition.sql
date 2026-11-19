select edition_key, code_module, code_presentation, module_presentation_length,
       source_sha256, source_row_number, load_run_id, loaded_at
from {{ ref('slv_editions') }}
