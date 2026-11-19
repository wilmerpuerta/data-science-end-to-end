-- Verificación de metadatos. No consulta tablas de datos ni reanuda el warehouse.
-- Ejecutar después de 01_aprovisionar.sql, en la misma cuenta.

USE ROLE SYSADMIN;
SHOW WAREHOUSES LIKE 'PSET2_WH';
SHOW PARAMETERS LIKE 'STATEMENT_TIMEOUT_IN_SECONDS' IN WAREHOUSE PSET2_WH;
SHOW SCHEMAS IN DATABASE PSET2_OULAD;
SHOW GRANTS TO ROLE PSET2_PIPELINE;

USE ROLE PSET2_PIPELINE;
USE DATABASE PSET2_OULAD;
USE SCHEMA RAW;
SELECT CURRENT_ROLE() AS rol_activo;
SHOW SCHEMAS IN DATABASE PSET2_OULAD;

-- Comprobar en Snowsight:
-- 1. PSET2_WH: X-Small, estado SUSPENDED, auto_suspend 60, auto_resume true.
-- 2. STATEMENT_TIMEOUT_IN_SECONDS: 600.
-- 3. RAW, BRONZE, SILVER, GOLD y ANALYTICS presentes; PUBLIC/INFORMATION_SCHEMA
--    son esquemas estándar adicionales, no capas del pipeline.
-- 4. Rol PSET2_PIPELINE utilizable y grants limitados a recursos del proyecto.
-- 5. ANALYTICS es el esquema destino previsto de la OBT matrícula-corte.
-- Esta verificación no prueba autenticación externa, dbt, Spark ni ingesta.
