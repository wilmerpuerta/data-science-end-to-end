select e.enrollment_key, e.edition_key, e.id_student,
       1::integer as enrollment_count,
       r.date_registration, r.is_registration_missing,
       r.is_registration_after_start, r.is_registered_at_start,
       r.initial_registration_status,
       e.source_sha256 as info_source_sha256,
       e.source_row_number as info_source_row_number,
       r.source_sha256 as registration_source_sha256,
       r.source_row_number as registration_source_row_number
from {{ ref('slv_enrollments') }} e
left join {{ ref('slv_registration') }} r on e.enrollment_key = r.enrollment_key
