# Ruta de revisión para la comisión

Este documento ofrece una revisión breve y verificable del TFM. El repositorio
publica la memoria, el CSV de origen, el código Python, las salidas generadas,
el modelo experimental y la aplicación Streamlit.

## 1. Lectura académica

1. Abrir la [memoria en PDF](../memoria/TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.pdf).
2. Consultar la [ficha del dataset](../data/DATASET_CARD.md) para distinguir
   procedencia técnica de procedencia clínica.
3. Revisar la [ficha del modelo](../MODEL_CARD.md) y su decisión NO-GO.

## 2. Reproducción mínima

Requisitos: Python 3.12 y Git.

```bash
git clone https://github.com/catrilaf/TFM-medicina-personalizada.git
cd TFM-medicina-personalizada
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_all.py
python -m pytest -q
python tools/verify_repository.py
```

`run_all.py` comprueba el hash del CSV bruto y reconstruye datasets, split,
preprocesamiento, seis modelos, tablas, figuras, metadatos y modelo serializado.
La selección se hace dentro de train mediante CV 5×2; el holdout interno del
25 % se mantiene separado de esa selección y se utiliza posteriormente para la
evaluación comparativa y las auditorías post hoc. No equivale a validación
externa. Al terminar, el propio comando actualiza
el manifiesto SHA-256 para que `verify_repository.py` compruebe ese estado local.

Los valores publicados corresponden al entorno de referencia. En otro sistema
operativo, Random Forest puede variar unas milésimas al resolver empates entre
divisiones equivalentes. La auditoría admite ±0,005 en las métricas puntuales,
pero exige que se conserve el resultado científico: rendimiento cercano a
0,25, sin mejora material frente al Dummy, p de aleatorización no significativo
y 100 % de abstención.

## 3. Evidencias clave

| Pregunta | Evidencia |
|---|---|
| ¿Qué variables entran al modelo? | [`src/config.py`](../src/config.py) y [`06_auditoria_leakage.csv`](../outputs/tables/06_auditoria_leakage.csv) |
| ¿Cómo se compararon los modelos? | [`src/modeling.py`](../src/modeling.py) y [`12_cv_resumen_modelos.csv`](../outputs/tables/12_cv_resumen_modelos.csv) |
| ¿Existe mejora frente al azar? | [`26_comparaciones_cv_pareadas.csv`](../outputs/tables/26_comparaciones_cv_pareadas.csv) y [`32_prueba_aleatorizacion_etiquetas.csv`](../outputs/tables/32_prueba_aleatorizacion_etiquetas.csv) |
| ¿Por qué la web se abstiene? | [`28_rendimiento_selectivo_umbral.csv`](../outputs/tables/28_rendimiento_selectivo_umbral.csv), [`src/app_logic.py`](../src/app_logic.py) y [`tests/test_streamlit_app.py`](../tests/test_streamlit_app.py) |
| ¿Son coherentes los archivos? | [`MANIFEST_SHA256.csv`](../MANIFEST_SHA256.csv) y [`tools/verify_repository.py`](../tools/verify_repository.py) |

## 4. Aplicación web

```bash
python -m streamlit run app.py
```

La interfaz funciona en local, no almacena entradas y muestra probabilidades
experimentales, incertidumbre, alertas de consistencia y abstención. No es un
sistema asistencial y no debe recibir información de pacientes reales. Las
instrucciones para publicar una demostración están en
[`DESPLIEGUE_STREAMLIT.md`](DESPLIEGUE_STREAMLIT.md).

## 5. Interpretación del resultado

El objetivo computacional es clasificar el régimen histórico registrado; no
es estimar el tratamiento óptimo. Random Forest obtiene F1 macro 0,2521 en CV y
0,2496 en holdout, sin superar materialmente al Dummy estratificado (0,2525 en
CV). La aleatorización de etiquetas produce p = 0,4991. Por tanto, la decisión
responsable es NO-GO clínico y 100 % de abstención con el umbral ilustrativo.

El aporte demostrable es la cadena reproducible, la prevención de leakage, la
comparación contra baselines, la auditoría de señal y la interfaz que impide
presentar una predicción cercana al azar como recomendación médica.

Los intervalos y la prueba de Wilcoxon construidos sobre los diez resultados de
CV son diagnósticos exploratorios: los folds repetidos se solapan y no pueden
tratarse como observaciones estadísticamente independientes. La decisión NO-GO
se apoya además en el holdout interno, la aleatorización de etiquetas, el skill
probabilístico negativo, la calibración y la abstención completa.
