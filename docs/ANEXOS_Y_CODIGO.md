# Correspondencia directa entre anexos y código Python

Esta página permite revisar cada anexo de la memoria desde el navegador de
GitHub. Los enlaces de la columna **Código fuente** abren directamente el
script que implementa o verifica la evidencia descrita. Cuando un anexo es una
síntesis narrativa, se enlaza el código que produce o comprueba sus cifras; no
se presenta el texto del anexo como si hubiera sido generado automáticamente.

| Anexo | Contenido de la memoria | Código fuente | Evidencia verificable |
|---|---|---|---|
| Anexo A | Model card simplificada | [`src/modeling.py`](../src/modeling.py), [`src/metrics.py`](../src/metrics.py) | [`MODEL_CARD.md`](../MODEL_CARD.md), [`model_metadata.json`](../outputs/models/model_metadata.json) |
| Anexo B | Matriz de riesgos | [`src/app_logic.py`](../src/app_logic.py), [`src/robustness.py`](../src/robustness.py) | [`MODEL_CARD.md`](../MODEL_CARD.md), [`test_streamlit_app.py`](../tests/test_streamlit_app.py) |
| Anexo C | Reproducibilidad del paquete | [`run_all.py`](../run_all.py), [`tools/verify_repository.py`](../tools/verify_repository.py) | [`QA_VERIFICACION.md`](../QA_VERIFICACION.md), [`MANIFEST_SHA256.csv`](../MANIFEST_SHA256.csv) |
| Anexo D | Casos model-ready ilustrativos | [`tools/rebuild_datasets_from_raw.py`](../tools/rebuild_datasets_from_raw.py), [`src/preprocessing.py`](../src/preprocessing.py) | [`muestra de 1.000 registros`](../data/chemotherapy_patient_data_muestra_revision_profesor_1000.csv) |
| Anexo E | Controles incorporados | [`src/preprocessing.py`](../src/preprocessing.py), [`src/robustness.py`](../src/robustness.py), [`src/app_logic.py`](../src/app_logic.py) | [`tests/`](../tests/) |
| Anexo F | Procedencia y reconstrucción | [`src/preprocessing.py`](../src/preprocessing.py), [`tools/rebuild_datasets_from_raw.py`](../tools/rebuild_datasets_from_raw.py) | [`SOURCE_METADATA.json`](../data/SOURCE_METADATA.json), [`README_KAGGLE.md`](../data/raw/README_KAGGLE.md) |
| Anexo G | Contrato de modelado y pruebas | [`src/config.py`](../src/config.py), [`tests/test_repository_contract.py`](../tests/test_repository_contract.py), [`tests/test_smoke.py`](../tests/test_smoke.py) | [`06_auditoria_leakage.csv`](../outputs/tables/06_auditoria_leakage.csv) |
| Anexo H | Modelos y decisión NO-GO | [`src/modeling.py`](../src/modeling.py), [`src/metrics.py`](../src/metrics.py), [`src/robustness.py`](../src/robustness.py) | [`12_cv_resumen_modelos.csv`](../outputs/tables/12_cv_resumen_modelos.csv), [`32_prueba_aleatorizacion_etiquetas.csv`](../outputs/tables/32_prueba_aleatorizacion_etiquetas.csv) |
| Anexo I | Aplicación y ruta hospitalaria | [`app.py`](../app.py), [`src/app_logic.py`](../src/app_logic.py), [`tests/test_streamlit_app.py`](../tests/test_streamlit_app.py) | [Aplicación pública](https://tfm-medicina-personalizada.streamlit.app/) |
| Anexo J | Trazabilidad del uso de IA | [`tools/build_manifest.py`](../tools/build_manifest.py), [`tools/verify_repository.py`](../tools/verify_repository.py) | [`REGISTRO_USO_IA.md`](REGISTRO_USO_IA.md) |
| Anexo K | Repositorio y acceso al código | [`tools/verify_repository.py`](../tools/verify_repository.py), [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | [GitHub Actions](https://github.com/catrilaf/TFM-medicina-personalizada/actions) |
| Anexo L | Hitos de implementación en Python | [`run_all.py`](../run_all.py), [`src/analysis.py`](../src/analysis.py), [`src/figures.py`](../src/figures.py) | [`notebook ejecutado`](../notebooks/01_estudio_completo_oncologia.ipynb), [`informe HTML`](../reports/Estudio_Completo_Oncologia.html) |

## Secuencia recomendada de auditoría

1. Ejecutar `python run_all.py` para reconstruir datos, modelos y resultados.
2. Ejecutar `python -m pytest -q` para comprobar contratos y comportamiento.
3. Ejecutar `python tools/verify_repository.py` para validar inventario,
   métricas, decisión NO-GO y correspondencia entre anexos y scripts.
4. Contrastar las salidas con la memoria y con
   [`INDICE_AUDITORIA.md`](INDICE_AUDITORIA.md).
