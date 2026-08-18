"""Métricas consistentes para clasificación multiclase."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    matthews_corrcoef,
    precision_score,
    recall_score,
    top_k_accuracy_score,
)


def multiclass_brier_score(
    y_true: pd.Series | np.ndarray,
    probabilities: np.ndarray,
    classes: np.ndarray,
) -> float:
    class_to_index = {label: idx for idx, label in enumerate(classes)}
    encoded = np.zeros_like(probabilities, dtype=float)
    for row, label in enumerate(np.asarray(y_true)):
        encoded[row, class_to_index[label]] = 1.0
    return float(np.mean(np.sum((probabilities - encoded) ** 2, axis=1)))


def evaluate_multiclass(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    probabilities: np.ndarray,
    classes: np.ndarray,
) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "log_loss": float(log_loss(y_true, probabilities, labels=classes)),
        "brier_multiclase": multiclass_brier_score(y_true, probabilities, classes),
        "top2_accuracy": float(top_k_accuracy_score(y_true, probabilities, k=2, labels=classes)),
        "confianza_media": float(np.max(probabilities, axis=1).mean()),
    }


def classification_report_table(y_true, y_pred) -> pd.DataFrame:
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    return pd.DataFrame(report).T.reset_index(names="clase")


def confusion_tables(y_true, y_pred, classes: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = confusion_matrix(y_true, y_pred, labels=classes)
    normalized = confusion_matrix(y_true, y_pred, labels=classes, normalize="true")
    raw_df = pd.DataFrame(raw, index=classes, columns=classes)
    norm_df = pd.DataFrame(normalized, index=classes, columns=classes)
    raw_df.index.name = "real"
    norm_df.index.name = "real"
    return raw_df, norm_df


def subgroup_performance(
    frame: pd.DataFrame,
    y_true: pd.Series,
    y_pred: np.ndarray,
    group_columns: list[str],
) -> pd.DataFrame:
    audit = frame[group_columns].copy()
    audit["y_true"] = np.asarray(y_true)
    audit["y_pred"] = np.asarray(y_pred)
    rows: list[dict[str, float | int | str]] = []
    for group_column in group_columns:
        for group_value, subset in audit.groupby(group_column, dropna=False):
            rows.append(
                {
                    "atributo": group_column,
                    "grupo": str(group_value),
                    "n": int(len(subset)),
                    "accuracy": float(accuracy_score(subset["y_true"], subset["y_pred"])),
                    "balanced_accuracy": float(
                        balanced_accuracy_score(subset["y_true"], subset["y_pred"])
                    ),
                    "f1_macro": float(
                        f1_score(subset["y_true"], subset["y_pred"], average="macro", zero_division=0)
                    ),
                }
            )
    return pd.DataFrame(rows)
