"""Reconstruye, ejecuta y exporta el estudio docente a HTML.

Uso:
    python tools/render_notebook.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "01_estudio_completo_oncologia.ipynb"
REPORT = ROOT / "reports" / "Estudio_Completo_Oncologia.html"
sys.path.insert(0, str(ROOT))

from tools.build_manifest import build_manifest


def main() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "build_notebook.py")],
        cwd=ROOT,
        check=True,
    )

    notebook = nbformat.read(NOTEBOOK, as_version=4)
    executor = ExecutePreprocessor(timeout=1_800, kernel_name="python3")
    executor.preprocess(notebook, {"metadata": {"path": str(ROOT)}})
    nbformat.write(notebook, NOTEBOOK)

    exporter = HTMLExporter()
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    body, _ = exporter.from_notebook_node(notebook)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(body, encoding="utf-8")
    build_manifest(ROOT)

    print(f"Notebook ejecutado: {NOTEBOOK}")
    print(f"Informe HTML: {REPORT}")


if __name__ == "__main__":
    main()
