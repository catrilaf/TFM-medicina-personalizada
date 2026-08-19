"""Genera el notebook docente a partir del pipeline modular."""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "01_estudio_completo_oncologia.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


cells = [
    md(
        """
# Estudio completo de minería de datos aplicado a oncología

## Sistema Web de Recomendación de Tratamientos Personalizados en Oncología

**Entrega académica reproducible en Python**  
Autor: Enrique Catrilaf González  
Curso: Máster en Inteligencia Artificial Aplicada

> Advertencia: este estudio clasifica una etiqueta histórica de un dataset académico. No prescribe, no recomienda tratamientos y no demuestra eficacia clínica.

La organización reproduce el enfoque de los estudios docentes Ames Housing y Super Telco Churn: CRISP-DM, auditoría de calidad, prevención de leakage, split congelado, validación cruzada, torneo de modelos, análisis de errores, segmentación y limitaciones.
"""
    ),
    md(
        """
## 0. Reproducibilidad

El notebook invoca el mismo pipeline que `python run_all.py`. La ejecución comienza verificando el SHA-256 del CSV original de Kaggle v1 y reconstruyendo los datasets derivados. Todas las transformaciones del modelo se aprenden dentro de cada fold mediante `Pipeline` y `ColumnTransformer`. La semilla global es 42.
"""
    ),
    code(
        """
from pathlib import Path
import json
import sys
import pandas as pd
from IPython.display import Image, display, Markdown

ROOT = Path.cwd().resolve()
if not (ROOT / "run_all.py").exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

from src import run_analysis
from src.preprocessing import rebuild_from_raw

preprocessing = rebuild_from_raw(ROOT)
summary = run_analysis(ROOT)
{"preprocessing": preprocessing, "analysis": summary}
"""
    ),
    md(
        """
## 1. Comprensión del problema (CRISP-DM)

La pregunta computacional es: **¿pueden las variables pretratamiento predecir el régimen de quimioterapia registrado?**

La pregunta clínica "¿cuál es el mejor tratamiento?" es diferente y no puede contestarse con estos datos. Requeriría indicación clínica, comparadores, temporalidad, confusores, guías, outcomes acreditados y validación prospectiva.
"""
    ),
    md("## 2. Comprensión y calidad de los datos"),
    code(
        """
quality = pd.read_csv(ROOT / "outputs/tables/01_resumen_calidad.csv")
consistency = pd.read_csv(ROOT / "outputs/tables/05_consistencia_clinica.csv")
integrity = pd.read_csv(ROOT / "outputs/tables/30_integridad_perfiles_predictores.csv")
numeric_associations = pd.read_csv(ROOT / "outputs/tables/31_asociaciones_numericas_target.csv")
display(quality)
display(consistency)
display(integrity)
display(numeric_associations.round(6))
"""
    ),
    md(
        """
Los controles cruzados se reportan, pero no se corrigen automáticamente. El archivo y su licencia están verificados contra Kaggle v1, pero la procedencia clínica no está acreditada; por ello no es posible distinguir con seguridad entre errores, definiciones no documentadas y un mecanismo de generación desconocido.
"""
    ),
    md("### 2.1. Distribución del target y EDA"),
    code(
        """
display(pd.read_csv(ROOT / "outputs/tables/07_distribucion_target.csv"))
display(Image(filename=str(ROOT / "outputs/figures/01_distribucion_target.png"), width=760))
display(Image(filename=str(ROOT / "outputs/figures/02_eda_numericas.png"), width=980))
display(Image(filename=str(ROOT / "outputs/figures/03_eda_categoricas.png"), width=980))
"""
    ),
    md("### 2.2. ¿Existe asociación entre contexto clínico y régimen?"),
    code(
        """
associations = pd.read_csv(ROOT / "outputs/tables/08_asociaciones_cramers_v.csv")
display(associations)
display(Image(filename=str(ROOT / "outputs/figures/04_regimen_por_cancer.png"), width=760))
display(Image(filename=str(ROOT / "outputs/figures/05_asociaciones_target.png"), width=760))
"""
    ),
    md(
        """
Los valores de V de Cramér corregido son prácticamente cero. Esta es una señal de alerta previa al modelado: el target parece casi independiente de variables que deberían ser clínicamente relevantes, como tipo de cáncer, estadio o mutación.
"""
    ),
    md("## 3. Preparación y auditoría de leakage"),
    code(
        """
leakage = pd.read_csv(ROOT / "outputs/tables/06_auditoria_leakage.csv")
display(leakage)
"""
    ),
    md(
        """
Solo se utilizan variables conocidas antes de la elección terapéutica. Dosis, ciclos, toxicidad, respuesta y supervivencia se excluyen porque contienen información posterior. Las variables derivadas redundantes también se excluyen para mantener parsimonia.
"""
    ),
    md("## 4. Diseño experimental"),
    code(
        """
split_manifest = pd.read_csv(ROOT / "outputs/tables/10_manifest_split.csv")
display(split_manifest)
"""
    ),
    md(
        """
Se reserva un holdout estratificado del 25 %. Dentro del 75 % de entrenamiento se ejecuta una validación cruzada estratificada de 5 folds y 2 repeticiones. El holdout no participa en la elección del modelo.
"""
    ),
    md("## 5. Torneo de modelos"),
    code(
        """
cv = pd.read_csv(ROOT / "outputs/tables/12_cv_resumen_modelos.csv")
display(cv.round(4))
display(Image(filename=str(ROOT / "outputs/figures/06_comparacion_cv.png"), width=820))
"""
    ),
    md(
        """
El modelo experimental se selecciona por F1 macro medio entre los modelos no Dummy. El resultado debe compararse siempre con el Dummy estratificado. Una diferencia de unas milésimas, dentro de la variabilidad entre folds, no constituye una mejora material.
"""
    ),
    md("## 6. Evaluación final en holdout"),
    code(
        """
holdout = pd.read_csv(ROOT / "outputs/tables/13_metricas_holdout_modelos.csv")
display(holdout.round(4))
display(Image(filename=str(ROOT / "outputs/figures/07_matriz_confusion.png"), width=620))
display(Image(filename=str(ROOT / "outputs/figures/08_confianza_holdout.png"), width=760))
"""
    ),
    md(
        """
Balanced accuracy y F1 macro próximas a 0,25 son consistentes con azar en cuatro clases. La confianza máxima también es baja; por eso la interfaz aplica abstención en lugar de convertir una probabilidad débil en una recomendación.
"""
    ),
    md("### 6.1. Robustez, calibración y comparación pareada"),
    code(
        """
bootstrap = pd.read_csv(ROOT / "outputs/tables/25_ic_bootstrap_holdout.csv")
paired = pd.read_csv(ROOT / "outputs/tables/26_comparaciones_cv_pareadas.csv")
calibration = pd.read_csv(ROOT / "outputs/tables/27_calibracion_top_label.csv")
selective = pd.read_csv(ROOT / "outputs/tables/28_rendimiento_selectivo_umbral.csv")
randomization = pd.read_csv(ROOT / "outputs/tables/32_prueba_aleatorizacion_etiquetas.csv")
learning = pd.read_csv(ROOT / "outputs/tables/34_curva_aprendizaje.csv")
probabilistic_skill = pd.read_csv(ROOT / "outputs/tables/35_skill_probabilistico.csv")
display(bootstrap.round(4))
display(paired.round(4))
display(calibration.round(4))
display(selective.round(4))
display(randomization.round(4))
display(learning.round(4))
display(probabilistic_skill.round(4))
display(Image(filename=str(ROOT / "outputs/figures/13_calibracion_top_label.png"), width=650))
display(Image(filename=str(ROOT / "outputs/figures/14_rendimiento_selectivo.png"), width=760))
display(Image(filename=str(ROOT / "outputs/figures/16_comparaciones_cv_pareadas.png"), width=760))
display(Image(filename=str(ROOT / "outputs/figures/17_prueba_aleatorizacion.png"), width=760))
display(Image(filename=str(ROOT / "outputs/figures/18_curva_aprendizaje.png"), width=980))
"""
    ),
    md(
        """
Los intervalos bootstrap cuantifican incertidumbre del holdout. La comparación pareada utiliza los mismos folds para todos los modelos; si el intervalo de la diferencia incluye cero, no existe evidencia de una ventaja estable. La prueba de aleatorización contrasta directamente la concordancia observada con la independencia entre predicción y etiqueta. La curva de aprendizaje comprueba si más registros mejoran la generalización, y el skill probabilístico compara contra prevalencias aprendidas solo en train. La curva selectiva muestra que aumentar el umbral reduce cobertura y no crea validación clínica.
"""
    ),
    md("## 7. Interpretación y auditoría por subgrupos"),
    code(
        """
importance = pd.read_csv(ROOT / "outputs/tables/18_importancia_variables.csv")
permutation = pd.read_csv(ROOT / "outputs/tables/29_importancia_permutacion.csv")
subgroups = pd.read_csv(ROOT / "outputs/tables/19_rendimiento_subgrupos.csv")
display(importance.head(15))
display(Image(filename=str(ROOT / "outputs/figures/09_importancia_variables.png"), width=780))
display(permutation.round(4))
display(Image(filename=str(ROOT / "outputs/figures/15_importancia_permutacion.png"), width=760))
display(subgroups.round(4))
display(Image(filename=str(ROOT / "outputs/figures/10_rendimiento_subgrupos.png"), width=780))
"""
    ),
    md(
        """
La importancia interna se contrasta con permutación sobre el holdout. Si la pérdida de F1 no es estable o cruza cero, la variable no aporta señal robusta. Ninguna importancia demuestra causalidad y, con rendimiento global equivalente al azar, las explicaciones individuales tampoco deben considerarse clínicamente fiables.
"""
    ),
    md("## 8. Aprendizaje no supervisado"),
    code(
        """
cluster_eval = pd.read_csv(ROOT / "outputs/tables/20_clustering_evaluacion_k.csv")
cluster_profiles = pd.read_csv(ROOT / "outputs/tables/21_clustering_perfiles.csv")
cluster_target = pd.read_csv(ROOT / "outputs/tables/22_clustering_asociacion_target.csv")
display(cluster_eval.round(4))
display(cluster_profiles.round(3))
display(cluster_target)
display(Image(filename=str(ROOT / "outputs/figures/11_clustering_metricas.png"), width=850))
display(Image(filename=str(ROOT / "outputs/figures/12_clustering_pca.png"), width=760))
"""
    ),
    md(
        """
El Silhouette bajo indica separación débil. Los clusters sirven para explorar perfiles, pero no deben convertirse en segmentos terapéuticos ni reglas de tratamiento.
"""
    ),
    md("## 9. Outcomes descriptivos"),
    code(
        """
outcomes = pd.read_csv(ROOT / "outputs/tables/09_outcomes_descriptivos_por_regimen.csv")
display(outcomes.round(4))
"""
    ),
    md(
        """
Las tasas se presentan como descripción del dataset. No son estimaciones de eficacia o seguridad comparada: no existe aleatorización, ajuste de confusores, temporalidad ni protocolo de seguimiento acreditado.
"""
    ),
    md("## 10. Conclusión y decisión de avance"),
    code(
        """
display(Markdown(f'''**Conclusión reproducible:** {summary["evidence_conclusion"]}

- Modelo experimental: {summary["selected_model"]}
- F1 macro CV: {summary["cv_f1_macro_mean"]:.4f}
- F1 macro Dummy estratificado: {summary["dummy_stratified_cv_f1_macro"]:.4f}
- F1 macro holdout: {summary["holdout_f1_macro"]:.4f}
- Balanced accuracy holdout: {summary["holdout_balanced_accuracy"]:.4f}
- Abstención en holdout: {summary["abstention_rate_holdout"]:.1%}
- p de aleatorización: {summary["label_randomization_p_value"]:.4f}
- Brier skill vs prevalencia: {summary["brier_skill_vs_prevalence"]:.4f}
- F1 final de curva de aprendizaje: {summary["learning_curve_final_validation_f1"]:.4f}
- Mejor Silhouette: {summary["clustering_silhouette"]:.4f}
'''))
"""
    ),
    md(
        """
### Decisión

El resultado establece un **NO-GO clínico** y conserva valor como prueba de concepto de ingeniería, auditoría de IA y control de abstención. Para avanzar se necesita una cohorte con procedencia clínica, temporalidad, variables relevantes, validación externa y revisión por especialistas.

### Material docente aplicado

- Tema 1: KDD y CRISP-DM.
- Tema 2: EDA, calidad, outliers y prevención de leakage.
- Tema 3: modelos supervisados y métricas.
- Tema 4: clustering, Silhouette y Davies-Bouldin.
- Tema 5: jerarquía visual y data storytelling.
- Tema 6: dashboard como interfaz de decisión, gobernanza y validación.
- Guía de métricas: balanced accuracy, F1, log-loss y métricas de clustering.
"""
    ),
]

notebook = nbf.v4.new_notebook(cells=cells)
notebook.metadata.kernelspec = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
notebook.metadata.language_info = {"name": "python", "version": "3.12"}
nbf.write(notebook, OUTPUT)
print(OUTPUT)
