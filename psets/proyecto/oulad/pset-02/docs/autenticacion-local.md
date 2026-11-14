# Autenticación local por par de claves

Estado: generación local y GRANT confirmados por el autor; prueba externa correcta según docs/conexion-snowflake.json (12-nov-2026, 21:30:28 UTC). El agente no leyó las claves ni la frase de cifrado. Se verificó el contexto esperado. Posteriormente Kestra cargó Raw y dbt construyó Bronze; la conexión cloud de Spark también está comprobada; ver obt-spark.md.

## 1. Generar claves fuera del repositorio

Desde la raíz, en la terminal integrada de VS Code:

```bash
python3 pset-02/scripts/preparar_claves.py
```

Se requiere Python 3 y OpenSSL. El script genera una clave RSA de 2048 bits cifrada con AES-256-CBC en formato PEM/PKCS#8 y exporta su clave pública. OpenSSL pide la frase de cifrado dos veces al crear la privada y otra vez para exportar la pública. Introducirla directamente en la terminal, sin enviarla al chat ni incluirla como argumento.

Los archivos quedan en `~/.config/psets/snowflake/`, fuera del repositorio:

- rsa_key.p8: clave privada cifrada.
- rsa_key.pub: clave pública.
- registrar_usuario.local.sql: copia local de la plantilla de alta, con la clave pública incorporada.

La carpeta es configurable con `--output-dir`, siempre fuera del repositorio. El script no sobrescribe archivos existentes ni conecta con Snowflake. No subir ninguno de estos archivos al repositorio. Los archivos nuevos usan permisos privados. Guardar la frase en un gestor seguro; su integración local con los clientes se preparará al configurar esos clientes.

## 2. Crear un usuario dedicado en Snowflake

Se propone PSET2_SVC, tipo SERVICE, limitado al rol PSET2_PIPELINE. Así no se modifica la autenticación del usuario personal ni se da acceso administrativo al pipeline.

En una worksheet SQL de Snowsight, usando tu sesión administrativa:

```sql
USE ROLE SECURITYADMIN;
SHOW USERS LIKE 'PSET2_SVC';
```

Si aparece exactamente PSET2_SVC, detenerse y revisar para evitar reutilizar una identidad o una clave ajena. Si no existe, abrir **la copia local** `~/.config/psets/snowflake/registrar_usuario.local.sql`, copiarla a Snowsight y ejecutar cada sentencia en orden, deteniéndose ante cualquier error. El bloque CREATE USER completo es una sentencia. La plantilla versionada contiene un marcador y no sirve para ejecutarla directamente.

El script crea un usuario nuevo sin contraseña, registra únicamente la clave pública y le asigna PSET2_PIPELINE. El usuario de servicio no es para entrar a Snowsight: lo usarán los clientes del pipeline. No se crea ni reanuda ningún warehouse en este paso. Si CREATE USER termina pero falla el GRANT, no regenerar claves ni intentar reemplazar el usuario: retomar el GRANT después de resolver el error.

## 3. Probar la conexión desde la terminal

Entorno preparado: Python 3.11.16, separado del entorno de PSet 1, con snowflake-connector-python 4.7.4. El conector está fijado en scripts/requirements-conexion.in y las 25 dependencias resueltas en scripts/requirements-conexion.txt. Se verificó la importación sin abrir conexión. Se probaron con dobles aislados el éxito, contexto incorrecto y sanitización de errores, sin red ni claves reales. Esto es el cliente de diagnóstico local; dbt usa su imagen y adaptador fijados, comprobados después con Bronze; el conector cloud de Spark se resolvió y probó después; ver spark-dependencias.json y obt-spark.md.

Desde la raíz, con el entorno de conexión instalado:

```bash
pset-02/.venv/bin/python pset-02/scripts/probar_conexion.py
```

El script solicita:

1. Identificador de cuenta para clientes, normalmente `organizacion-cuenta`. Obtenerlo del apartado de detalles de conexión de la cuenta en Snowsight. No usar la URL del navegador, https:// ni el sufijo .snowflakecomputing.com. Introducirlo solo en la terminal, no en el chat.
2. Ruta a la privada: Enter utiliza `~/.config/psets/snowflake/rsa_key.p8`.
3. Frase de cifrado: se introduce oculta mediante getpass, sin almacenarla ni pasarla por argumentos.

No se crea .env ni se guarda el identificador de cuenta en esta prueba. El conector utiliza la clave para JWT y solicita la sesión PSET2_SVC/PSET2_PIPELINE/PSET2_OULAD/RAW/PSET2_WH. Se ejecuta únicamente una consulta de funciones de contexto, sin consultar tablas ni cargar datos. El script no cambia la configuración del warehouse.

