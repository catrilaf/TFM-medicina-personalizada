"""Reconstrucción determinista de los datasets derivados desde el CSV bruto.

Este módulo conserva las transformaciones del script de limpieza recibido y
las expone como funciones reutilizables para que ``python run_all.py`` parta
del archivo original incluido en ``data/raw``.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd

RAW_SHA256 = "7809afd664be251e882ce02d4c843fd26a7765c0a921192cadfe11c37b2db6f2"
CLEAN_SHA256 = "a911f348979e9b7b54f691a2459dfa59bb5274d54585dd5a52cbc04877bb77b3"
MODEL_READY_SHA256 = (
    "3d4c3c478b4e0720cfae9ab13ca5715c8d5baf3a064c0bc98125a9661e065d08"
)


def sha256_file(path: Path) -> str:
    """Calcula SHA-256 sin cargar el archivo completo en memoria."""

    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def snake(value: object) -> str:
    """Normaliza encabezados a ``snake_case`` reproducible."""

    text = str(value).strip().replace("²", "2")
    text = re.sub(r"[\(\)/]+", " ", text)
    text = text.replace("%", "pct")
    text = re.sub(r"[^0-9A-Za-z]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_").lower()


def age_group(age: float) -> str:
    if age < 50:
        return "<50"
    if age < 65:
        return "50-64"
    if age < 75:
        return "65-74"
    return ">=75"


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Bajo_peso"
    if bmi < 25:
        return "Normopeso"
    if bmi < 30:
        return "Sobrepeso"
    return "Obesidad"


def clinical_risk(row: pd.Series) -> str:
    if row["tumor_stage"] == "IV" or row["metastasis_status"] == "Yes":
        return "Alto"
    if row["tumor_stage"] == "III" or row["tumor_size_cm"] >= 5:
        return "Intermedio"
    return "Bajo"


def frailty_risk(row: pd.Series) -> str:
    if row["age"] >= 75 or row["bmi"] < 20:
        return "Alto"
    if row["age"] >= 65 or row["bmi"] >= 30:
        return "Intermedio"
    return "Bajo"


def build_datasets(raw_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Devuelve dataset limpio, model-ready y resumen de limpieza."""

    if not raw_path.exists():
        raise FileNotFoundError(f"No se encontró el CSV bruto: {raw_path}")
    observed_hash = sha256_file(raw_path)
    if observed_hash != RAW_SHA256:
        raise ValueError(
            "El CSV bruto no coincide con la versión 1 evaluada. "
            f"SHA-256 observado: {observed_hash}"
        )

    raw = pd.read_csv(raw_path)
    original_shape = raw.shape

    clean = raw.copy()
    clean.columns = [snake(column) for column in clean.columns]
    for column in clean.select_dtypes(include="object").columns:
        clean[column] = clean[column].astype("string").str.strip()

    clean["genetic_mutation"] = clean["genetic_mutation"].fillna("Not_reported")
    clean["chemotherapy_regimen_missing"] = (
        clean["chemotherapy_regimen"].isna().astype(int)
    )
    clean["chemotherapy_regimen"] = clean["chemotherapy_regimen"].fillna(
        "Not_recorded"
    )

    clean["bmi"] = clean["bmi"].round(1)
    clean["tumor_size_cm"] = clean["tumor_size"].round(1)
    clean = clean.drop(columns=["tumor_size"])
    clean["dosage_mg_m2"] = clean["dosage_mg_m2"].round(1)

    stage_map = {"I": 1, "II": 2, "III": 3, "IV": 4}
    clean["tumor_stage_numeric"] = clean["tumor_stage"].map(stage_map).astype("Int64")
    clean["metastasis_binary"] = (
        clean["metastasis_status"].map({"Yes": 1, "No": 0}).astype("Int64")
    )
    clean["neutropenia_binary"] = (
        clean["neutropenia"].map({"Yes": 1, "No": 0}).astype("Int64")
    )

    clean["age_group"] = clean["age"].apply(age_group)
    clean["bmi_category"] = clean["bmi"].apply(bmi_category)
    clean["clinical_risk_group"] = clean.apply(clinical_risk, axis=1)
    clean["frailty_risk_pre"] = clean.apply(frailty_risk, axis=1)

    clean["response_favorable"] = (
        clean["tumor_response"].isin(["Complete", "Partial"]).astype(int)
    )
    clean["progressive_disease"] = (
        clean["tumor_response"] == "Progressive"
    ).astype(int)
    clean["severe_toxicity_observed"] = (
        (clean["neutropenia"] == "Yes") | (clean["nausea_severity"] >= 4)
    ).astype(int)
    clean["survival_12m"] = (clean["overall_survival_months"] >= 12).astype(int)
    clean["survival_24m"] = (clean["overall_survival_months"] >= 24).astype(int)
    clean["record_quality_for_recommender"] = np.where(
        clean["chemotherapy_regimen"] == "Not_recorded",
        "missing_target_regimen",
        "complete_for_recommender",
    )

    ordered_columns = [
        "patient_id",
        "age",
        "age_group",
        "sex",
        "bmi",
        "bmi_category",
        "smoking_status",
        "cancer_type",
        "genetic_mutation",
        "tumor_stage",
        "tumor_stage_numeric",
        "tumor_size_cm",
        "metastasis_status",
        "metastasis_binary",
        "clinical_risk_group",
        "frailty_risk_pre",
        "chemotherapy_regimen",
        "chemotherapy_regimen_missing",
        "dosage_mg_m2",
        "cycles_completed",
        "nausea_severity",
        "neutropenia",
        "neutropenia_binary",
        "severe_toxicity_observed",
        "tumor_response",
        "response_favorable",
        "progressive_disease",
        "overall_survival_months",
        "survival_12m",
        "survival_24m",
        "record_quality_for_recommender",
    ]
    clean = clean[ordered_columns]

    model_ready = clean.loc[
        clean["chemotherapy_regimen"] != "Not_recorded"
    ].copy()
    predictor_columns = [
        "patient_id",
        "age",
        "age_group",
        "sex",
        "bmi",
        "bmi_category",
        "smoking_status",
        "cancer_type",
        "genetic_mutation",
        "tumor_stage",
        "tumor_stage_numeric",
        "tumor_size_cm",
        "metastasis_status",
        "metastasis_binary",
        "clinical_risk_group",
        "frailty_risk_pre",
        "chemotherapy_regimen",
    ]
    outcome_columns = [
        "dosage_mg_m2",
        "cycles_completed",
        "nausea_severity",
        "neutropenia",
        "neutropenia_binary",
        "severe_toxicity_observed",
        "tumor_response",
        "response_favorable",
        "progressive_disease",
        "overall_survival_months",
        "survival_12m",
        "survival_24m",
    ]
    model_ready = model_ready[predictor_columns + outcome_columns]

    summary = pd.DataFrame(
        [
            {"indicador": "Registros originales", "valor": original_shape[0]},
            {"indicador": "Columnas originales", "valor": original_shape[1]},
            {"indicador": "Registros dataset limpio", "valor": clean.shape[0]},
            {"indicador": "Columnas dataset limpio", "valor": clean.shape[1]},
            {
                "indicador": "Patient_ID duplicados",
                "valor": int(raw["Patient_ID"].duplicated().sum()),
            },
            {
                "indicador": "Genetic_Mutation faltante imputado como Not_reported",
                "valor": int(raw["Genetic_Mutation"].isna().sum()),
            },
            {
                "indicador": "Chemotherapy_Regimen faltante en original",
                "valor": int(raw["Chemotherapy_Regimen"].isna().sum()),
            },
            {
                "indicador": "Registros model-ready con régimen conocido",
                "valor": model_ready.shape[0],
            },
        ]
    )
    return clean, model_ready, summary


