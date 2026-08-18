from pathlib import Path
import hashlib

import joblib
import numpy as np
import pandas as pd
import pytest

from src.app_logic import build_input_frame, clinical_consistency_alerts, uncertainty_indicators
from src.config import CORE_FEATURES, TARGET
from src.data import load_datasets, numeric_target_associations, predictor_profile_audit
from src.robustness import (
    holdout_label_randomization_test,
    probabilistic_skill_table,
    selective_performance_table,
    top_label_calibration_table,
)
from src.preprocessing import (
    CLEAN_SHA256,
    MODEL_READY_SHA256,
    RAW_SHA256,
)


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def test_dataset_contract():
    clean, model_ready = load_datasets(ROOT / "data")
    assert len(clean) == 52321
    assert len(model_ready) == 49765
    assert model_ready["patient_id"].is_unique
    assert model_ready[TARGET].nunique() == 4
    assert set(CORE_FEATURES).issubset(model_ready.columns)


def test_dataset_provenance_hashes():
    assert (
        _sha256(ROOT / "data" / "raw" / "chemotherapy_patient_data.csv")
        == RAW_SHA256
    )
    assert (
        _sha256(ROOT / "data" / "chemotherapy_patient_data_clean_tfm.csv")
        == CLEAN_SHA256
    )
    assert (
        _sha256(
            ROOT
            / "data"
            / "chemotherapy_patient_data_model_ready_recommender_tfm.csv"
        )
        == MODEL_READY_SHA256
    )


def test_model_smoke_prediction():
    model_path = ROOT / "outputs" / "models" / "modelo_experimental_full.joblib"
    assert model_path.exists(), "Ejecute primero python run_all.py"
    model = joblib.load(model_path)
    df = pd.read_csv(ROOT / "data" / "chemotherapy_patient_data_model_ready_recommender_tfm.csv")
    probabilities = model.predict_proba(df[CORE_FEATURES].head(3))
    assert probabilities.shape == (3, 4)
    assert ((probabilities >= 0) & (probabilities <= 1)).all()
    assert (abs(probabilities.sum(axis=1) - 1) < 1e-8).all()


def test_app_logic_contract():
    values = {
        "age": 57,
        "sex": "Female",
        "bmi": 26.8,
        "smoking_status": "Never",
        "cancer_type": "Lung",
        "genetic_mutation": "EGFR",
        "tumor_stage": "I",
        "tumor_size_cm": 5.5,
        "metastasis_status": "Yes",
    }
    frame = build_input_frame(values)
    assert frame.columns.tolist() == CORE_FEATURES
    with pytest.raises(ValueError, match="Faltan variables requeridas"):
        build_input_frame({key: value for key, value in values.items() if key != "age"})
    indicators = uncertainty_indicators(np.array([0.24, 0.26, 0.25, 0.25]))
    assert indicators["confianza_maxima"] == 0.26
    assert 0.98 <= indicators["entropia_normalizada"] <= 1.0
    with pytest.raises(ValueError, match="deben sumar 1"):
        uncertainty_indicators(np.array([0.4, 0.4, 0.4, 0.4]))
    assert clinical_consistency_alerts("I", "Yes")


def test_robustness_tables():
    classes = np.array(["A", "B", "C", "D"])
    y_true = np.array(["A", "B", "C", "D"] * 5)
    probabilities = np.tile(np.array([0.28, 0.24, 0.24, 0.24]), (20, 1))
    y_pred = classes[probabilities.argmax(axis=1)]
    calibration, ece = top_label_calibration_table(y_true, probabilities, classes)
    selective = selective_performance_table(y_true, y_pred, probabilities)
    assert calibration["n"].sum() == len(y_true)
    assert 0 <= ece <= 1
    assert selective.loc[selective["umbral"] == 0.45, "cobertura"].iloc[0] == 0


def test_signal_and_integrity_audits():
    _, model_ready = load_datasets(ROOT / "data")
    integrity = predictor_profile_audit(model_ready)
    numeric = numeric_target_associations(model_ready)
    assert int(
        integrity.loc[
            integrity["indicador"] == "Perfiles repetidos con etiquetas en conflicto", "valor"
        ].iloc[0]
    ) == 0
    assert set(numeric["variable"]) == {"age", "bmi", "tumor_size_cm"}
    assert numeric["eta_cuadrado"].between(0, 1).all()


def test_randomization_and_probabilistic_baselines():
    classes = np.array(["A", "B", "C", "D"])
    y_true = np.array(["A", "B", "C", "D"] * 20)
    y_pred = np.array(["A", "B", "C", "D"] * 20)
    summary, distribution = holdout_label_randomization_test(
        y_true,
        y_pred,
        n_permutations=100,
    )
    probabilities = np.eye(4)[np.tile(np.arange(4), 20)] * 0.7 + 0.075
    skill = probabilistic_skill_table(
        pd.Series(y_true),
        y_true,
        probabilities,
        classes,
        "Modelo prueba",
    )
    assert len(distribution) == 100
    assert summary.iloc[0]["p_unilateral_superior"] < 0.05
    assert skill.loc[skill["modelo"] == "Modelo prueba", "brier_skill_vs_prevalencia"].iloc[0] > 0
