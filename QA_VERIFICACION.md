# Verificación del respaldo reproducible en Python

Fecha de la verificación reproducible original: 24 de julio de 2026.

Revisión del paquete para publicación académica: 19 de agosto de 2026.

Revisión de cierre del acta y navegación de anexos: 20 de agosto de 2026.

Actualización de los datos administrativos confirmados por el autor: 20 de
agosto de 2026.

Depuración final de archivos obsoletos y actualización del inventario: 21 de
agosto de 2026.

- Reconstrucción integral repetida con `python run_all.py`: correcta.
- Las cifras de referencia coinciden con README, ficha del modelo y artefactos.
- En distintos sistemas operativos los ensembles de árboles pueden resolver de
  forma diferente empates de impureza y variar unas milésimas. La verificación
  exige tolerancia de ±0,005 en las métricas principales y conserva criterios
  científicos invariantes: F1 próxima a 0,25, ausencia de ganancia material,
  aleatorización no significativa y abstención del 100 %.

## Pipeline y datos

- Ejecución desde `data/raw/chemotherapy_patient_data.csv` mediante `python run_all.py`.
- CSV original: 52.321 filas × 17 variables.
- Dataset model-ready: 49.765 filas.
- Identificadores únicos en model-ready.
- Nueve predictores exclusivamente pretratamiento.
- Hashes del archivo original y de los dos datasets derivados comprobados.
- Holdout interno estratificado del 25 % separado antes del entrenamiento y
  excluido de la selección del modelo.
- Ausencia de solapamiento de índices y de perfiles predictores idénticos entre
  train y holdout para la partición reproducible con semilla 42.

## Modelo

- Se compararon Dummy mayoritario, Dummy estratificado, regresión logística,
  árbol de decisión, Random Forest y Extra Trees.
- Random Forest: F1 macro CV 0,2521 y F1 macro holdout 0,2496.
- Dummy estratificado: F1 macro CV 0,2525.
- Diferencia pareada: −0,0004; intervalo del 95 % compatible con cero. Los
  intervalos y Wilcoxon de los folds repetidos se interpretan como diagnósticos
  exploratorios porque los folds se solapan.
- Aleatorización de etiquetas: p = 0,4991.
- Brier skill frente a prevalencia: −0,0118.
- Cobertura al umbral ilustrativo del 45 %: 0 %; abstención: 100 %.
- Gate formal de suficiencia de señal: `false`; autorización clínica:
  `clinical_go=false`.

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
- Resultado local de la revisión del 20 de agosto: **13 pruebas superadas de
  13** con Python 3.12.13.
- La memoria final se incluye en DOCX y PDF; no se publica una presentación.
- El repositorio ignora cachés, entornos virtuales, secretos y documentos de
  trabajo distintos de la memoria final expresamente autorizada.
- No se detectaron credenciales, claves privadas ni secretos en los archivos
  publicables mediante la auditoría de patrones previa a la publicación.
- Inventario y huellas de integridad registrados en `MANIFEST_SHA256.csv`.
- Correspondencia de los anexos A-L con enlaces directos a código y salidas
  comprobada por `tools/verify_repository.py`.
- Portada confirmada por el autor: director de TFM, Sinuhe Martinez Rodriguez;
  primera convocatoria; fecha, septiembre de 2026.
- El cuaderno usa el kernel portátil `python3` y puede reconstruirse, ejecutarse
  y exportarse con `python tools/render_notebook.py`.
- La validación automática se define en `.github/workflows/ci.yml`.
- `ruff check` finaliza sin avisos sobre el código activo y las utilidades.
- `pip-audit -r requirements.txt` no informa vulnerabilidades conocidas; se
  actualizó `nbconvert` a 7.17.1.
- El PDF final conserva 88 páginas A4 y se exportó como documento etiquetado;
  la auditoría DOCX no presenta incidencias de accesibilidad de severidad alta.

## Dictamen

Todos los artefactos muestran las mismas cifras y el mismo resultado:
**NO-GO clínico**. El prototipo no recomienda tratamientos y mantiene la
abstención como control de seguridad.
