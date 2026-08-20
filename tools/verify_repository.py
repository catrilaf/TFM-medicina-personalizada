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
    "docs/ANEXOS_Y_CODIGO.md",
    "memoria/TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.docx",
    "memoria/TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.pdf",
]

ANNEX_SCRIPT_MAP = {
    "A": ["src/modeling.py", "src/metrics.py"],
    "B": ["src/app_logic.py", "src/robustness.py"],
    "C": ["run_all.py", "tools/verify_repository.py"],
    "D": ["tools/rebuild_datasets_from_raw.py", "src/preprocessing.py"],
    "E": ["src/preprocessing.py", "src/robustness.py", "src/app_logic.py"],
    "F": ["src/preprocessing.py", "tools/rebuild_datasets_from_raw.py"],
    "G": [
        "src/config.py",
        "tests/test_repository_contract.py",
        "tests/test_smoke.py",
    ],
    "H": ["src/modeling.py", "src/metrics.py", "src/robustness.py"],
    "I": ["app.py", "src/app_logic.py", "tests/test_streamlit_app.py"],
    "J": ["tools/build_manifest.py", "tools/verify_repository.py"],
    "K": ["tools/verify_repository.py", ".github/workflows/ci.yml"],
    "L": ["run_all.py", "src/analysis.py", "src/figures.py"],
}

EXPECTED_TEXT = {
    "selected_model": "Random Forest",
    "evidence_conclusion": (
        "No se demuestra señal predictiva útil: el modelo no supera los "
        "criterios preespecificados frente al azar."
    ),
}

EXPECTED_CLOSE = {
    "cv_f1_macro_mean": 0.252054,
    "dummy_stratified_cv_f1_macro": 0.252499,
    "holdout_f1_macro": 0.249598,
    "holdout_balanced_accuracy": 0.249909,
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
    for key, expected in EXPECTED_TEXT.items():
        actual = summary.get(key)
        if actual != expected:
            errors.append(f"Valor incoherente {key}: {actual!r} != {expected!r}")
    for key, expected in EXPECTED_CLOSE.items():
        actual = summary.get(key)
        if actual is None or not math.isclose(float(actual), expected, abs_tol=0.005):
            errors.append(
                f"Métrica fuera de tolerancia {key}: {actual!r}; referencia {expected!r}"
            )

    p_value = float(summary.get("label_randomization_p_value", -1))
    if not 0.05 <= p_value <= 1.0:
        errors.append(f"La aleatorización contradice el NO-GO: p={p_value!r}")
    if float(summary.get("abstention_rate_holdout", -1)) != 1.0:
        errors.append("La tasa de abstención del holdout debe ser 1,0")
    metadata_path = ROOT / "outputs" / "models" / "model_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("signal_gate_passed") is not False:
        errors.append("El gate de señal debe conservar la decisión NO-GO")
    if metadata.get("clinical_go") is not False:
        errors.append("clinical_go debe ser false en un prototipo no validado")
    delta = float(summary.get("delta_f1_vs_dummy", 1.0))
    if delta >= 0.01:
        errors.append(f"La mejora frente al Dummy supera el margen NO-GO: {delta!r}")


def check_annex_links(errors: list[str]) -> None:
    index_path = ROOT / "docs" / "ANEXOS_Y_CODIGO.md"
    if not index_path.is_file():
        return
    content = index_path.read_text(encoding="utf-8")
    for annex, scripts in ANNEX_SCRIPT_MAP.items():
        if f"Anexo {annex}" not in content:
            errors.append(f"Falta Anexo {annex} en docs/ANEXOS_Y_CODIGO.md")
        for script in scripts:
            if not (ROOT / script).is_file():
                errors.append(f"Falta script enlazado por Anexo {annex}: {script}")
            expected_link = f"../{script}"
            if expected_link not in content:
                errors.append(
                    f"Falta enlace directo de Anexo {annex} al script {script}"
                )


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
    check_annex_links(errors)
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
    print(f"- Anexos con enlace directo a scripts: {len(ANNEX_SCRIPT_MAP)}")
    print("- Cifras principales dentro de tolerancia y decisión NO-GO conservada")


if __name__ == "__main__":
    main()
