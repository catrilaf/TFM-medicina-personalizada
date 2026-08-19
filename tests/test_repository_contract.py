"""Contratos de publicación y coherencia entre artefactos."""

import json
from pathlib import Path

import nbformat

from tools.build_manifest import build_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_publication_artifacts_exist():
    required = [
        ROOT / "README.md",
        ROOT / "docs" / "INDICE_AUDITORIA.md",
        ROOT / "docs" / "REVISION_COMISION.md",
        ROOT / "docs" / "DESPLIEGUE_STREAMLIT.md",
        ROOT / "memoria" / "TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.docx",
        ROOT / "memoria" / "TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.pdf",
    ]
    assert all(path.is_file() for path in required)


def test_generated_artifact_counts_and_decision(tmp_path):
    assert len(list((ROOT / "outputs" / "tables").glob("*.csv"))) == 35
    assert len(list((ROOT / "outputs" / "figures").glob("*.png"))) == 18
    summary = json.loads(
        (ROOT / "outputs" / "analysis_summary.json").read_text(encoding="utf-8")
    )
    metadata = json.loads(
        (ROOT / "outputs" / "models" / "model_metadata.json").read_text(
            encoding="utf-8"
        )
    )
    assert summary["selected_model"] == metadata["selected_model"] == "Random Forest"
    assert summary["evidence_conclusion"] == metadata["evidence_conclusion"]
    assert summary["abstention_rate_holdout"] == 1.0
    assert metadata["signal_gate_passed"] is False
    assert metadata["clinical_go"] is False

    (tmp_path / "entregable.txt").write_text("contenido", encoding="utf-8")
    (tmp_path / ".coverage").write_text("cache", encoding="utf-8")
    cache_dir = tmp_path / ".ruff_cache"
    cache_dir.mkdir()
    (cache_dir / "cache.bin").write_bytes(b"cache")
    assert build_manifest(tmp_path) == 1
    manifest = (tmp_path / "MANIFEST_SHA256.csv").read_text(encoding="utf-8")
    assert "entregable.txt" in manifest
    assert ".coverage" not in manifest
    assert ".ruff_cache" not in manifest


def test_notebook_uses_portable_kernel():
    notebook = nbformat.read(
        ROOT / "notebooks" / "01_estudio_completo_oncologia.ipynb",
        as_version=4,
    )
    assert notebook.metadata.kernelspec.name == "python3"
