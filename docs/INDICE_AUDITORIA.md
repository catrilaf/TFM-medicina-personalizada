# Índice de auditoría técnica

Este índice permite revisar el proyecto desde la memoria o directamente desde
el código. Cada enlace apunta al código que genera o comprueba el artefacto
indicado. La ruta abreviada está en
[`REVISION_COMISION.md`](REVISION_COMISION.md) y el contraste con la pauta en
[`MATRIZ_CUMPLIMIENTO_VIU.md`](MATRIZ_CUMPLIMIENTO_VIU.md).

La preparación personal para explicar el proyecto y confirmar la declaración
de herramientas está en [`AUTORIA_Y_DEFENSA.md`](AUTORIA_Y_DEFENSA.md).
La correspondencia completa entre los anexos A-L y el código está en
[`ANEXOS_Y_CODIGO.md`](ANEXOS_Y_CODIGO.md).

## Memoria académica

- [`TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.pdf`](../memoria/TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.pdf)
- [`TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.docx`](../memoria/TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.docx)

## A. Preparación y procedencia de los datos

| Evidencia | Implementación | Salida verificable |
|---|---|---|
| Identidad del CSV bruto | [`src/preprocessing.py`](../src/preprocessing.py) | [`data/SOURCE_METADATA.json`](../data/SOURCE_METADATA.json) |
| Limpieza y variables derivadas | [`src/preprocessing.py`](../src/preprocessing.py) | [`data/chemotherapy_patient_data_clean_tfm.csv`](../data/chemotherapy_patient_data_clean_tfm.csv) |
| Dataset model-ready | [`tools/rebuild_datasets_from_raw.py`](../tools/rebuild_datasets_from_raw.py) | [`data/chemotherapy_patient_data_model_ready_recommender_tfm.csv`](../data/chemotherapy_patient_data_model_ready_recommender_tfm.csv) |
| Predictores y exclusiones por leakage | [`src/config.py`](../src/config.py) | [`outputs/tables/06_auditoria_leakage.csv`](../outputs/tables/06_auditoria_leakage.csv) |
| Calidad, duplicados y perfiles | [`src/data.py`](../src/data.py) | [`outputs/tables/01_resumen_calidad.csv`](../outputs/tables/01_resumen_calidad.csv) |

## B. Análisis exploratorio

| Evidencia | Implementación | Salida verificable |
|---|---|---|
| EDA y asociaciones | [`src/analysis.py`](../src/analysis.py) | [`outputs/tables/`](../outputs/tables/) |
| Gráficos | [`src/figures.py`](../src/figures.py) | [`outputs/figures/`](../outputs/figures/) |
| Estudio paso a paso | [`tools/render_notebook.py`](../tools/render_notebook.py) | [`notebooks/01_estudio_completo_oncologia.ipynb`](../notebooks/01_estudio_completo_oncologia.ipynb) y [`reports/Estudio_Completo_Oncologia.html`](../reports/Estudio_Completo_Oncologia.html) |

## C. Entrenamiento y evaluación

| Evidencia | Implementación | Salida verificable |
|---|---|---|
| División train/holdout | [`src/modeling.py`](../src/modeling.py) | [`outputs/tables/10_manifest_split.csv`](../outputs/tables/10_manifest_split.csv) |
| Seis modelos comparados | [`src/modeling.py`](../src/modeling.py) | [`outputs/tables/12_cv_resumen_modelos.csv`](../outputs/tables/12_cv_resumen_modelos.csv) |
| Métricas multiclase | [`src/metrics.py`](../src/metrics.py) | [`outputs/tables/13_metricas_holdout_modelos.csv`](../outputs/tables/13_metricas_holdout_modelos.csv) |
| Modelo serializado | [`src/modeling.py`](../src/modeling.py) | [`outputs/models/model_metadata.json`](../outputs/models/model_metadata.json) |

## D. Robustez, incertidumbre y resultado NO-GO

| Evidencia | Implementación | Salida verificable |
|---|---|---|
| IC bootstrap y comparación pareada | [`src/robustness.py`](../src/robustness.py) | [`outputs/tables/25_ic_bootstrap_holdout.csv`](../outputs/tables/25_ic_bootstrap_holdout.csv) |
| Calibración y skill probabilístico | [`src/robustness.py`](../src/robustness.py) | [`outputs/tables/35_skill_probabilistico.csv`](../outputs/tables/35_skill_probabilistico.csv) |
| Aleatorización de etiquetas | [`src/robustness.py`](../src/robustness.py) | [`outputs/tables/32_prueba_aleatorizacion_etiquetas.csv`](../outputs/tables/32_prueba_aleatorizacion_etiquetas.csv) |
| Curva de aprendizaje | [`src/robustness.py`](../src/robustness.py) | [`outputs/tables/34_curva_aprendizaje.csv`](../outputs/tables/34_curva_aprendizaje.csv) |
| Rendimiento por subgrupos | [`src/metrics.py`](../src/metrics.py) | [`outputs/tables/19_rendimiento_subgrupos.csv`](../outputs/tables/19_rendimiento_subgrupos.csv) |

## E. Aplicación y pruebas

| Evidencia | Implementación | Verificación |
|---|---|---|
| Interfaz y aviso no asistencial | [`app.py`](../app.py) | `streamlit run app.py` |
| Validación de entradas y alertas | [`src/app_logic.py`](../src/app_logic.py) | [`tests/test_smoke.py`](../tests/test_smoke.py) |
| Abstención funcional | [`tests/test_streamlit_app.py`](../tests/test_streamlit_app.py) | `python -m pytest -q` |
| Reproducción integral | [`run_all.py`](../run_all.py) | [`QA_VERIFICACION.md`](../QA_VERIFICACION.md) |
| Integridad de archivos | [`tools/build_manifest.py`](../tools/build_manifest.py) | [`MANIFEST_SHA256.csv`](../MANIFEST_SHA256.csv) |
| Auditoría autocontenida | [`tools/verify_repository.py`](../tools/verify_repository.py) | `python tools/verify_repository.py` |
| Integración continua | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | [GitHub Actions](https://github.com/catrilaf/TFM-medicina-personalizada/actions) |

## F. Código histórico

[`legacy/`](../legacy/) conserva los scripts inicialmente recibidos para que el
tribunal pueda distinguir el punto de partida de la versión modular. No son los
puntos de ejecución recomendados y no deben confundirse con el pipeline final.

## G. Correspondencia de los anexos

Cada anexo de la memoria tiene al menos un enlace directo al script que
implementa o verifica su contenido. La tabla completa y navegable está en
[`ANEXOS_Y_CODIGO.md`](ANEXOS_Y_CODIGO.md). La auditoría automática comprueba
que los anexos A-L y todos los scripts enlazados continúan presentes.
