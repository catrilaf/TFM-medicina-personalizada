"""Punto de entrada para reproducir todo el estudio.

Uso:
    python run_all.py
"""

from __future__ import annotations

import json
from pathlib import Path

from src import run_analysis
from src.preprocessing import rebuild_from_raw
from tools.build_manifest import build_manifest


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    preprocessing = rebuild_from_raw(root)
    result = run_analysis(root)
    result["preprocessing"] = preprocessing
    result["manifest_files"] = build_manifest(root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
