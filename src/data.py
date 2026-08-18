"""Carga, controles de calidad y auditoría de leakage."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, kruskal

from .config import (
    CORE_FEATURES,
    DERIVED_REDUNDANT_COLUMNS,
    ID_COLUMN,
    POST_TREATMENT_COLUMNS,
    SEED,
    TARGET,
)


def load_datasets(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean = pd.read_csv(data_dir / "chemotherapy_patient_data_clean_tfm.csv")
    model_ready = pd.read_csv(
        data_dir / "chemotherapy_patient_data_model_ready_recommender_tfm.csv"
    )
    return clean, model_ready


def data_quality_overview(clean: pd.DataFrame, model_ready: pd.DataFrame) -> pd.DataFrame:
    rows = [
        ("Registros del dataset limpio", len(clean)),
        ("Columnas del dataset limpio", clean.shape[1]),
        ("Registros con régimen conocido", len(model_ready)),
        ("Columnas del dataset model-ready", model_ready.shape[1]),
        ("Registros sin régimen en el dataset limpio", int((clean[TARGET] == "Not_recorded").sum())),
        ("Valores faltantes en model-ready", int(model_ready.isna().sum().sum())),
        ("Patient ID duplicados", int(model_ready[ID_COLUMN].duplicated().sum())),
        ("Filas completamente duplicadas", int(model_ready.duplicated().sum())),
        ("Clases de régimen", int(model_ready[TARGET].nunique())),
    ]
    return pd.DataFrame(rows, columns=["indicador", "valor"])


def predictor_profile_audit(df: pd.DataFrame) -> pd.DataFrame:
    """Audita duplicación y conflicto de etiquetas en los perfiles de entrada."""

    profile = (
        df.groupby(CORE_FEATURES, dropna=False)[TARGET]
        .agg(n_registros="size", n_etiquetas="nunique")
        .reset_index()
    )
    duplicated_rows = int(df[CORE_FEATURES].duplicated(keep=False).sum())
    repeated_profiles = int((profile["n_registros"] > 1).sum())
    conflicting_profiles = int((profile["n_etiquetas"] > 1).sum())
    rows = [
        ("Registros evaluados", len(df), "Unidad de análisis del model-ready"),
        ("Identificadores únicos", int(df[ID_COLUMN].nunique()), "Debe coincidir con los registros"),
        ("Perfiles predictores únicos", len(profile), "Combinaciones exactas de las nueve entradas"),
        ("Filas pertenecientes a perfiles repetidos", duplicated_rows, "Incluye todas las copias"),
        ("Perfiles repetidos", repeated_profiles, "Combinaciones exactas presentes más de una vez"),
        (
            "Perfiles repetidos con etiquetas en conflicto",
            conflicting_profiles,
            "Un valor mayor que cero indicaría ambigüedad determinista del target",
        ),
        (
            "Máximo de registros por perfil",
            int(profile["n_registros"].max()),
            "Concentración máxima de una combinación exacta",
        ),
    ]
    return pd.DataFrame(rows, columns=["indicador", "valor", "interpretacion"])


def missingness_table(clean: pd.DataFrame) -> pd.DataFrame:
    table = pd.DataFrame(
        {
            "variable": clean.columns,
            "n_faltantes": [int(clean[c].isna().sum()) for c in clean.columns],
            "pct_faltantes": [float(clean[c].isna().mean()) for c in clean.columns],
        }
    )
    return table.sort_values(["n_faltantes", "variable"], ascending=[False, True]).reset_index(drop=True)


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "age",
        "bmi",
        "tumor_size_cm",
        "dosage_mg_m2",
        "cycles_completed",
        "nausea_severity",
        "overall_survival_months",
    ]
    summary = df[columns].describe(percentiles=[0.25, 0.5, 0.75]).T.reset_index()
    summary = summary.rename(columns={"index": "variable"})
    return summary


def iqr_outlier_table(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for column in ["age", "bmi", "tumor_size_cm"]:
        q1 = float(df[column].quantile(0.25))
        q3 = float(df[column].quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        count = int(((df[column] < lower) | (df[column] > upper)).sum())
        rows.append(
            {
                "variable": column,
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "limite_inferior": lower,
                "limite_superior": upper,
                "n_fuera_iqr": count,
                "decision": "Conservar; revisar con conocimiento clínico antes de excluir.",
            }
        )
    return pd.DataFrame(rows)


def clinical_consistency_table(df: pd.DataFrame) -> pd.DataFrame:
    checks = [
        (
            "Estadio IV sin metástasis registrada",
            (df["tumor_stage"] == "IV") & (df["metastasis_status"] == "No"),
            "Revisar semántica y procedencia; no corregir automáticamente.",
        ),
        (
            "Estadio I con metástasis registrada",
            (df["tumor_stage"] == "I") & (df["metastasis_status"] == "Yes"),
            "Combinación clínicamente atípica; requiere validación de dominio.",
        ),
        (
            "Respuesta favorable y progresión simultáneas",
            (df["response_favorable"] == 1) & (df["progressive_disease"] == 1),
            "Debe ser cero por definición de variables derivadas.",
        ),
    ]
    return pd.DataFrame(
        [
            {
                "control": name,
                "n_registros": int(mask.sum()),
                "pct_registros": float(mask.mean()),
                "interpretacion": note,
            }
            for name, mask, note in checks
        ]
    )


def add_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["flag_stage_iv_no_metastasis"] = (
        (result["tumor_stage"] == "IV") & (result["metastasis_status"] == "No")
    ).astype(int)
    result["flag_stage_i_metastasis"] = (
        (result["tumor_stage"] == "I") & (result["metastasis_status"] == "Yes")
    ).astype(int)
    return result


def build_professor_sample(df: pd.DataFrame, n_per_class: int = 250) -> pd.DataFrame:
    sample = (
        add_quality_flags(df)
        .groupby(TARGET, group_keys=False)
        .sample(n=n_per_class, random_state=SEED)
        .sort_values([TARGET, ID_COLUMN])
        .reset_index(drop=True)
    )
    return sample


def leakage_audit_table(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for column in df.columns:
        if column == ID_COLUMN:
            role, decision = "Identificador", "Excluir del modelado"
        elif column == TARGET:
            role, decision = "Variable objetivo", "Usar únicamente como y"
        elif column in CORE_FEATURES:
            role, decision = "Pretratamiento", "Incluir en el modelo principal"
        elif column in DERIVED_REDUNDANT_COLUMNS:
            role, decision = "Derivada de pretratamiento", "Excluir del modelo principal por redundancia"
        elif column in POST_TREATMENT_COLUMNS:
            role, decision = "Posterior al tratamiento / desenlace", "Excluir: riesgo de leakage temporal"
        else:
            role, decision = "Control de calidad", "Conservar para auditoría; excluir del modelo"
        rows.append({"variable": column, "rol_temporal": role, "decision": decision})
    return pd.DataFrame(rows)


def cramers_v_with_p_value(x: pd.Series, y: pd.Series) -> tuple[float, float]:
    contingency = pd.crosstab(x, y)
    chi2, p_value, _, _ = chi2_contingency(contingency)
    n = contingency.to_numpy().sum()
    r, k = contingency.shape
    if n <= 1:
        return 0.0, float(p_value)
    phi2 = chi2 / n
    phi2_corrected = max(0.0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    r_corrected = r - ((r - 1) ** 2) / (n - 1)
    k_corrected = k - ((k - 1) ** 2) / (n - 1)
    denominator = min(k_corrected - 1, r_corrected - 1)
    value = np.sqrt(phi2_corrected / denominator) if denominator > 0 else 0.0
    return float(value), float(p_value)


def _benjamini_hochberg(p_values: list[float]) -> np.ndarray:
    """Ajusta una familia de p-valores controlando FDR con Benjamini-Hochberg."""

    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values)
    ranked = values[order]
    adjusted_ranked = ranked * len(values) / np.arange(1, len(values) + 1)
    adjusted_ranked = np.minimum.accumulate(adjusted_ranked[::-1])[::-1]
    adjusted = np.empty_like(adjusted_ranked)
    adjusted[order] = np.clip(adjusted_ranked, 0.0, 1.0)
    return adjusted


def target_associations(df: pd.DataFrame) -> pd.DataFrame:
    variables = [
        "sex",
        "smoking_status",
        "cancer_type",
        "genetic_mutation",
        "tumor_stage",
        "metastasis_status",
        "age_group",
        "bmi_category",
        "clinical_risk_group",
        "frailty_risk_pre",
    ]
    rows = []
    for variable in variables:
        value, p_value = cramers_v_with_p_value(df[variable], df[TARGET])
        rows.append(
            {
                "variable": variable,
                "cramers_v_corregido": value,
                "p_value_chi2": p_value,
                "interpretacion": "Asociación despreciable" if value < 0.10 else "Asociación a revisar",
            }
        )
    result = pd.DataFrame(rows)
    result["p_value_fdr_bh"] = _benjamini_hochberg(result["p_value_chi2"].tolist())
    result["significativo_fdr_005"] = result["p_value_fdr_bh"] < 0.05
    return result.sort_values("cramers_v_corregido", ascending=False).reset_index(drop=True)


def numeric_target_associations(df: pd.DataFrame) -> pd.DataFrame:
    """Cuantifica efecto y contraste no paramétrico para predictores numéricos."""

    rows = []
    for variable in ["age", "bmi", "tumor_size_cm"]:
        grand_mean = float(df[variable].mean())
        ss_total = float(((df[variable] - grand_mean) ** 2).sum())
        ss_between = 0.0
        groups = []
        for _, group in df.groupby(TARGET):
            values = group[variable].dropna().to_numpy(dtype=float)
            groups.append(values)
            ss_between += len(values) * (float(values.mean()) - grand_mean) ** 2
        eta_squared = ss_between / ss_total if ss_total else 0.0
        _, p_value = kruskal(*groups)
        rows.append(
            {
                "variable": variable,
                "eta_cuadrado": float(eta_squared),
                "p_value_kruskal": float(p_value),
                "interpretacion": (
                    "Efecto despreciable" if eta_squared < 0.01 else "Efecto a revisar"
                ),
            }
        )
    result = pd.DataFrame(rows)
    result["p_value_fdr_bh"] = _benjamini_hochberg(result["p_value_kruskal"].tolist())
    result["significativo_fdr_005"] = result["p_value_fdr_bh"] < 0.05
    return result.sort_values("eta_cuadrado", ascending=False).reset_index(drop=True)


def target_distribution(df: pd.DataFrame) -> pd.DataFrame:
    counts = df[TARGET].value_counts().rename_axis(TARGET).reset_index(name="n")
    counts["proporcion"] = counts["n"] / counts["n"].sum()
    return counts


def descriptive_outcomes_by_regimen(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(TARGET)
        .agg(
            n=(ID_COLUMN, "size"),
            response_favorable_rate=("response_favorable", "mean"),
            progressive_disease_rate=("progressive_disease", "mean"),
            severe_toxicity_rate=("severe_toxicity_observed", "mean"),
            survival_months_mean=("overall_survival_months", "mean"),
            survival_months_median=("overall_survival_months", "median"),
        )
        .reset_index()
    )
