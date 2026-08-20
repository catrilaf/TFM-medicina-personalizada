"""Alinea la memoria final con el diagnóstico solicitado en el acta.

La operación es deliberadamente mínima: actualiza el título visible de la
subsección 6.14 tanto en el cuerpo como en el índice estático y añade una frase
de enlace al primer párrafo. No altera tablas, figuras, cifras ni referencias.
"""

from __future__ import annotations

import argparse
import os
import tempfile
import zipfile
from pathlib import Path

OLD_HEADING = "6.14. Prueba de aleatorización, curva de aprendizaje y skill"
NEW_HEADING = "6.14. Diagnóstico del proceso generador de datos"
OLD_OPENING = (
    "Para comprobar si el rendimiento obtenido por el modelo era realmente "
    "superior al azar, se realizó una prueba de aleatorización sobre el conjunto "
    "holdout."
)
NEW_OPENING = (
    "El diagnóstico del proceso generador de datos integra la prueba de "
    "aleatorización, la curva de aprendizaje y el skill probabilístico. "
    + OLD_OPENING
)


def update_docx(path: Path) -> None:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    with zipfile.ZipFile(path, "r") as source:
        document_xml = source.read("word/document.xml")
        old_heading = OLD_HEADING.encode("utf-8")
        new_heading = NEW_HEADING.encode("utf-8")
        old_opening = OLD_OPENING.encode("utf-8")
        new_opening = NEW_OPENING.encode("utf-8")

        heading_count = document_xml.count(old_heading)
        if heading_count not in (0, 2):
            raise RuntimeError(
                f"Se esperaban dos apariciones del título anterior y se hallaron "
                f"{heading_count}."
            )
        if heading_count == 2:
            document_xml = document_xml.replace(old_heading, new_heading)
        elif document_xml.count(new_heading) != 2:
            raise RuntimeError("La memoria no contiene el título esperado.")

        if old_opening in document_xml:
            document_xml = document_xml.replace(old_opening, new_opening, 1)
        elif new_opening not in document_xml:
            raise RuntimeError("No se encontró el párrafo inicial de la sección 6.14.")

        fd, tmp_name = tempfile.mkstemp(suffix=".docx", dir=path.parent)
        os.close(fd)
        tmp_path = Path(tmp_name)
        try:
            with zipfile.ZipFile(tmp_path, "w") as target:
                for item in source.infolist():
                    payload = (
                        document_xml
                        if item.filename == "word/document.xml"
                        else source.read(item.filename)
                    )
                    target.writestr(item, payload)
            os.replace(tmp_path, path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "docx",
        nargs="?",
        default=(
            "memoria/TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.docx"
        ),
        type=Path,
    )
    args = parser.parse_args()
    update_docx(args.docx)
    print(f"Memoria actualizada: {args.docx}")


if __name__ == "__main__":
    main()
