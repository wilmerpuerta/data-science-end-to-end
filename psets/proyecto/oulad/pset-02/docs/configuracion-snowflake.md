# Preparación de Snowflake y recursos del proyecto

Estado: los resultados aportados confirman PSET2_OULAD y sus cinco esquemas, el warehouse suspendido STANDARD/X-Small, auto_suspend=60, auto_resume=true y el rol activo PSET2_PIPELINE. La autenticación externa de PSET2_SVC funcionó desde los clientes. Los permisos se comprobaron mediante carga Raw, builds Bronze/Silver/Gold y publicación OBT con Spark. El timeout del warehouse aún requiere evidencia específica. Este documento conserva el procedimiento de aprovisionamiento y sus incidencias. Ver [autenticación local](autenticacion-local.md) y [evidencia de ejecución](estado-ejecucion.md).

## 1. Confirmar el tipo de acceso

El autor confirmó permisos para crear recursos. El procedimiento siguiente utiliza SECURITYADMIN y SYSADMIN. Si alguno no está disponible, detenerse en esa sentencia y revisar la delegación de permisos; no reemplazarlo automáticamente por otro rol.

No usar ACCOUNTADMIN como rol de ejecución del pipeline. El aprovisionamiento administrativo y la operación del proyecto se documentarán por separado según los privilegios reales.

## 2. Preparar los recursos concretos

1. En Snowsight abrir una **worksheet SQL**. Revisar que los nombres PSET2_PIPELINE, PSET2_WH y PSET2_OULAD no correspondan a otros proyectos. Si ya existen y no son de este proyecto, no ejecutar: acordar nuevos nombres y adaptar todas las referencias.
2. Abrir [01_aprovisionar.sql](../snowflake/01_aprovisionar.sql), copiarlo en la worksheet y ejecutar sus sentencias en orden, en la misma sesión. Si falla una, detenerse y conservar solo el mensaje de error sin información privada para revisarlo.
3. Ejecutar [02_verificar_recursos.sql](../snowflake/02_verificar_recursos.sql). Comprobar los resultados según sus comentarios.

El diseño crea:

| Recurso | Configuración |
|---|---|
| Rol PSET2_PIPELINE | Ejecuta el pipeline; no administra usuarios ni la cuenta |
| Warehouse PSET2_WH | X-Small, inicialmente suspendido, auto-suspend de 60 s y timeout por sentencia de 600 s |
| Base PSET2_OULAD | Contiene las capas del proyecto |
| Esquemas | RAW, BRONZE, SILVER, GOLD y ANALYTICS como destino OBT |

El usuario autenticado recibe el rol sin escribir su nombre en el SQL versionado. SYSADMIN conserva la administración de los recursos; las futuras tablas se crearán con PSET2_PIPELINE para que ese rol sea su propietario. Se comprobarán los permisos concretos al probar los conectores.

El SQL no hace cargas ni reanuda explícitamente el warehouse. AUTO_RESUME permitirá activarlo cuando más adelante se ejecute una consulta que lo necesite; auto-suspend y timeout no son un límite monetario global ni garantizan gratuidad. Si el warehouse ya existía, IF NOT EXISTS no corrige su tamaño, estado ni parámetros: verificar los valores antes de seguir. Tampoco cambia propietarios de objetos existentes.

Si los recursos ya están asignados, adaptar el diseño a ellos y comprobar los permisos necesarios. No recrearlos ni cambiar su configuración global sin autorización.

## 3. Configurar autenticación local

Elegir un método admitido por la cuenta y por los clientes seleccionados, apto para ejecución desatendida. La opción inicial a evaluar es un par de claves. Los identificadores reales de conexión y referencias a claves irán en configuración local excluida de Git; el material privado se guardará preferentemente fuera del repositorio. Actualizar .env.example con nombres de variables y ejemplos ficticios cuando se concrete el método.

La plantilla .env.example ya refleja par de claves y los nombres de recursos del SQL. No contiene una contraseña de acceso. Las rutas privadas, frase de cifrado e identificadores reales solo se completarán localmente después de crear y registrar la clave pública. La generación y el registro ya se completaron según evidencia del autor; la conexión del host pasó la prueba. La configuración de los contenedores se preparará por separado, sin enviar claves al chat.

No reemplazar una clave pública ya utilizada en el usuario sin revisar sus otros clientes. La selección del usuario y del mecanismo de registro de la clave se concretará antes de modificar autenticación.

## 4. Verificar antes de cargar datos

