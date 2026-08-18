"""Configuración central del estudio.

Todas las decisiones que afectan a la reproducibilidad se mantienen en este
archivo: semilla, variable objetivo, predictores y variables excluidas.
"""

from pathlib import Path

SEED = 42
TEST_SIZE = 0.25
TARGET = "chemotherapy_regimen"
ID_COLUMN = "patient_id"

# Predictores disponibles antes de seleccionar un tratamiento. Se evita usar
# duplicados derivados (por ejemplo, tumor_stage y tumor_stage_numeric a la vez)
# para mantener parsimonia e interpretación.
CORE_FEATURES = [
    "age",
    "sex",
    "bmi",
    "smoking_status",
    "cancer_type",
    "genetic_mutation",
    "tumor_stage",
    "tumor_size_cm",
    "metastasis_status",
]

NUMERIC_FEATURES = ["age", "bmi", "tumor_size_cm"]
CATEGORICAL_FEATURES = [c for c in CORE_FEATURES if c not in NUMERIC_FEATURES]

# Variables posteriores a la decisión terapéutica. Incorporarlas al modelo
# principal produciría data leakage y una evaluación optimista.
POST_TREATMENT_COLUMNS = [
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

DERIVED_REDUNDANT_COLUMNS = [
    "age_group",
    "bmi_category",
    "tumor_stage_numeric",
    "metastasis_binary",
    "clinical_risk_group",
    "frailty_risk_pre",
]

MODEL_NAMES = [
    "Dummy mayoría",
    "Dummy estratificado",
    "Regresión logística",
    "Árbol CART",
    "Random Forest",
    "Extra Trees",
]


def project_paths(project_root: Path) -> dict[str, Path]:
    root = Path(project_root).resolve()
    return {
        "root": root,
        "data": root / "data",
        "outputs": root / "outputs",
        "figures": root / "outputs" / "figures",
        "tables": root / "outputs" / "tables",
        "models": root / "outputs" / "models",
        "reports": root / "reports",
    }
