# PSet 3 · Reconstrucción v2

Estado: respaldo v1 verificado; protocolo y código inicial en preparación. Esta carpeta no presenta las salidas de v1 como experimentos nuevos. Los entregables vigentes de v1 permanecen fuera de v2 hasta completar esta reconstrucción.

Seis candidatos incluyen un LLM generativo de OpenAI mediante prompting. Mismo snapshot, particiones, cinco folds y métrica de negocio; disponibilidad de información al corte. API con tope global autorizado de USD 10, libro de reservas y caché privada. Los ejemplos de prompting proceden únicamente de train-fold, con cantidad explícita; no se afirma que el LLM procese todas las filas como un clasificador tradicional.

La prueba 2014J fue observada en v1. Su uso en v2 se declara como benchmark retrospectivo reutilizado. No se presenta como prueba inédita ni se permite ajustar con sus resultados.

## Acceso OpenAI

Crear la clave en https://platform.openai.com/api-keys y completar OPENAI_API_KEY en .secrets/pset3-openai.env de la raíz. No pegar claves en chat, notebooks o Git. No modificar el límite de USD 10. Se usa Responses API con JSON Schema y sin herramientas, razonamiento none y modelo gpt-6-luna; tarifas verificadas de entrada USD 0,10 y salida USD 0,50 por millón de tokens en contexto corto. La cota de reservas no aplica descuentos, por lo que es conservadora.

Documentación oficial: https://developers.openai.com/api/docs/quickstart y https://developers.openai.com/api/docs/models/gpt-6-luna y https://developers.openai.com/api/docs/pricing. ChatGPT y API tienen acceso/facturación separados; créditos elegibles deben activarse. El plugin OpenAI Developers es opcional para consultar documentación durante integración.

## Orden

1. Cerrar preflight de credenciales, presupuesto y código; congelar protocolo y commit.
2. Ejecutar EDA y derivadas con evidencia de desarrollo.
3. Registrar dos baselines antes de seis candidatos por defecto.
4. Tuning de tres mejores por negocio, mínimo 30 configuraciones cada uno, nested.
5. Controles estáticos equivalentes, anticipación y decisión congelada.
6. Prueba final, Registry, reproducción, memo legible de seis páginas y auditoría literal.

El cierre no se declara completo mientras falte un candidato, su tuning obligatorio o verificación. Las restricciones operativas no sustituyen al ensayo del LLM.
