# Datos compartidos: OULAD

Fuente oficial: The Open University, https://research.stem.open.ac.uk/ouanalyse/dataset/. Publicación: Kuzilek, Hlosta y Zdrahal (2017), https://doi.org/10.1038/sdata.2017.171. Histórico 2013–2014, licencia CC BY 4.0; mantener atribución. No se afirma una actualización reciente del conjunto histórico.

Colocar aquí los originales sin modificar: studentInfo.csv (matrícula, antecedentes y resultado), studentRegistration.csv (registro/retiro), courses.csv (edición y duración), vle.csv (recursos) y studentVle.csv (interacciones diarias). assessments.csv y studentAssessment.csv están presentes, pero no forman parte del entrenamiento principal ni de los cinco archivos auditados. No se copian datos de otros proyectos.

Los CSV están excluidos de Git. Para reproducir desde un clon, obtener legalmente el paquete OULAD desde la fuente oficial, extraer estos cinco nombres y comprobar identidad con manifest.json antes de ejecutar. La versión concreta de descarga no fue facilitada: los hashes identifican esta copia y no prueban por sí solos autenticidad respecto al proveedor. Si difieren, registrar nueva versión y reconciliar el análisis; no afirmar reproducción idéntica.

Verificar un archivo con `shasum -a 256 datasets/studentInfo.csv` desde raíz y contrastar con el manifiesto; repetir para los cinco. La auditoría recalcula todos los hashes y conteos mediante `python pset-01/scripts/auditar_datos.py` en un entorno con las dependencias declaradas. manifest.json contiene origen, licencia, histórico/publicación, fecha de auditoría UTC, nombre, SHA-256, bytes, filas y modificación local. La fecha original de descarga permanece desconocida.

PSet 1 solo audita descriptivamente. PSet 2 consume ../datasets mediante un montaje de solo lectura y verifica los cinco hashes antes de cargar; su cadena y reproducción limpia ya se ejecutaron. Cada etapa guarda derivados en su propio árbol. [Auditoría y límites](../pset-01/docs/auditoria-datos.md) y [pipeline reproducible](../pset-02/README.md).
