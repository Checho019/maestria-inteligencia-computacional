"""
Convierte los informes en Markdown a Word (.docx).

Solo entiende el subconjunto de Markdown que usan los informes: encabezados,
parrafos, listas, tablas, citas, bloques de codigo, imagenes y negrita, cursiva
o codigo en linea. No pretende ser un conversor general.

Uso:  python codigo/md_a_docx.py                 (convierte los dos informes)
      python codigo/md_a_docx.py Informe_Ecoli   (convierte solo uno)
"""
import os
import re
import sys

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

BASE = os.path.dirname(os.path.abspath(__file__))
INFORMES = ["Revision_datos"]

# Los tecnicos van apaisados porque sus tablas tienen 5 y 6 columnas de texto
# largo, y en vertical quedan ilegibles.
APAISADOS = ("TECNICO_",)

ANCHO_MAX = Inches(6.3)


def mermaid_a_texto(lineas):
    """Mermaid no se renderiza en Word. Se convierte a texto plano legible."""
    fuera = []
    for ln in lineas:
        t = ln.strip()
        if not t or t.startswith(("flowchart", "graph", "end", "classDef", "class ", "style ")):
            continue
        t = t.replace("<br/>", " / ").replace("<br>", " / ")
        # subgraph P1["titulo"]  ->  [ titulo ]
        m = re.match(r'^subgraph\s+\w+\["?(.*?)"?\]$', t)
        if m:
            fuera.append("[ %s ]" % m.group(1))
            continue
        # NODO["texto"], NODO(("texto")), NODO[("texto")]
        m = re.match(r'^(\w+)\s*[\[\(]{1,2}"?(.*?)"?[\]\)]{1,2}$', t)
        if m:
            fuera.append("   %-6s %s" % (m.group(1) + ":", m.group(2)))
            continue
        fuera.append("   " + t)
    return fuera


def texto_con_formato(par, texto):
    """Escribe texto aplicando **negrita**, *cursiva* y `codigo`."""
    for trozo in re.split(r"(\*\*.+?\*\*|`[^`]+`|\*[^*]+?\*)", texto):
        if not trozo:
            continue
        if trozo.startswith("**") and trozo.endswith("**"):
            par.add_run(trozo[2:-2]).bold = True
        elif trozo.startswith("`") and trozo.endswith("`"):
            r = par.add_run(trozo[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(0xA0, 0x30, 0x30)
        elif trozo.startswith("*") and trozo.endswith("*") and len(trozo) > 2:
            par.add_run(trozo[1:-1]).italic = True
        else:
            par.add_run(trozo)


def limpiar_celda(t):
    t = t.strip()
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    return t


def convertir(nombre):
    MD = os.path.join(BASE, nombre + ".md")
    DOCX = os.path.join(BASE, nombre + ".docx")
    with open(MD, encoding="utf-8") as fh:
        lineas = fh.read().split("\n")

    # si el archivo abre con frontmatter YAML entre --- y ---, se descarta
    if lineas and lineas[0].strip() == "---":
        cierre = next((k for k in range(1, len(lineas))
                       if lineas[k].strip() == "---"), None)
        if cierre is not None:
            lineas = lineas[cierre + 1:]

    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)

    ancho_max = ANCHO_MAX
    if nombre.startswith(APAISADOS):
        sec = doc.sections[0]
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = sec.page_height, sec.page_width
        sec.left_margin = sec.right_margin = Inches(0.6)
        sec.top_margin = sec.bottom_margin = Inches(0.6)
        ancho_max = Inches(9.8)

    i = 0
    n_img = 0
    n_tab = 0
    while i < len(lineas):
        ln = lineas[i]
        s = ln.strip()

        # --- separador
        if s == "---":
            i += 1
            continue

        # --- bloque de codigo
        if s.startswith("```"):
            es_mermaid = s.lower().startswith("```mermaid")
            i += 1
            buf = []
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                buf.append(lineas[i])
                i += 1
            i += 1
            if es_mermaid:
                buf = mermaid_a_texto(buf)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            r = p.add_run("\n".join(buf))
            r.font.name = "Consolas"
            r.font.size = Pt(8)
            continue

        # --- imagen + pie de foto
        m = re.match(r"^!\[(.*?)\]\((.+?)\)$", s)
        if m:
            ruta = os.path.join(os.path.dirname(os.path.abspath(MD)), m.group(2).replace("/", os.sep))
            if os.path.exists(ruta):
                doc.add_picture(ruta, width=ancho_max)
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                n_img += 1
            else:
                print("  [!] falta la imagen:", ruta)
            # el pie va en la linea siguiente, en cursiva
            if i + 1 < len(lineas) and lineas[i + 1].strip().startswith("*"):
                pie = lineas[i + 1].strip().strip("*")
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(pie)
                r.italic = True
                r.font.size = Pt(9)
                i += 1
            i += 1
            continue

        # --- tabla
        if s.startswith("|") and i + 1 < len(lineas) and re.match(r"^\|[\s:|-]+\|$", lineas[i + 1].strip()):
            cab = [limpiar_celda(c) for c in s.strip("|").split("|")]
            i += 2
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                filas.append([limpiar_celda(c) for c in lineas[i].strip().strip("|").split("|")])
                i += 1
            t = doc.add_table(rows=1, cols=len(cab))
            t.style = "Light Grid Accent 1"
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            t.autofit = True
            for k, c in enumerate(cab):
                celda = t.rows[0].cells[k]
                celda.text = ""
                run = celda.paragraphs[0].add_run(c)
                run.bold = True
                run.font.size = Pt(8.5)
            for fila in filas:
                celdas = t.add_row().cells
                for k in range(min(len(fila), len(cab))):
                    celdas[k].text = ""
                    run = celdas[k].paragraphs[0].add_run(fila[k])
                    run.font.size = Pt(8.5)
            doc.add_paragraph()
            n_tab += 1
            continue

        # --- encabezados
        if s.startswith("#"):
            nivel = len(s) - len(s.lstrip("#"))
            doc.add_heading(s.lstrip("#").strip(), level=min(nivel, 4))
            i += 1
            continue

        # --- cita
        if s.startswith(">"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.35)
            texto_con_formato(p, s.lstrip("> ").strip())
            for r in p.runs:
                r.italic = True
            i += 1
            continue

        # --- lista con vinetas
        if re.match(r"^[-*]\s+", s):
            p = doc.add_paragraph(style="List Bullet")
            texto_con_formato(p, re.sub(r"^[-*]\s+", "", s))
            i += 1
            continue

        # --- lista numerada
        if re.match(r"^\d+\.\s+", s):
            p = doc.add_paragraph(style="List Number")
            texto_con_formato(p, re.sub(r"^\d+\.\s+", "", s))
            i += 1
            continue

        # --- parrafo normal
        if s:
            p = doc.add_paragraph()
            texto_con_formato(p, s)
        i += 1

    doc.save(DOCX)
    print("Listo: %s  (%d imagenes, %d tablas)" % (os.path.basename(DOCX), n_img, n_tab))


def main():
    objetivos = sys.argv[1:] if len(sys.argv) > 1 else INFORMES
    for nombre in objetivos:
        convertir(nombre.replace(".md", ""))


if __name__ == "__main__":
    main()