Resultado esperado: `Conexión correcta: usuario de servicio, rol, base, esquema y warehouse esperados.` El informe docs/conexion-snowflake.json solo se genera al intentar la conexión; incluye fecha, versión del cliente y éxito o códigos sanitizados de fallo, sin cuenta, rutas, claves ni frase. No se entrega un informe ficticio antes de ejecutar. Ante fallo, compartir solo la categoría y códigos del informe, no volcados del entorno ni excepciones completas.

Comprobación sin acceso cloud: añadir `--check-installation`; importa el conector y muestra la versión sin leer claves ni abrir conexión. La prueba requiere terminal interactiva. La futura automatización del pipeline sustituirá estos prompts por configuración local/secretos montados, no por valores versionados.

Para reproducir la instalación desde una copia limpia, una vez disponible requirements-conexion.txt:

```bash
uv --cache-dir tmp/uv-cache venv --python 3.11 pset-02/.venv
uv --cache-dir tmp/uv-cache pip sync --only-binary :all: --python pset-02/.venv/bin/python pset-02/scripts/requirements-conexion.txt
pset-02/.venv/bin/python pset-02/scripts/probar_conexion.py --check-installation
```

Los comandos de creación del entorno e instalación solo se necesitan si ese entorno aún no está preparado. La clave privada permanecerá fuera del repositorio y se montará como solo lectura en los futuros contenedores que la necesiten.

La instalación inicial intentó compilar cryptography 50.0.2 y falló por dependencias nativas de OpenSSL. Se resolvió instalando solo distribuciones precompiladas: el entorno instalado usa cryptography 48.0.1, compatible con las restricciones del conector. El archivo resuelto conserva esa combinación; no se requiere compilarla para repetir esta instalación. Validar disponibilidad de wheels si se cambia de plataforma o versión de Python.

Que el rol funcione en tu sesión personal o que se cree el usuario SERVICE no demuestra aún que la autenticación externa funcione. Marcarla verificada solamente tras conectar desde el cliente seleccionado.

## Diagnóstico del primer intento: 290404 / 08001

El primer intento real devolvió 290404. En el código del conector 4.7.4 instalado, network.py calcula ER_HTTP_GENERAL_ERROR + response.status_code, y errorcode.py fija la base en 290000: corresponde a HTTP 404. No demuestra por sí solo qué componente devolvió el 404 ni que haya un error de clave. Comprobar primero el identificador de cuenta/destino antes de modificar autenticación o grants.

En Snowsight, en la misma cuenta donde se crearon PSET2_OULAD y PSET2_SVC, ejecutar:

```sql
SELECT REPLACE(
    CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME(),
    '_', '-'
) AS identificador_cuenta;
```

Usar el valor de esa celda solo en la terminal, al repetir probar_conexion.py. No añadir región al formato organización-cuenta, ni https://, comillas, sufijo .snowflakecomputing.com o segmentos de la URL del navegador. No pegar el resultado en el chat ni guardarlo en documentación versionada. La sustitución de guiones bajos produce el formato de cliente recomendado por la documentación de configuración.

Alternativa: menú de usuario de Snowsight → Connect a tool to Snowflake → Config file; utilizar únicamente el valor del campo account, sin copiar toda la configuración ni sus otros valores al chat. Fuente: [configuración oficial de clientes](https://docs.snowflake.com/en/user-guide/gen-conn-config).

Si persiste el mismo 404 usando el identificador obtenido de esa cuenta, revisar configuración del endpoint, red/proxy o uso de conectividad privada. No cambiar ni desactivar validaciones TLS. El script conserva solo códigos sanitizados.

Resultado de esta incidencia: resuelta al corregir el identificador de cuenta. El informe posterior registra status=ok y contexto esperado verificado. No se modificaron claves ni grants para resolverla. Estas instrucciones se conservan para reproducir el diagnóstico si ocurre en otra instalación.

Referencias: [Snowflake: claves y cifrado](https://docs.snowflake.com/en/user-guide/key-pair-auth), [CREATE USER, tipo SERVICE](https://docs.snowflake.com/en/sql-reference/sql/create-user), [SHOW USERS](https://docs.snowflake.com/en/sql-reference/sql/show-users) y [conexión del cliente Python](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect). Consultadas el 12-nov-2026. Generación local y asignación del rol confirmadas por el autor; prueba externa posterior correcta según conexion-snowflake.json. La revisión del script no generó ni mostró material privado; los clientes posteriores leen internamente los montajes privados para autenticar.
