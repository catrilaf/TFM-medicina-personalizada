"""Análisis de robustez, incertidumbre y utilidad selectiva.

Estas funciones complementan las métricas puntuales con intervalos de confianza,
comparaciones pareadas y controles de calibración. No convierten el experimento
en una validación clínica; cuantifican mejor la incertidumbre del resultado.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.model_selection import StratifiedKFold, learning_curve

from .config import SEED
from .metrics import evaluate_multiclass, multiclass_brier_score


def _stratified_bootstrap_indices(
    y_true: pd.Series | np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Muestrea con reemplazo dentro de cada clase y conserva su prevalencia."""

    values = np.asarray(y_true)
    sampled = []
    for label in np.unique(values):
        class_indices = np.flatnonzero(values == label)
        sampled.append(rng.choice(class_indices, size=len(class_indices), replace=True))
    combined = np.concatenate(sampled)
    rng.shuffle(combined)
    return combined


def bootstrap_metric_intervals(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    probabilities: np.ndarray,
    classes: np.ndarray,
    n_bootstrap: int = 500,
    seed: int = SEED,
) -> pd.DataFrame:
    """Calcula IC percentiles estratificados para métricas del holdout."""

    y_array = np.asarray(y_true)
    pred_array = np.asarray(y_pred)
    prob_array = np.asarray(probabilities)
    point = evaluate_multiclass(y_array, pred_array, prob_array, classes)
    metrics = [
        "balanced_accuracy",
        "f1_macro",
        "mcc",
        "log_loss",
        "brier_multiclase",
        "top2_accuracy",
    ]
    draws = {metric: [] for metric in metrics}
    rng = np.random.default_rng(seed)
    for _ in range(n_bootstrap):
        indices = _stratified_bootstrap_indices(y_array, rng)
        values = evaluate_multiclass(
            y_array[indices],
            pred_array[indices],
            prob_array[indices],
            classes,
        )
        for metric in metrics:
            draws[metric].append(values[metric])

    rows = []
    for metric in metrics:
        distribution = np.asarray(draws[metric], dtype=float)
        rows.append(
            {
                "metrica": metric,
                "estimacion": point[metric],
                "ic95_inferior": float(np.quantile(distribution, 0.025)),
                "ic95_superior": float(np.quantile(distribution, 0.975)),
                "n_bootstrap": n_bootstrap,
            }
        )
    return pd.DataFrame(rows)


