"""Auditoría autocontenida de los artefactos entregables.

Comprueba estructura, inventario SHA-256 y coherencia de las cifras principales.
No reentrena el modelo; para ello debe ejecutarse ``python run_all.py``.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "app.py",
    "run_all.py",
    "requirements.txt",
    "MODEL_CARD.md",
    "data/raw/chemotherapy_patient_data.csv",
    "outputs/analysis_summary.json",
    "outputs/models/model_metadata.json",
    "outputs/models/modelo_experimental_full.joblib",
    "notebooks/01_estudio_completo_oncologia.ipynb",
    "reports/Estudio_Completo_Oncologia.html",
    "memoria/TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.docx",
    "memoria/TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.pdf",
]

EXPECTED = {
    "selected_model": "Random Forest",
    "cv_f1_macro_mean": 0.252054,
    "dummy_stratified_cv_f1_macro": 0.252499,
    "holdout_f1_macro": 0.249598,
    "holdout_balanced_accuracy": 0.249909,
    "label_randomization_p_value": 0.499100,
    "abstention_rate_holdout": 1.0,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_manifest(errors: list[str]) -> int:
    manifest = ROOT / "MANIFEST_SHA256.csv"
    if not manifest.exists():
        errors.append("Falta MANIFEST_SHA256.csv")
        return 0

    checked = 0
    with manifest.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            path = ROOT / row["archivo"]
            if not path.is_file():
                errors.append(f"Falta archivo inventariado: {row['archivo']}")
                continue
            if path.stat().st_size != int(row["bytes"]):
                errors.append(f"Tamaño distinto: {row['archivo']}")
            if sha256(path) != row["sha256"]:
                errors.append(f"SHA-256 distinto: {row['archivo']}")
            checked += 1
    return checked


def check_metrics(errors: list[str]) -> None:
    summary_path = ROOT / "outputs" / "analysis_summary.json"
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    for key, expected in EXPECTED.items():
        actual = summary.get(key)
        if isinstance(expected, float):
            if actual is None or not math.isclose(float(actual), expected, abs_tol=5e-7):
                errors.append(f"Métrica incoherente {key}: {actual!r} != {expected!r}")
        elif actual != expected:
            errors.append(f"Valor incoherente {key}: {actual!r} != {expected!r}")


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).is_file():
            errors.append(f"Falta archivo requerido: {relative}")

    table_count = len(list((ROOT / "outputs" / "tables").glob("*.csv")))
    figure_count = len(list((ROOT / "outputs" / "figures").glob("*.png")))
    if table_count != 35:
        errors.append(f"Se esperaban 35 tablas y se encontraron {table_count}")
    if figure_count != 18:
        errors.append(f"Se esperaban 18 figuras y se encontraron {figure_count}")

    check_metrics(errors)
    checked = check_manifest(errors)

    if errors:
        print("AUDITORÍA: ERROR")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("AUDITORÍA: CORRECTA")
    print(f"- Archivos con SHA-256 comprobado: {checked}")
    print(f"- Tablas reproducibles: {table_count}")
    print(f"- Figuras reproducibles: {figure_count}")
    print("- Cifras principales coherentes con outputs/analysis_summary.json")


if __name__ == "__main__":
    main()
