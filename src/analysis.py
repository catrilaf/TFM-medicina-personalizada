"""Orquestador del estudio reproducible de minería de datos."""

from __future__ import annotations

import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import scipy
import seaborn as sns
import sklearn
from sklearn.base import clone

from .clustering import run_clustering
from .config import (
    CATEGORICAL_FEATURES,
    CORE_FEATURES,
    CV_REPEATS,
    CV_SPLITS,
    NUMERIC_FEATURES,
    SEED,
    TARGET,
    TEST_SIZE,
    project_paths,
)
from .data import (
    build_professor_sample,
    clinical_consistency_table,
    data_quality_overview,
    descriptive_outcomes_by_regimen,
    iqr_outlier_table,
    leakage_audit_table,
    load_datasets,
    missingness_table,
    numeric_summary,
    numeric_target_associations,
    predictor_profile_audit,
    target_associations,
    target_distribution,
)
from .figures import (
    plot_associations,
    plot_calibration,
    plot_categorical_eda,
    plot_cluster_evaluation,
    plot_cluster_pca,
    plot_confidence,
    plot_confusion,
    plot_cv_comparison,
    plot_feature_importance,
    plot_label_randomization,
    plot_learning_curve,
    plot_numeric_eda,
    plot_paired_cv,
    plot_permutation_importance,
    plot_selective_performance,
    plot_subgroups,
    plot_target_by_cancer,
    plot_target_distribution,
)
from .metrics import (
    classification_report_table,
    confusion_tables,
    evaluate_multiclass,
    subgroup_performance,
)
from .modeling import (
    build_model_pipelines,
    cross_validate_models,
    feature_importance_table,
    fit_full_and_save,
    prediction_table,
    select_experimental_model,
    split_holdout,
)
from .robustness import (
    bootstrap_metric_intervals,
    holdout_label_randomization_test,
    learning_curve_table,
    paired_cv_comparisons,
    permutation_importance_table,
    probabilistic_skill_table,
    selective_performance_table,
    top_label_calibration_table,
)


def _ensure_directories(paths: dict[str, Path]) -> None:
    for key in ["outputs", "figures", "tables", "models", "reports"]:
        paths[key].mkdir(parents=True, exist_ok=True)


def _save_table(df: pd.DataFrame, path: Path, index: bool = False) -> None:
    df.to_csv(path, index=index, encoding="utf-8")


def _evaluate_all_holdout_models(X_train, X_test, y_train, y_test):
    rows: list[dict[str, float | str]] = []
    fitted: dict[str, object] = {}
    outputs: dict[str, dict[str, object]] = {}
    for name, pipeline in build_model_pipelines().items():
        model = clone(pipeline)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        probabilities = model.predict_proba(X_test)
        classes = model.named_steps["modelo"].classes_
        metrics = evaluate_multiclass(y_test, y_pred, probabilities, classes)
        rows.append({"modelo": name, **metrics})
        fitted[name] = model
        outputs[name] = {
            "predictions": y_pred,
            "probabilities": probabilities,
            "classes": classes,
            "metrics": metrics,
        }
    return pd.DataFrame(rows).sort_values("f1_macro", ascending=False), fitted, outputs