def rebuild_from_raw(root: Path) -> dict[str, object]:
    """Regenera y verifica los CSV derivados dentro del paquete."""

    data_dir = root / "data"
    raw_path = data_dir / "raw" / "chemotherapy_patient_data.csv"
    clean_path = data_dir / "chemotherapy_patient_data_clean_tfm.csv"
    model_ready_path = (
        data_dir / "chemotherapy_patient_data_model_ready_recommender_tfm.csv"
    )
    summary_path = data_dir / "resumen_limpieza_recomendador_oncologia.csv"

    clean, model_ready, summary = build_datasets(raw_path)
    clean.to_csv(clean_path, index=False)
    model_ready.to_csv(model_ready_path, index=False)
    summary.to_csv(summary_path, index=False)

    hashes = {
        "raw_sha256": sha256_file(raw_path),
        "clean_sha256": sha256_file(clean_path),
        "model_ready_sha256": sha256_file(model_ready_path),
    }
    if hashes["clean_sha256"] != CLEAN_SHA256:
        raise RuntimeError(
            "El dataset limpio no coincide con la referencia reproducida. "
            f"SHA-256: {hashes['clean_sha256']}"
        )
    if hashes["model_ready_sha256"] != MODEL_READY_SHA256:
        raise RuntimeError(
            "El model-ready no coincide con la referencia reproducida. "
            f"SHA-256: {hashes['model_ready_sha256']}"
        )
    return {
        "rows_raw": len(clean),
        "rows_model_ready": len(model_ready),
        **hashes,
    }
