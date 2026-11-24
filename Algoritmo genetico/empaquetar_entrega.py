"""Arma entrega/Algoritmo_genetico_Duarte.zip con la aplicación ejecutable en la
raíz, su código, los experimentos y la fuente del informe. El informe en PDF se
sube aparte y queda junto al ZIP en la carpeta entrega.

Uso, desde esta carpeta: python empaquetar_entrega.py RUTA_DEL_EJECUTABLE
(el AlgoritmoGenetico.exe que genera PyInstaller con --onefile)
"""

import shutil
import sys
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ZIP = AQUI / "entrega" / "Algoritmo_genetico_Duarte.zip"
OMITIR = {".pyc", ".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".synctex.gz"}


def archivos(ejecutable):
    yield ejecutable, "AlgoritmoGenetico.exe"
    yield AQUI / "README.md", "README.md"
    for carpeta in ("ag_app", "experimentos", "informe"):
        for ruta in sorted((AQUI / carpeta).rglob("*")):
            if ruta.is_file() and "__pycache__" not in ruta.parts and ruta.suffix not in OMITIR \
                    and ruta.name not in ("main.pdf", "AG.pdf"):
                yield ruta, ruta.relative_to(AQUI).as_posix()


def main():
    if len(sys.argv) != 2 or Path(sys.argv[1]).name != "AlgoritmoGenetico.exe" or not Path(sys.argv[1]).is_file():
        sys.exit("Indique el AlgoritmoGenetico.exe generado con PyInstaller (ver ag_app/README.md).")
    ZIP.parent.mkdir(exist_ok=True)
    informe = next(r for r in (AQUI / "informe" / "main.pdf", AQUI / "informe" / "AG.pdf") if r.is_file())
    shutil.copy2(informe, ZIP.parent / "Informe algoritmo genetico Duarte.pdf")
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for origen, destino in archivos(Path(sys.argv[1])):
            z.write(origen, destino)
    with zipfile.ZipFile(ZIP) as z:
        print(f"{ZIP.name}, {ZIP.stat().st_size / 1e6:.1f} MB, {len(z.namelist())} archivos")


if __name__ == "__main__":
    main()
