# Validación de la estructura de entrega PSet 2

La copia de entrega es `pset_2/`. Se preservó `pset-02/` y un respaldo privado del inventario público anterior. Los archivos principales y las carpetas corresponden a la estructura solicitada; los componentes auxiliares se distribuyen dentro de Kestra y dbt. No se distribuyen secretos ni datos individuales.

| Comprobación nueva | Resultado |
|---|---|
| Compose local y cloud | Configuraciones válidas con las nuevas rutas |
| Stack local | Proyecto `pset2-entrega`, servicios saludables y puertos `18090/18091` |
| Kestra | Flujo local `infra_smoke` en SUCCESS; acceso no autenticado rechazado |
| Ingesta | Cuatro pruebas de invariantes aprobadas sin Snowflake |
| dbt | `parse` local reconoce 23 modelos y 168 tests; los tests cloud no se repiten |
| Spark local | Motor 3.5.6, 32.593 matrículas leídas y cinco checksums verificados con montaje de solo lectura |
| Features Spark | Siete casos sintéticos aprobados, incluida perturbación futura |
| Memo | Archivo original en `docs/`, seis páginas; conservación de contenido comprobada |
| Evidencias | Informes agregados bajo `docs/evidencia/`; referencias y resúmenes ajustados |
| Seguridad | Configuración privada excluida; el verificador publica categorías y ubicaciones, sin valores sensibles |

Se conservan las definiciones de los modelos dbt, las transformaciones Spark, la ingesta y los ejecutores internos. Los cambios afectan rutas del host, montajes, auxiliares de empaquetado/reproducción y documentación. Los paths internos de contenedores siguen siendo `/workspace/...`.

Las comprobaciones nuevas no vuelven a cargar Raw, construir capas en Snowflake o publicar la OBT. Los 168 tests dbt y las cifras cloud del trabajo cerrado se respaldan con la evidencia histórica conservada; `dbt parse` valida estructura y sintaxis, no los resultados de esos tests. No se afirma una nueva reproducción cloud integral.

La entrega usa un proyecto Compose distinto al histórico. Las claves y la configuración Snowflake externas se conservan; no se regeneran ni se publican. Las contraseñas locales de la copia nueva se generan aparte. El memo mantiene su instantánea histórica: consultar [rutas de entrega](rutas-entrega.md) para traducir sus comandos.

Comprobación repetible: `python3 kestra/scripts/verificar_paquete.py --infra`, desde `pset_2/`, con `.env.infra` y las referencias cloud preparadas. El informe técnico completo se conserva en [validacion-entrega.json](validacion-entrega.json); el inventario y sus comprobaciones, en [paquete-verificacion.json](paquete-verificacion.json).

También se construyeron las tres imágenes desde sus nuevos contextos y se desplegaron las definiciones Raw e integral en Kestra, sin ejecutar cargas y con calendarios desactivados. La exportación de reproducción limpia quedó PREPARED y sus dos configuraciones Compose validaron. La copia local de pruebas quedó detenida conservando volúmenes; se vuelve a levantar con `infra.py up --local-only` o `--cloud` según la configuración. El stack histórico se conserva.

El ZIP se descomprimió en una carpeta independiente y su verificador pasó sin Git ni dependencia de `pset-02/`. Se comprobaron CRC, manifiesto SHA-256, raíz única `pset_2/`, ausencia de archivos privados y un único PDF bajo `docs/`.


## Actualización de calendario — 20-nov-2026

La validación anterior conserva el estado histórico de sus pruebas. Ahora `pset2-entrega` está levantado en modo cloud y el calendario padre está activo; Raw sigue sin calendario independiente. Una ejecución Schedule recuperó el 15-nov y terminó SUCCESS el 20-nov. El memo se revisó manteniendo seis páginas, con original preservado e identificación de hashes. [Corrección y evidencia](calendario-programado.md). No se repite ni reetiqueta la reproducción histórica como si incluyera estas modificaciones.
