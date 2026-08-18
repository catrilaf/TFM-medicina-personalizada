# Dataset card

## Identificación

- Nombre operativo: `chemotherapy_patient_data_clean_tfm.csv`.
- Dataset de modelado: `chemotherapy_patient_data_model_ready_recommender_tfm.csv`.
- Unidad de análisis: un registro de paciente.
- Filas del dataset limpio: 52.321.
- Filas con régimen conocido: 49.765.
- Variable objetivo: `chemotherapy_regimen`.
- Clases: ABVD, CHOP, FOLFOX y Gemcitabine.

## Procedencia y licencia

La procedencia técnica del archivo se verificó el 24 de julio de 2026:

- Fuente: Kaggle, `omenkj/chemotherapy-regimens-based-on-patient-data`.
- Título: *Chemotherapy Regimens Based on Patient Data*.
- Autor/propietario publicado: OmenKj.
- Versión: 1, actualizada el 22 de febrero de 2025.
- Licencia publicada: Apache 2.0.
- Archivo bruto: `data/raw/chemotherapy_patient_data.csv`.
- Tamaño: 4.351.306 bytes.
- SHA-256: `7809afd664be251e882ce02d4c843fd26a7765c0a921192cadfe11c37b2db6f2`.

El archivo aportado por el alumno coincide byte a byte con el CSV descargado
mediante la API de Kaggle para la versión 1. Esta verificación acredita la
identidad del archivo y la licencia publicada, pero no su procedencia clínica.
Kaggle no identifica una institución sanitaria, protocolo de recogida,
aprobación ética, criterios de inclusión ni mecanismo de generación. Por ello,
no se afirma que los registros correspondan a pacientes reales y tampoco se
afirma como hecho que sean sintéticos.

## Privacidad

Los identificadores tienen formato `P00001`, pero esto no demuestra
anonimización formal. El paquete no contiene nombres, direcciones ni fechas,
aunque tampoco incluye una evaluación de reidentificación. No se debe combinar
con fuentes externas ni introducir datos reales en la aplicación.

## Transformaciones documentadas

- Normalización de nombres a `snake_case`.
- Imputación de mutación faltante como `Not_reported`.
- Marcado de régimen faltante como `Not_recorded` en el dataset limpio.
- Creación de grupos de edad, categoría de IMC y variables binarias.
- Derivación de riesgo clínico/frailty con reglas académicas.
- Derivación de outcomes binarios.
- Exclusión de regímenes no registrados para el dataset model-ready.

La reconstrucción se ejecuta mediante `python tools/rebuild_datasets_from_raw.py`
o como primera fase de `python run_all.py`. Los hashes esperados son:

- Dataset limpio: `a911f348979e9b7b54f691a2459dfa59bb5274d54585dd5a52cbc04877bb77b3`.
- Model-ready: `3d4c3c478b4e0720cfae9ab13ca5715c8d5baf3a064c0bc98125a9661e065d08`.

## Calidad conocida

- No hay duplicados de `patient_id` en model-ready.
- No hay valores faltantes después de la preparación.
- Existen 49.763 perfiles predictores únicos sobre 49.765 registros; dos perfiles aparecen dos veces y ninguno presenta etiquetas en conflicto.
- Existen combinaciones de estadio y metástasis que requieren revisión clínica.
- Las asociaciones entre tipo de cáncer, estadio, mutación y régimen son prácticamente nulas.
- Los tamaños de efecto numéricos son despreciables: eta cuadrado es inferior a 0,0001 para edad, IMC y tamaño tumoral.
- El target está moderadamente desbalanceado hacia FOLFOX.

## Uso apropiado

- Docencia de EDA, pipelines, clasificación, clustering y evaluación.
- Demostración de reproducibilidad y prevención de leakage.
- Auditoría metodológica de un resultado negativo.

## Uso inapropiado

- Recomendar, prescribir o descartar tratamientos.
- Comparar eficacia, seguridad o supervivencia entre regímenes.
- Estimar costo-efectividad o impacto presupuestario.
- Entrenar un producto sanitario.
- Publicar conclusiones clínicas sin validar procedencia y representatividad.

## Archivos para revisión

- Archivo bruto sin modificar: `raw/chemotherapy_patient_data.csv`.
- Metadatos y verificación: `SOURCE_METADATA.json`.
- Aviso de licencia: `LICENSE_DATASET.txt`.
- Dataset completo y transformaciones: `chemotherapy_patient_data_clean_tfm.csv`.
- Dataset utilizado por los modelos: `chemotherapy_patient_data_model_ready_recommender_tfm.csv`.
- Muestra manual equilibrada de 1.000 registros: `chemotherapy_patient_data_muestra_revision_profesor_1000.csv`.
- Diccionario: `diccionario_variables_recomendador_oncologia.csv`.