def _bootstrap_mean_interval(
    values: np.ndarray,
    rng: np.random.Generator,
    n_bootstrap: int = 10000,
) -> tuple[float, float]:
    if len(values) == 0:
        return float("nan"), float("nan")
    draws = rng.choice(values, size=(n_bootstrap, len(values)), replace=True).mean(axis=1)
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def paired_cv_comparisons(
    cv_long: pd.DataFrame,
    selected_model: str,
    seed: int = SEED,
) -> pd.DataFrame:
    """Compara folds alineados del modelo seleccionado frente a cada alternativa.

    Los folds de una validación cruzada repetida se solapan y no constituyen
    observaciones independientes. Por ello, los intervalos bootstrap y la prueba
    de Wilcoxon se publican como diagnósticos exploratorios, no como inferencia
    confirmatoria ni como sustituto de una validación externa.
    """

    selected = cv_long.loc[
        cv_long["modelo"] == selected_model,
        ["fold", "f1_macro", "balanced_accuracy"],
    ].rename(
        columns={
            "f1_macro": "f1_seleccionado",
            "balanced_accuracy": "bal_seleccionado",
        }
    )
    rng = np.random.default_rng(seed)
    rows = []
    for comparator in cv_long["modelo"].drop_duplicates():
        if comparator == selected_model:
            continue
        other = cv_long.loc[
            cv_long["modelo"] == comparator,
            ["fold", "f1_macro", "balanced_accuracy"],
        ].rename(
            columns={
                "f1_macro": "f1_comparador",
                "balanced_accuracy": "bal_comparador",
            }
        )
        paired = selected.merge(other, on="fold", how="inner", validate="one_to_one")
        f1_diff = (paired["f1_seleccionado"] - paired["f1_comparador"]).to_numpy()
        bal_diff = (paired["bal_seleccionado"] - paired["bal_comparador"]).to_numpy()
        f1_low, f1_high = _bootstrap_mean_interval(f1_diff, rng)
        bal_low, bal_high = _bootstrap_mean_interval(bal_diff, rng)
        if np.allclose(f1_diff, 0):
            p_value = 1.0
        else:
            p_value = float(wilcoxon(f1_diff, alternative="two-sided").pvalue)
        rows.append(
            {
                "modelo_seleccionado": selected_model,
                "comparador": comparator,
                "n_pares": len(paired),
                "delta_f1_macro_medio": float(f1_diff.mean()),
                "delta_f1_ic95_inferior": f1_low,
                "delta_f1_ic95_superior": f1_high,
                "delta_balanced_accuracy_medio": float(bal_diff.mean()),
                "delta_balanced_accuracy_ic95_inferior": bal_low,
                "delta_balanced_accuracy_ic95_superior": bal_high,
                "p_wilcoxon_f1": p_value,
                "nota_inferencia": (
                    "Exploratoria: los folds de CV repetida se solapan y no son "
                    "observaciones independientes."
                ),
                "lectura": (
                    "Sin evidencia de diferencia"
                    if f1_low <= 0 <= f1_high
                    else "Diferencia consistente en los folds"
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("delta_f1_macro_medio", ascending=False)


def top_label_calibration_table(
    y_true: pd.Series | np.ndarray,
    probabilities: np.ndarray,
    classes: np.ndarray,
    n_bins: int = 10,
) -> tuple[pd.DataFrame, float]:
    """Resume calibración top-label y calcula Expected Calibration Error."""

    y_array = np.asarray(y_true)
    prob_array = np.asarray(probabilities)
    top_index = prob_array.argmax(axis=1)
    confidence = prob_array.max(axis=1)
    predicted = np.asarray(classes)[top_index]
    correct = (predicted == y_array).astype(float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.clip(np.digitize(confidence, edges, right=True) - 1, 0, n_bins - 1)
    rows = []
    for bin_id in range(n_bins):
        mask = bin_ids == bin_id
        if not mask.any():
            continue
        mean_confidence = float(confidence[mask].mean())
        observed_accuracy = float(correct[mask].mean())
        weight = float(mask.mean())
        rows.append(
            {
                "bin": bin_id + 1,
                "limite_inferior": edges[bin_id],
                "limite_superior": edges[bin_id + 1],
                "n": int(mask.sum()),
                "confianza_media": mean_confidence,
                "accuracy_observada": observed_accuracy,
                "brecha_calibracion": observed_accuracy - mean_confidence,
                "peso": weight,
            }
        )
    table = pd.DataFrame(rows)
    ece = float((table["peso"] * table["brecha_calibracion"].abs()).sum())
    return table, ece


def selective_performance_table(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    probabilities: np.ndarray,
    thresholds: tuple[float, ...] = (0.25, 0.27, 0.28, 0.30, 0.32, 0.35, 0.40, 0.45, 0.50),
) -> pd.DataFrame:
    """Evalúa cobertura y rendimiento entre los casos no abstencionistas."""

    y_array = np.asarray(y_true)
    pred_array = np.asarray(y_pred)
    confidence = np.asarray(probabilities).max(axis=1)
    rows = []
    for threshold in thresholds:
        retained = confidence >= threshold
        n_retained = int(retained.sum())
        if n_retained:
            accuracy = float(accuracy_score(y_array[retained], pred_array[retained]))
            f1_macro = float(
                f1_score(y_array[retained], pred_array[retained], average="macro", zero_division=0)
            )
            balanced = float(balanced_accuracy_score(y_array[retained], pred_array[retained]))
        else:
            accuracy = f1_macro = balanced = float("nan")
        rows.append(
            {
                "umbral": threshold,
                "n_no_abstenciones": n_retained,
                "cobertura": float(retained.mean()),
                "tasa_abstencion": float(1 - retained.mean()),
                "accuracy_selectiva": accuracy,
                "balanced_accuracy_selectiva": balanced,
                "f1_macro_selectivo": f1_macro,
            }
        )
    return pd.DataFrame(rows)


def permutation_importance_table(
    pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_repeats: int = 7,
    seed: int = SEED,
) -> pd.DataFrame:
    """Calcula importancia por permutación sobre variables originales del holdout."""

    result = permutation_importance(
        pipeline,
        X_test,
        y_test,
        scoring="f1_macro",
        n_repeats=n_repeats,
        random_state=seed,
        n_jobs=-1,
    )
    frame = pd.DataFrame(
        {
            "variable": X_test.columns,
            "importancia_media": result.importances_mean,
            "importancia_desviacion": result.importances_std,
            "limite_inferior_2sd": result.importances_mean - 2 * result.importances_std,
            "limite_superior_2sd": result.importances_mean + 2 * result.importances_std,
            "n_repeticiones": n_repeats,
            "metodo": "Disminución de F1 macro por permutación en holdout",
        }
    )
    return frame.sort_values("importancia_media", ascending=False).reset_index(drop=True)


def holdout_label_randomization_test(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    n_permutations: int = 5000,
    seed: int = SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Contrasta el F1 observado frente a etiquetas permutadas en el holdout.

    El modelo y sus predicciones permanecen fijos. La prueba pregunta si la
    concordancia observada es mayor que la esperable si target y predicción
    fueran independientes; no sustituye una validación externa.
    """

    true_values = np.asarray(y_true)
    pred_values = np.asarray(y_pred)
    classes = np.unique(np.concatenate([true_values, pred_values]))
    mapping = {label: index for index, label in enumerate(classes)}
    true_encoded = np.asarray([mapping[label] for label in true_values], dtype=np.int16)
    pred_encoded = np.asarray([mapping[label] for label in pred_values], dtype=np.int16)
    n_classes = len(classes)

    def fast_macro_f1(encoded_true: np.ndarray) -> float:
        matrix = np.bincount(
            encoded_true * n_classes + pred_encoded,
            minlength=n_classes * n_classes,
        ).reshape(n_classes, n_classes)
        true_positive = np.diag(matrix).astype(float)
        denominator = matrix.sum(axis=1) + matrix.sum(axis=0)
        class_f1 = np.divide(
            2 * true_positive,
            denominator,
            out=np.zeros_like(true_positive),
            where=denominator != 0,
        )
        return float(class_f1.mean())

    observed = fast_macro_f1(true_encoded)
    rng = np.random.default_rng(seed)
    null_values = np.empty(n_permutations, dtype=float)
    for index in range(n_permutations):
        null_values[index] = fast_macro_f1(rng.permutation(true_encoded))
    p_value = float((1 + np.sum(null_values >= observed)) / (n_permutations + 1))
    summary = pd.DataFrame(
        [
            {
                "f1_macro_observado": observed,
                "f1_macro_nulo_medio": float(null_values.mean()),
                "f1_macro_nulo_ic95_inferior": float(np.quantile(null_values, 0.025)),
                "f1_macro_nulo_ic95_superior": float(np.quantile(null_values, 0.975)),
                "p_unilateral_superior": p_value,
                "n_permutaciones": n_permutations,
                "conclusion": (
                    "Sin evidencia de concordancia superior al azar"
                    if p_value >= 0.05
                    else "Concordancia superior al azar en este holdout"
                ),
            }
        ]
    )
    distribution = pd.DataFrame(
        {"permutacion": np.arange(1, n_permutations + 1), "f1_macro_nulo": null_values}
    )
    return summary, distribution


def learning_curve_table(
    selected_pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    selected_model: str,
    seed: int = SEED,
) -> pd.DataFrame:
    """Diagnóstico de sesgo/varianza dentro de train para modelo y baseline."""

    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    candidates = {
        selected_model: clone(selected_pipeline),
        "Dummy estratificado": DummyClassifier(strategy="stratified", random_state=seed),
    }
    rows = []
    for name, estimator in candidates.items():
        sizes, train_scores, validation_scores = learning_curve(
            estimator,
            X_train,
            y_train,
            train_sizes=np.asarray([0.10, 0.25, 0.50, 0.75, 1.00]),
            cv=cv,
            scoring="f1_macro",
            n_jobs=-1,
            shuffle=True,
            random_state=seed,
        )
        for fraction, size, train_fold, validation_fold in zip(
            [0.10, 0.25, 0.50, 0.75, 1.00], sizes, train_scores, validation_scores
        ):
            rows.append(
                {
                    "modelo": name,
                    "fraccion_train": fraction,
                    "n_entrenamiento_por_fold": int(size),
                    "f1_train_media": float(train_fold.mean()),
                    "f1_train_std": float(train_fold.std(ddof=1)),
                    "f1_validacion_media": float(validation_fold.mean()),
                    "f1_validacion_std": float(validation_fold.std(ddof=1)),
                    "n_folds": cv.get_n_splits(),
                }
            )
    return pd.DataFrame(rows)


def probabilistic_skill_table(
    y_train: pd.Series,
    y_test: pd.Series | np.ndarray,
    selected_probabilities: np.ndarray,
    classes: np.ndarray,
    selected_model: str,
) -> pd.DataFrame:
    """Compara log-loss y Brier con baselines uniformes y de prevalencia train."""

    class_values = np.asarray(classes)
    n_test = len(y_test)
    train_prevalence = y_train.value_counts(normalize=True)
    prior_vector = np.asarray([train_prevalence.get(label, 0.0) for label in class_values])
    prior_vector = prior_vector / prior_vector.sum()
    candidates = {
        selected_model: np.asarray(selected_probabilities),
        "Baseline prevalencia train": np.tile(prior_vector, (n_test, 1)),
        "Baseline uniforme": np.full((n_test, len(class_values)), 1 / len(class_values)),
    }
    prior_probabilities = candidates["Baseline prevalencia train"]
    prior_brier = multiclass_brier_score(y_test, prior_probabilities, class_values)
    prior_log_loss = float(log_loss(y_test, prior_probabilities, labels=class_values))
    rows = []
    for name, probabilities in candidates.items():
        brier = multiclass_brier_score(y_test, probabilities, class_values)
        loss = float(log_loss(y_test, probabilities, labels=class_values))
        rows.append(
            {
                "modelo": name,
                "brier_multiclase": brier,
                "brier_skill_vs_prevalencia": float(1 - brier / prior_brier),
                "log_loss": loss,
                "ganancia_log_loss_vs_prevalencia": float(prior_log_loss - loss),
            }
        )
    return pd.DataFrame(rows)
