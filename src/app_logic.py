"""Lógica pura y comprobable utilizada por la interfaz Streamlit."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import CORE_FEATURES


def build_input_frame(values: dict[str, object]) -> pd.DataFrame:
    """Construye una fila en el mismo orden y contrato que el entrenamiento."""

    missing = [feature for feature in CORE_FEATURES if feature not in values]
    if missing:
        raise ValueError(f"Faltan variables requeridas: {', '.join(missing)}")
    return pd.DataFrame([{feature: values[feature] for feature in CORE_FEATURES}])


def uncertainty_indicators(probabilities: np.ndarray) -> dict[str, float]:
    """Resume confianza, margen top-2 y entropía normalizada."""

    values = np.asarray(probabilities, dtype=float)
    if values.ndim != 1 or len(values) < 2:
        raise ValueError("Se requiere un vector de al menos dos probabilidades.")
    if not np.isclose(values.sum(), 1.0, atol=1e-6):
        raise ValueError("Las probabilidades deben sumar 1.")
    sorted_values = np.sort(values)[::-1]
    entropy = -float(np.sum(values * np.log(np.clip(values, 1e-12, 1.0)))) / np.log(len(values))
    return {
        "confianza_maxima": float(sorted_values[0]),
        "margen_top2": float(sorted_values[0] - sorted_values[1]),
        "entropia_normalizada": entropy,
    }


def clinical_consistency_alerts(tumor_stage: str, metastasis_status: str) -> list[str]:
    """Señala combinaciones atípicas sin corregir ni emitir consejo clínico."""

    alerts = []
    if tumor_stage == "IV" and metastasis_status == "No":
        alerts.append(
            "Combinación atípica en el dataset: estadio IV sin metástasis registrada. "
            "Debe revisarse la definición y procedencia del dato."
        )
    if tumor_stage == "I" and metastasis_status == "Yes":
        alerts.append(
            "Combinación atípica en el dataset: estadio I con metástasis registrada. "
            "No se corrige automáticamente y requiere revisión de dominio."
        )
    return alerts
