"""Crea un inventario SHA-256 de los artefactos de la entrega."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "MANIFEST_SHA256.csv"
EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "qa",
    "tmp",
    ".DS_Store",
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def build_manifest(root: Path = ROOT) -> int:
    """Registra el estado íntegro del paquete y devuelve el número de archivos."""

    root = Path(root).resolve()
    output = root / "MANIFEST_SHA256.csv"
    files = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path != output
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
    ]

    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["archivo", "bytes", "sha256"])
        for path in sorted(files):
            writer.writerow(
                [path.relative_to(root).as_posix(), path.stat().st_size, digest(path)]
            )

    print(f"{output}: {len(files)} archivos")
    return len(files)


if __name__ == "__main__":
    build_manifest()
