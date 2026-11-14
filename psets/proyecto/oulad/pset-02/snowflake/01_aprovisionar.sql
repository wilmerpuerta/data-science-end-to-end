-- Ejecutar en una worksheet SQL de Snowsight, en orden y en la misma sesión.
-- Requiere SECURITYADMIN y SYSADMIN. No incluye usuarios ni credenciales reales.
-- No ejecutar sobre recursos homónimos de otros proyectos: revisar antes.
-- DDL confirma cambios por sentencia; si una falla, detenerse y revisar.
-- Usar Run All/Ejecutar todo o ejecutar cada sentencia desde el inicio en orden.
-- Ejecutar solo la sentencia bajo el cursor puede omitir CREATE DATABASE.

USE ROLE SECURITYADMIN;

CREATE ROLE IF NOT EXISTS PSET2_PIPELINE
    COMMENT = 'Rol de ejecucion del pipeline academico OULAD';

GRANT ROLE PSET2_PIPELINE TO ROLE SYSADMIN;

-- Asignar al usuario autenticado sin guardar su nombre en el repositorio.
-- Ejecutar TODO el bloque $$ como una sola sentencia. Las variables de
-- Scripting admiten CURRENT_USER(); no usar SET de sesión para esta expresión.
-- Citar el identificador conserva puntos, espacios y mayúsculas del usuario.
EXECUTE IMMEDIATE $$
DECLARE
    operator_name VARCHAR;
    grant_statement VARCHAR;
BEGIN
    operator_name := CURRENT_USER();
    grant_statement := 'GRANT ROLE PSET2_PIPELINE TO USER "'
        || REPLACE(operator_name, '"', '""') || '"';
    EXECUTE IMMEDIATE grant_statement;
    RETURN 'Rol PSET2_PIPELINE asignado al usuario de la sesion';
END;
$$;

USE ROLE SYSADMIN;

CREATE WAREHOUSE IF NOT EXISTS PSET2_WH
    WAREHOUSE_TYPE = STANDARD
    WAREHOUSE_SIZE = XSMALL
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    STATEMENT_TIMEOUT_IN_SECONDS = 600
    COMMENT = 'PSet 2 OULAD: ejecucion controlada';

CREATE DATABASE IF NOT EXISTS PSET2_OULAD
    COMMENT = 'Capas del pipeline academico OULAD';

CREATE SCHEMA IF NOT EXISTS PSET2_OULAD.RAW;
CREATE SCHEMA IF NOT EXISTS PSET2_OULAD.BRONZE;
CREATE SCHEMA IF NOT EXISTS PSET2_OULAD.SILVER;
CREATE SCHEMA IF NOT EXISTS PSET2_OULAD.GOLD;
CREATE SCHEMA IF NOT EXISTS PSET2_OULAD.ANALYTICS;

GRANT USAGE ON WAREHOUSE PSET2_WH TO ROLE PSET2_PIPELINE;
GRANT USAGE ON DATABASE PSET2_OULAD TO ROLE PSET2_PIPELINE;

GRANT USAGE, CREATE TABLE, CREATE STAGE, CREATE FILE FORMAT
    ON SCHEMA PSET2_OULAD.RAW TO ROLE PSET2_PIPELINE;
GRANT USAGE, CREATE TABLE, CREATE VIEW
    ON SCHEMA PSET2_OULAD.BRONZE TO ROLE PSET2_PIPELINE;
GRANT USAGE, CREATE TABLE, CREATE VIEW
    ON SCHEMA PSET2_OULAD.SILVER TO ROLE PSET2_PIPELINE;
GRANT USAGE, CREATE TABLE, CREATE VIEW
    ON SCHEMA PSET2_OULAD.GOLD TO ROLE PSET2_PIPELINE;
GRANT USAGE, CREATE TABLE, CREATE STAGE, CREATE FILE FORMAT
    ON SCHEMA PSET2_OULAD.ANALYTICS TO ROLE PSET2_PIPELINE;

-- Los objetos del pipeline deberán crearse con PSET2_PIPELINE para que ese rol
-- conserve su propiedad. No se otorgan privilegios globales ni sobre datos ajenos.
-- Se revisarán los privilegios si los conectores probados requieren otros.
-- IF NOT EXISTS no reconcilia configuración de recursos preexistentes.
