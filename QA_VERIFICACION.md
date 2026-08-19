# Verificación del respaldo reproducible en Python

Fecha de la verificación reproducible original: 24 de julio de 2026.

Revisión del paquete para publicación académica: 19 de agosto de 2026.

- Reconstrucción integral repetida con `python run_all.py`: correcta.
- Las cifras regeneradas coinciden con README, ficha del modelo y artefactos.

## Pipeline y datos

- Ejecución desde `data/raw/chemotherapy_patient_data.csv` mediante `python run_all.py`.
- CSV original: 52.321 filas × 17 variables.
- Dataset model-ready: 49.765 filas.
- Identificadores únicos en model-ready.
- Nueve predictores exclusivamente pretratamiento.
- Hashes del archivo original y de los dos datasets derivados comprobados.
- Holdout estratificado del 25 % separado antes del entrenamiento.

## Modelo

- Se compararon Dummy mayoritario, Dummy estratificado, regresión logística,
  árbol de decisión, Random Forest y Extra Trees.
- Random Forest: F1 macro CV 0,2521 y F1 macro holdout 0,2496.
- Dummy estratificado: F1 macro CV 0,2525.
- Diferencia pareada: −0,0004; intervalo del 95 % compatible con cero.
- Aleatorización de etiquetas: p = 0,4991.
- Brier skill frente a prevalencia: −0,0118.
- Cobertura al umbral ilustrativo del 45 %: 0 %; abstención: 100 %.

## Aplicación

- Carga inicial de Streamlit sin excepciones.
- Caso válido con salida `ABSTENCIÓN`.
- Caso “estadio I con metástasis” con advertencia de consistencia.
- Nueve entradas con rangos numéricos o categorías cerradas.
- Pruebas de valores faltantes, suma de probabilidades y contrato de columnas.
- Cinco secciones: simulador, evidencia, datos, metodología e implantación.

## Pruebas del ZIP

- Entorno limpio temporal con Python 3.12.13.
- Dependencias instaladas exclusivamente desde `requirements.txt`.
- Ejecución: `python -m pytest -q`.
- Resultado local de la revisión del 19 de agosto: **13 pruebas superadas de
  13** con Python 3.12.13.
- La memoria final se incluye en DOCX y PDF; no se publica una presentación.
- El repositorio ignora cachés, entornos virtuales, secretos y documentos de
  trabajo distintos de la memoria final expresamente autorizada.
- No se detectaron credenciales, claves privadas ni secretos en los archivos
  publicables mediante la auditoría de patrones previa a la publicación.
- Inventario y huellas de integridad registrados en `MANIFEST_SHA256.csv`.
- El cuaderno usa el kernel portátil `python3` y puede reconstruirse, ejecutarse
  y exportarse con `python tools/render_notebook.py`.
- La validación automática se define en `.github/workflows/ci.yml`.

## Dictamen

Todos los artefactos muestran las mismas cifras y el mismo resultado:
**NO-GO clínico**. El prototipo no recomienda tratamientos y mantiene la
abstención como control de seguridad.
