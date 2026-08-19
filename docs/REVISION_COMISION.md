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
La selección se hace dentro de train mediante CV 5×2; el holdout del 25 % se
mantiene separado hasta la evaluación. Al terminar, el propio comando actualiza
el manifiesto SHA-256 para que `verify_repository.py` compruebe ese estado local.

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