def run_analysis(project_root: Path | str) -> dict[str, object]:
    """Ejecuta el estudio completo y guarda artefactos auditables."""

    paths = project_paths(Path(project_root))
    _ensure_directories(paths)
    np.random.seed(SEED)

    clean, model_ready = load_datasets(paths["data"])

    # Fase 1 - Comprensión y calidad del dato.
    quality = data_quality_overview(clean, model_ready)
    missing = missingness_table(clean)
    numeric = numeric_summary(model_ready)
    outliers = iqr_outlier_table(model_ready)
    consistency = clinical_consistency_table(model_ready)
    leakage = leakage_audit_table(model_ready)
    distribution = target_distribution(model_ready)
    associations = target_associations(model_ready)
    numeric_associations = numeric_target_associations(model_ready)
    profile_integrity = predictor_profile_audit(model_ready)
    outcomes = descriptive_outcomes_by_regimen(model_ready)
    professor_sample = build_professor_sample(model_ready)

    _save_table(quality, paths["tables"] / "01_resumen_calidad.csv")
    _save_table(missing, paths["tables"] / "02_faltantes_por_variable.csv")
    _save_table(numeric, paths["tables"] / "03_resumen_numerico.csv")
    _save_table(outliers, paths["tables"] / "04_auditoria_outliers_iqr.csv")
    _save_table(consistency, paths["tables"] / "05_consistencia_clinica.csv")
    _save_table(leakage, paths["tables"] / "06_auditoria_leakage.csv")
    _save_table(distribution, paths["tables"] / "07_distribucion_target.csv")
    _save_table(associations, paths["tables"] / "08_asociaciones_cramers_v.csv")
    _save_table(outcomes, paths["tables"] / "09_outcomes_descriptivos_por_regimen.csv")
    professor_sample.to_csv(
        paths["data"] / "chemotherapy_patient_data_muestra_revision_profesor_1000.csv",
        index=False,
    )

    plot_target_distribution(distribution, paths["figures"] / "01_distribucion_target.png")
    plot_numeric_eda(model_ready, paths["figures"] / "02_eda_numericas.png")
    plot_categorical_eda(model_ready, paths["figures"] / "03_eda_categoricas.png")
    plot_target_by_cancer(model_ready, paths["figures"] / "04_regimen_por_cancer.png")
    plot_associations(associations, paths["figures"] / "05_asociaciones_target.png")

    # Fases 2 a 5 - Split congelado, CV solo en train y evaluación interna en holdout.
    X_train, X_test, y_train, y_test = split_holdout(model_ready, TARGET)
    split_manifest = pd.DataFrame(
        [
            {
                "subconjunto": "train",
                "n": len(X_train),
                "proporcion": len(X_train) / len(model_ready),
                "semilla": SEED,
            },
            {
                "subconjunto": "holdout_test",
                "n": len(X_test),
                "proporcion": len(X_test) / len(model_ready),
                "semilla": SEED,
            },
        ]
    )
    _save_table(split_manifest, paths["tables"] / "10_manifest_split.csv")

    cv_long, cv_summary = cross_validate_models(X_train, y_train)
    _save_table(cv_long, paths["tables"] / "11_cv_resultados_por_fold.csv")
    _save_table(cv_summary, paths["tables"] / "12_cv_resumen_modelos.csv")
    plot_cv_comparison(cv_summary, paths["figures"] / "06_comparacion_cv.png")

    selected_model = select_experimental_model(cv_summary)
    holdout_all, fitted_models, holdout_outputs = _evaluate_all_holdout_models(
        X_train,
        X_test,
        y_train,
        y_test,
    )
    _save_table(holdout_all, paths["tables"] / "13_metricas_holdout_modelos.csv")

    selected_pipeline = fitted_models[selected_model]
    selected_output = holdout_outputs[selected_model]
    predictions = selected_output["predictions"]
    probabilities = selected_output["probabilities"]
    classes = selected_output["classes"]
    selected_metrics = selected_output["metrics"]

    report_table = classification_report_table(y_test, predictions)
    _save_table(report_table, paths["tables"] / "14_classification_report_holdout.csv")
    raw_cm, norm_cm = confusion_tables(y_test, predictions, classes)
    _save_table(raw_cm, paths["tables"] / "15_matriz_confusion_holdout.csv", index=True)
    _save_table(norm_cm, paths["tables"] / "16_matriz_confusion_normalizada.csv", index=True)
    plot_confusion(norm_cm, paths["figures"] / "07_matriz_confusion.png")

    test_rows = model_ready.loc[y_test.index]
    predictions_df = prediction_table(
        test_rows["patient_id"],
        y_test,
        predictions,
        probabilities,
        classes,
    )
    _save_table(predictions_df, paths["tables"] / "17_predicciones_holdout.csv")
    plot_confidence(predictions_df, paths["figures"] / "08_confianza_holdout.png")

    importance = feature_importance_table(selected_pipeline)
    _save_table(importance, paths["tables"] / "18_importancia_variables.csv")
    if not importance.empty:
        plot_feature_importance(importance, paths["figures"] / "09_importancia_variables.png")

    subgroup_frame = test_rows.copy()
    subgroup_results = subgroup_performance(
        subgroup_frame,
        y_test,
        predictions,
        ["sex", "age_group"],
    )
    _save_table(subgroup_results, paths["tables"] / "19_rendimiento_subgrupos.csv")
    plot_subgroups(subgroup_results, paths["figures"] / "10_rendimiento_subgrupos.png")

    # Fase no supervisada - segmentación descriptiva, no recomendación.
    cluster_results = run_clustering(model_ready)
    _save_table(cluster_results["evaluation"], paths["tables"] / "20_clustering_evaluacion_k.csv")
    _save_table(cluster_results["profiles"], paths["tables"] / "21_clustering_perfiles.csv")
    _save_table(
        cluster_results["target_association"],
        paths["tables"] / "22_clustering_asociacion_target.csv",
    )
    _save_table(
        cluster_results["assignments"],
        paths["tables"] / "23_clustering_asignaciones.csv",
    )
    _save_table(cluster_results["pca_sample"], paths["tables"] / "24_clustering_pca_muestra.csv")
    plot_cluster_evaluation(
        cluster_results["evaluation"],
        paths["figures"] / "11_clustering_metricas.png",
    )
    plot_cluster_pca(cluster_results["pca_sample"], paths["figures"] / "12_clustering_pca.png")

    # Robustez adicional - intervalos, comparación pareada, calibración,
    # importancia por permutación y comportamiento selectivo de la abstención.
    bootstrap_intervals = bootstrap_metric_intervals(
        y_test,
        predictions,
        probabilities,
        classes,
    )
    paired_comparisons = paired_cv_comparisons(cv_long, selected_model)
    calibration, ece_top_label = top_label_calibration_table(
        y_test,
        probabilities,
        classes,
    )
    selective = selective_performance_table(y_test, predictions, probabilities)
    permutation = permutation_importance_table(selected_pipeline, X_test, y_test)
    randomization, randomization_distribution = holdout_label_randomization_test(
        y_test,
        predictions,
    )
    learning = learning_curve_table(
        build_model_pipelines()[selected_model],
        X_train,
        y_train,
        selected_model,
    )
    probabilistic_skill = probabilistic_skill_table(
        y_train,
        y_test,
        probabilities,
        classes,
        selected_model,
    )

    _save_table(bootstrap_intervals, paths["tables"] / "25_ic_bootstrap_holdout.csv")
    _save_table(paired_comparisons, paths["tables"] / "26_comparaciones_cv_pareadas.csv")
    _save_table(calibration, paths["tables"] / "27_calibracion_top_label.csv")
    _save_table(selective, paths["tables"] / "28_rendimiento_selectivo_umbral.csv")
    _save_table(permutation, paths["tables"] / "29_importancia_permutacion.csv")
    _save_table(profile_integrity, paths["tables"] / "30_integridad_perfiles_predictores.csv")
    _save_table(numeric_associations, paths["tables"] / "31_asociaciones_numericas_target.csv")
    _save_table(randomization, paths["tables"] / "32_prueba_aleatorizacion_etiquetas.csv")
    _save_table(
        randomization_distribution,
        paths["tables"] / "33_distribucion_nula_f1.csv",
    )
    _save_table(learning, paths["tables"] / "34_curva_aprendizaje.csv")
    _save_table(probabilistic_skill, paths["tables"] / "35_skill_probabilistico.csv")
    plot_calibration(calibration, paths["figures"] / "13_calibracion_top_label.png")
    plot_selective_performance(selective, paths["figures"] / "14_rendimiento_selectivo.png")
    plot_permutation_importance(permutation, paths["figures"] / "15_importancia_permutacion.png")
    plot_paired_cv(paired_comparisons, paths["figures"] / "16_comparaciones_cv_pareadas.png")
    plot_label_randomization(
        randomization,
        randomization_distribution,
        paths["figures"] / "17_prueba_aleatorizacion.png",
    )
    plot_learning_curve(learning, paths["figures"] / "18_curva_aprendizaje.png")

    # Modelo final para el prototipo: se reentrena en todos los datos después de
    # conservar la evaluación del holdout interno y sus auditorías post hoc.
    full_model_path = paths["models"] / "modelo_experimental_full.joblib"
    fit_full_and_save(
        selected_model,
        model_ready[CORE_FEATURES],
        model_ready[TARGET],
        full_model_path,
    )
    cv_selected = cv_summary.loc[cv_summary["modelo"] == selected_model].iloc[0]
    dummy_stratified = cv_summary.loc[
        cv_summary["modelo"] == "Dummy estratificado", "f1_macro_mean"
    ].iloc[0]
    delta_f1 = float(cv_selected["f1_macro_mean"] - dummy_stratified)
    abstention_threshold = 0.45
    abstention_rate = float((predictions_df["confianza_maxima"] < abstention_threshold).mean())
    f1_interval = bootstrap_intervals.loc[bootstrap_intervals["metrica"] == "f1_macro"].iloc[0]
    balanced_interval = bootstrap_intervals.loc[
        bootstrap_intervals["metrica"] == "balanced_accuracy"
    ].iloc[0]
    dummy_comparison = paired_comparisons.loc[
        paired_comparisons["comparador"] == "Dummy estratificado"
    ].iloc[0]
    randomization_result = randomization.iloc[0]
    selected_probabilistic = probabilistic_skill.loc[
        probabilistic_skill["modelo"] == selected_model
    ].iloc[0]
    selected_learning_final = learning.loc[
        (learning["modelo"] == selected_model) & (learning["fraccion_train"] == 1.0)
    ].iloc[0]

    # Regla preespecificada de suficiencia de señal. No equivale a aprobación
    # clínica: aun superándola serían necesarios datos externos y evaluación
    # prospectiva. La comparación pareada se conserva como diagnóstico
    # exploratorio porque los folds repetidos no son independientes.
    signal_gate = {
        "delta_f1_vs_dummy_ge_0_01": delta_f1 >= 0.01,
        "paired_cv_ci_lower_gt_0_exploratory": (
            float(dummy_comparison["delta_f1_ic95_inferior"]) > 0
        ),
        "randomization_p_lt_0_05": (
            float(randomization_result["p_unilateral_superior"]) < 0.05
        ),
        "positive_brier_skill": (
            float(selected_probabilistic["brier_skill_vs_prevalencia"]) > 0
        ),
        "positive_log_loss_gain": (
            float(selected_probabilistic["ganancia_log_loss_vs_prevalencia"]) > 0
        ),
        "nonzero_coverage_at_safety_threshold": abstention_rate < 1.0,
    }
    signal_gate_passed = all(signal_gate.values())
    evidence_conclusion = (
        "Se observa una señal exploratoria que aún requiere validación externa."
        if signal_gate_passed
        else "No se demuestra señal predictiva útil: el modelo no supera los criterios preespecificados frente al azar."
    )

    candidate_model_hyperparameters = {
        name: pipeline.named_steps["modelo"].get_params(deep=False)
        for name, pipeline in build_model_pipelines().items()
    }

    metadata = {
        "generated_on": datetime.now(timezone.utc).date().isoformat(),
        "seed": SEED,
        "target": TARGET,
        "features": CORE_FEATURES,
        "classes": [str(item) for item in classes],
        "selected_model": selected_model,
        "selection_criterion": "Mayor F1 macro medio en CV repetida entre modelos no Dummy",
        "validation_configuration": {
            "holdout_fraction": TEST_SIZE,
            "holdout_stratified": True,
            "cv_splits": CV_SPLITS,
            "cv_repeats": CV_REPEATS,
            "cv_stratified": True,
        },
        "preprocessing_configuration": {
            "categorical_features": CATEGORICAL_FEATURES,
            "categorical_encoder": "OneHotEncoder(handle_unknown='ignore')",
            "numeric_features": NUMERIC_FEATURES,
            "numeric_scaler": "StandardScaler",
            "fit_scope": "Dentro de cada Pipeline y cada fold",
        },
        "candidate_model_hyperparameters": candidate_model_hyperparameters,
        "selected_model_hyperparameters": candidate_model_hyperparameters[
            selected_model
        ],
        "cv_f1_macro_mean": float(cv_selected["f1_macro_mean"]),
        "cv_f1_macro_std": float(cv_selected["f1_macro_std"]),
        "cv_balanced_accuracy_mean": float(cv_selected["balanced_accuracy_mean"]),
        "delta_f1_vs_dummy_stratified": delta_f1,
        "holdout_metrics": selected_metrics,
        "holdout_intervals_95": {
            "f1_macro": [
                float(f1_interval["ic95_inferior"]),
                float(f1_interval["ic95_superior"]),
            ],
            "balanced_accuracy": [
                float(balanced_interval["ic95_inferior"]),
                float(balanced_interval["ic95_superior"]),
            ],
        },
        "paired_cv_vs_dummy_stratified": {
            "delta_f1_macro_mean": float(dummy_comparison["delta_f1_macro_medio"]),
            "ci95": [
                float(dummy_comparison["delta_f1_ic95_inferior"]),
                float(dummy_comparison["delta_f1_ic95_superior"]),
            ],
            "p_wilcoxon": float(dummy_comparison["p_wilcoxon_f1"]),
        },
        "ece_top_label": ece_top_label,
        "holdout_label_randomization": {
            "p_value_one_sided": float(randomization_result["p_unilateral_superior"]),
            "null_f1_mean": float(randomization_result["f1_macro_nulo_medio"]),
            "n_permutations": int(randomization_result["n_permutaciones"]),
        },
        "probabilistic_skill_vs_prevalence": {
            "brier_skill": float(selected_probabilistic["brier_skill_vs_prevalencia"]),
            "log_loss_gain": float(
                selected_probabilistic["ganancia_log_loss_vs_prevalencia"]
            ),
        },
        "learning_curve_final_validation_f1": float(
            selected_learning_final["f1_validacion_media"]
        ),
        "abstention_threshold": abstention_threshold,
        "abstention_threshold_status": (
            "Umbral ilustrativo de seguridad; no optimizado ni validado clínicamente."
        ),
        "holdout_abstention_rate": abstention_rate,
        "signal_gate": signal_gate,
        "signal_gate_passed": signal_gate_passed,
        "clinical_go": False,
        "clinical_go_reason": (
            "No existe validación clínica externa ni prospectiva; el prototipo "
            "no puede recomendar tratamientos."
        ),
        "evidence_conclusion": evidence_conclusion,
        "use_restriction": "Prototipo académico. No prescribe ni recomienda tratamientos.",
        "data_provenance": (
            "Archivo y licencia verificados contra Kaggle v1; procedencia clínica, "
            "institución, protocolo y naturaleza real o sintética no acreditados."
        ),
        "category_values": {
            column: sorted(model_ready[column].dropna().astype(str).unique().tolist())
            for column in [
                "sex",
                "smoking_status",
                "cancer_type",
                "genetic_mutation",
                "tumor_stage",
                "metastasis_status",
            ]
        },
        "numeric_ranges": {
            column: {
                "min": float(model_ready[column].min()),
                "max": float(model_ready[column].max()),
                "median": float(model_ready[column].median()),
            }
            for column in ["age", "bmi", "tumor_size_cm"]
        },
    }
    with (paths["models"] / "model_metadata.json").open("w", encoding="utf-8") as stream:
        json.dump(metadata, stream, ensure_ascii=False, indent=2)

    environment = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scikit_learn": sklearn.__version__,
        "scipy": scipy.__version__,
        "matplotlib": matplotlib.__version__,
        "seaborn": sns.__version__,
        "seed": SEED,
    }
    with (paths["outputs"] / "environment_versions.json").open("w", encoding="utf-8") as stream:
        json.dump(environment, stream, ensure_ascii=False, indent=2)

    summary = {
        "dataset_rows_clean": len(clean),
        "dataset_rows_model_ready": len(model_ready),
        "selected_model": selected_model,
        "cv_f1_macro_mean": float(cv_selected["f1_macro_mean"]),
        "cv_balanced_accuracy_mean": float(cv_selected["balanced_accuracy_mean"]),
        "holdout_f1_macro": float(selected_metrics["f1_macro"]),
        "holdout_balanced_accuracy": float(selected_metrics["balanced_accuracy"]),
        "holdout_f1_macro_ci95": [
            float(f1_interval["ic95_inferior"]),
            float(f1_interval["ic95_superior"]),
        ],
        "holdout_balanced_accuracy_ci95": [
            float(balanced_interval["ic95_inferior"]),
            float(balanced_interval["ic95_superior"]),
        ],
        "paired_cv_delta_f1_vs_dummy": float(dummy_comparison["delta_f1_macro_medio"]),
        "paired_cv_delta_f1_ci95": [
            float(dummy_comparison["delta_f1_ic95_inferior"]),
            float(dummy_comparison["delta_f1_ic95_superior"]),
        ],
        "ece_top_label": ece_top_label,
        "label_randomization_p_value": float(
            randomization_result["p_unilateral_superior"]
        ),
        "label_randomization_null_f1_mean": float(
            randomization_result["f1_macro_nulo_medio"]
        ),
        "brier_skill_vs_prevalence": float(
            selected_probabilistic["brier_skill_vs_prevalencia"]
        ),
        "log_loss_gain_vs_prevalence": float(
            selected_probabilistic["ganancia_log_loss_vs_prevalencia"]
        ),
        "learning_curve_final_validation_f1": float(
            selected_learning_final["f1_validacion_media"]
        ),
        "dummy_stratified_cv_f1_macro": float(dummy_stratified),
        "delta_f1_vs_dummy": delta_f1,
        "abstention_rate_holdout": abstention_rate,
        "best_k_clustering": int(cluster_results["best_k"]),
        "clustering_silhouette": float(
            cluster_results["evaluation"]
            .loc[cluster_results["evaluation"]["k"] == cluster_results["best_k"], "silhouette"]
            .iloc[0]
        ),
        "evidence_conclusion": evidence_conclusion,
    }
    with (paths["outputs"] / "analysis_summary.json").open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
    return summary
