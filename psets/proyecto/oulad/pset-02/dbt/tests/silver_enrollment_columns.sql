{{ config(tags=['silver']) }}
-- ref registra la dependencia; no consultar columnas de resultados para features.
-- depends_on: {{ ref('slv_enrollments') }}
select column_name
from {{ target.database }}.information_schema.columns
where table_schema = 'SILVER' and table_name = 'SLV_ENROLLMENTS'
  and column_name not in (
    'ENROLLMENT_KEY','EDITION_KEY','ID_STUDENT','CODE_MODULE','CODE_PRESENTATION',
    'GENDER','REGION','HIGHEST_EDUCATION','IMD_BAND','AGE_BAND',
    'NUM_OF_PREV_ATTEMPTS','STUDIED_CREDITS','DISABILITY','IS_IMD_MISSING',
    'SOURCE_SHA256','SOURCE_ROW_NUMBER','LOAD_RUN_ID','LOADED_AT'
  )