Probar primero autenticación y una consulta mínima con el cliente seleccionado. Después comprobar acceso a los recursos autorizados. Registrar únicamente éxito/fallo y versiones, sin publicar valores de autenticación ni volcados de configuración.

Cierre de este paso: configuración local lista, privilegios comprobados y conexión mínima verificada. Hasta entonces, Snowflake permanece pendiente y no se declara ejecutado el pipeline.

## Evidencia de esta subetapa

La creación y verificación de metadatos cierran solo el aprovisionamiento, no la conexión externa. Comunicar si ambos SQL terminaron correctamente y si el warehouse quedó suspendido. No es necesario copiar aquí nombres de usuario, valores de conexión o resultados completos de grants.

Fuentes: [CREATE WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse), [GRANT ROLE](https://docs.snowflake.com/en/sql-reference/sql/grant-role) y [autenticación por claves](https://docs.snowflake.com/en/user-guide/key-pair-auth). Consultadas el 12-nov-2026. Se revisaron sintaxis y propósito con documentación oficial; el autor aportó evidencia posterior de recursos creados, rol, asignación al servicio y conexión externa correcta.

## Diagnóstico: base inexistente o no autorizada

Si aparece `Database 'PSET2_OULAD' does not exist or not authorized`, registrar la sentencia exacta que falló antes de cambiar permisos. El mensaje combina dos causas posibles; no demuestra por sí solo cuál ocurrió.

Abrir una worksheet SQL nueva. Si el contexto de base/esquema está fijado a PSET2_OULAD antes de que exista, quitar esa selección. Ejecutar los dos bloques de [00_diagnosticar_acceso.sql](../snowflake/00_diagnosticar_acceso.sql), cada uno completo y en orden. Buscar una fila con nombre exacto PSET2_OULAD en cada resultado. No es necesario compartir nombres de usuario o resultados completos.

- Ausente con ACCOUNTADMIN y SYSADMIN: comprobar la cuenta y si CREATE DATABASE llegó a ejecutarse; si pertenece a este proyecto, retomar 01 desde el inicio, deteniéndose ante el primer error.
- Visible con ACCOUNTADMIN, ausente con SYSADMIN: revisar propietario y grants de la base existente antes de decidir la corrección; no usar CREATE OR REPLACE ni ampliar permisos indiscriminadamente.
- Visible con ambos: revisar el rol y la sesión de la sentencia que falló y el orden real de ejecución.

En la interfaz de worksheets, Run All ejecuta el archivo completo; ejecutar únicamente la sentencia bajo el cursor puede omitir las sentencias previas. En Workspaces puede variar el nombre del control: ejecutar explícitamente todos los pasos en orden. Fuente: [ejecución de consultas en Snowsight](https://docs.snowflake.com/en/user-guide/ui-snowsight-query).

Estado de esta incidencia: posteriormente el autor aportó evidencia de base, cinco esquemas, warehouse suspendido X-Small y activación de PSET2_PIPELINE. La conexión externa del host pasó después la prueba; los permisos de carga Raw se comprobaron después desde Kestra; parámetros restantes aún necesitan evidencia específica; permisos de transformación Bronze comprobados posteriormente con dbt. Los permisos de Silver se comprobaron al construir sus tablas; Gold también se comprobó con su build; Spark se comprobó posteriormente mediante conexión real y construcción OBT.

## Corrección de asignación del rol al usuario actual

El autor identificó la sentencia fallida: SET PSET2_OPERATOR con CURRENT_USER(), que devolvió `Unsupported feature 'assignment from non-constant source expression'`. La asignación original a variable de sesión no fue válida. Se sustituyó en 01_aprovisionar.sql por un bloque Snowflake Scripting con variables locales y EXECUTE IMMEDIATE; mantiene el usuario fuera del SQL versionado y cita su identificador correctamente.

Ejecutar USE ROLE SECURITYADMIN y el bloque completo desde EXECUTE IMMEDIATE $$ hasta $$; como una sola sentencia. No ejecutar sus líneas interiores por separado. Después continuar desde USE ROLE SYSADMIN con el resto de 01 y luego ejecutar 02_verificar_recursos.sql. No hace falta borrar ni recrear lo que ya se creó. Si se vuelve a ejecutar 01 desde el inicio, revisar primero los nombres de recursos como se indicó antes.

Referencia: [variables de Snowflake Scripting](https://docs.snowflake.com/en/developer-guide/snowflake-scripting/variables) y [EXECUTE IMMEDIATE](https://docs.snowflake.com/en/sql-reference/sql/execute-immediate). La corrección se contrastó con documentación; el estado posterior y sus evidencias se registran en estado-ejecucion.md.
