"""CLI para reconstruir los datasets derivados desde el archivo Kaggle v1."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.preprocessing import rebuild_from_raw

if __name__ == "__main__":
    result = rebuild_from_raw(ROOT)
    print(json.dumps(result, indent=2, ensure_ascii=False))
