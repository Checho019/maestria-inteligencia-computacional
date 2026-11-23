"""Arma entrega/Algoritmo_genetico_Duarte.zip con el informe, la aplicación
ejecutable, su código, los experimentos y la fuente del informe.

Uso, desde esta carpeta: python empaquetar_entrega.py CARPETA_DEL_EJECUTABLE
(la carpeta AlgoritmoGenetico que genera PyInstaller con --onedir)
"""

import sys
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ZIP = AQUI / "entrega" / "Algoritmo_genetico_Duarte.zip"
OMITIR = {".pyc", ".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".synctex.gz"}


def archivos(ejecutable):
    yield AQUI / "informe" / "main.pdf", "Informe algoritmo genetico Duarte.pdf"
    yield AQUI / "README.md", "README.md"
    for ruta in sorted(ejecutable.rglob("*")):
        if ruta.is_file():
            yield ruta, "AlgoritmoGenetico/" + ruta.relative_to(ejecutable).as_posix()
    for carpeta in ("ag_app", "experimentos", "informe"):
        for ruta in sorted((AQUI / carpeta).rglob("*")):
            if ruta.is_file() and "__pycache__" not in ruta.parts and ruta.suffix not in OMITIR \
                    and ruta.name != "main.pdf":
                yield ruta, ruta.relative_to(AQUI).as_posix()


def main():
    if len(sys.argv) != 2 or not (Path(sys.argv[1]) / "AlgoritmoGenetico.exe").is_file():
        sys.exit("Indique la carpeta AlgoritmoGenetico generada con PyInstaller (ver ag_app/README.md).")
    ZIP.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for origen, destino in archivos(Path(sys.argv[1])):
            z.write(origen, destino)
    with zipfile.ZipFile(ZIP) as z:
        print(f"{ZIP.name}, {ZIP.stat().st_size / 1e6:.1f} MB, {len(z.namelist())} archivos")


if __name__ == "__main__":
    main()
