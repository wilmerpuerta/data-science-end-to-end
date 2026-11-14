-- Solo identidad: no fusionar atributos de matrículas distintas.
select distinct id_student
from {{ ref('slv_enrollments') }}
