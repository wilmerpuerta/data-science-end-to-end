-- Diagnóstico de visibilidad. No crea objetos ni concede permisos.
-- Ejecutar cada bloque completo y en orden, en una worksheet SQL nueva.
-- Si el contexto de la interfaz apunta a una base inexistente, quitar esa
-- selección de base/esquema antes de ejecutar. No seleccionar PSET2_OULAD
-- como contexto hasta confirmar que existe y es accesible.

-- Bloque A: visibilidad administrativa.
USE ROLE ACCOUNTADMIN;
SHOW DATABASES LIKE 'PSET2_OULAD';

-- Bloque B: visibilidad con el rol que crea la base en 01_aprovisionar.sql.
USE ROLE SYSADMIN;
SHOW DATABASES LIKE 'PSET2_OULAD';

-- Interpretación: buscar una fila con nombre EXACTO PSET2_OULAD.
-- Ausente en ambos: comprobar cuenta y ejecución de CREATE DATABASE en 01.
-- Visible solo en A: revisar propietario y grants antes de modificar permisos.
-- Visible en ambos: revisar la sentencia fallida, su rol y sesión concretos.
-- El diagnóstico cambia el rol de la sesión; no demuestra acceso del pipeline.
