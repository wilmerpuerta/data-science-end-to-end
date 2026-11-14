{{ config(tags=['silver']) }}
select enrollment_key
from {{ ref('slv_registration') }}
where is_registered_at_start is distinct from coalesce(date_registration <= 0, false)
   or is_registration_missing is distinct from (date_registration is null)
   or is_registration_after_start is distinct from coalesce(date_registration > 0, false)
   or has_no_recorded_withdrawal is distinct from (date_unregistration is null)
   or (case when is_registration_missing then 1 else 0 end
       + case when is_registration_after_start then 1 else 0 end
       + case when is_registered_at_start then 1 else 0 end) <> 1
