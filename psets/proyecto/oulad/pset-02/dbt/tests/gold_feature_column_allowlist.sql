{{ config(tags=['gold']) }}
-- depends_on: {{ ref('dim_student') }}
-- depends_on: {{ ref('dim_enrollment') }}
-- depends_on: {{ ref('fact_enrollment') }}
-- depends_on: {{ ref('fact_activity_daily') }}
select table_name,column_name
from {{ target.database }}.information_schema.columns
where table_schema='GOLD'
  and table_name in ('DIM_STUDENT','DIM_ENROLLMENT','FACT_ENROLLMENT','FACT_ACTIVITY_DAILY')
  and not (
      (table_name='DIM_STUDENT' and column_name='ID_STUDENT')
      or (table_name='DIM_ENROLLMENT' and column_name in (
          'ENROLLMENT_KEY','EDITION_KEY','ID_STUDENT','CODE_MODULE','CODE_PRESENTATION',
          'GENDER','REGION','HIGHEST_EDUCATION','IMD_BAND','AGE_BAND','NUM_OF_PREV_ATTEMPTS',
          'STUDIED_CREDITS','DISABILITY','IS_IMD_MISSING','SOURCE_SHA256','SOURCE_ROW_NUMBER','LOAD_RUN_ID','LOADED_AT'))
      or (table_name='FACT_ENROLLMENT' and column_name in (
          'ENROLLMENT_KEY','EDITION_KEY','ID_STUDENT','ENROLLMENT_COUNT','DATE_REGISTRATION',
          'IS_REGISTRATION_MISSING','IS_REGISTRATION_AFTER_START','IS_REGISTERED_AT_START',
          'INITIAL_REGISTRATION_STATUS','INFO_SOURCE_SHA256','INFO_SOURCE_ROW_NUMBER',
          'REGISTRATION_SOURCE_SHA256','REGISTRATION_SOURCE_ROW_NUMBER'))
      or (table_name='FACT_ACTIVITY_DAILY' and column_name in (
          'ENROLLMENT_KEY','EDITION_KEY','RESOURCE_KEY','ID_STUDENT','ID_SITE','CODE_MODULE','CODE_PRESENTATION',
          'ACTIVITY_DAY','CLICK_COUNT','SOURCE_ROW_COUNT','DISTINCT_SOURCE_VALUE_COUNT',
          'SOURCE_SHA256','SOURCE_VERSION_COUNT','SOURCE_MIN_ROW_NUMBER','SOURCE_MAX_ROW_NUMBER'))
  )
