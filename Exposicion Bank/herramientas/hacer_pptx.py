"""Arma exposicion_bank.pptx con las figuras de figuras/. Se corre desde la carpeta Exposicion Bank."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

AZUL = RGBColor(0x1F, 0x3A, 0x5F)
GRIS = RGBColor(0x55, 0x55, 0x55)
FIG = "figuras"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blanco = prs.slide_layouts[6]


def titulo(slide, texto, sub=None):
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.3), Inches(0.9))
    p = tb.text_frame.paragraphs[0]
    p.text = texto
    p.font.size = Pt(30); p.font.bold = True; p.font.color.rgb = AZUL; p.font.name = "Calibri"
    if sub:
        p2 = tb.text_frame.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(16); p2.font.color.rgb = GRIS; p2.font.name = "Calibri"
    ln = slide.shapes.add_shape(1, Inches(0.5), Inches(1.25), Inches(12.3), Inches(0.04))
    ln.fill.solid(); ln.fill.fore_color.rgb = AZUL; ln.line.fill.background()


def vinetas(slide, items, left, top, w, h, size=18):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    for k, it in enumerate(items):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        nivel = 0
        if it.startswith("  "):
            nivel = 1; it = it.strip()
        p.text = ("• " if nivel == 0 else "– ") + it
        p.level = nivel
        p.font.size = Pt(size - 2 * nivel); p.font.name = "Calibri"
        p.space_after = Pt(6)


def imagen(slide, nombre, left, top, w):
    slide.shapes.add_picture(os.path.join(FIG, nombre), Inches(left), Inches(top), width=Inches(w))


def tabla(slide, cab, filas, left, top, w, h, size=13, anchos=None):
    t = slide.shapes.add_table(len(filas) + 1, len(cab), Inches(left), Inches(top), Inches(w), Inches(h)).table
    for j, a in enumerate(anchos or []):
        t.columns[j].width = Inches(a)
    for j, c in enumerate(cab):
        cel = t.cell(0, j); cel.text = c
        for p in cel.text_frame.paragraphs:
            p.font.size = Pt(size); p.font.bold = True; p.font.name = "Calibri"
    for i, fila in enumerate(filas):
        for j, c in enumerate(fila):
            cel = t.cell(i + 1, j); cel.text = str(c)
            for p in cel.text_frame.paragraphs:
                p.font.size = Pt(size); p.font.name = "Calibri"


def pie(slide, texto):
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(6.9), Inches(12.3), Inches(0.5))
    tb.text_frame.word_wrap = True
    p = tb.text_frame.paragraphs[0]; p.text = texto
    p.font.size = Pt(12); p.font.color.rgb = GRIS; p.font.name = "Calibri"


def nueva(texto, sub=None):
    s = prs.slides.add_slide(blanco)
    titulo(s, texto, sub)
    return s


def portada():
    s = prs.slides.add_slide(blanco)
    tb = s.shapes.add_textbox(Inches(1), Inches(2.3), Inches(11.3), Inches(3))
    tf = tb.text_frame; tf.word_wrap = True
    lineas = [("Bank Marketing", 44, AZUL, True),
              ("Preparación del dataset paso a paso para la herramienta de clasificación", 24, GRIS, False),
              ("", 12, GRIS, False),
              ("Sergio Duarte", 20, None, False),
              ("Inteligencia Computacional. Maestría en Ciencias de la Información y las Comunicaciones", 16, GRIS, False),
              ("Universidad Distrital Francisco José de Caldas", 16, GRIS, False)]
    for k, (t, sz, col, neg) in enumerate(lineas):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.text = t; p.font.size = Pt(sz); p.font.bold = neg; p.font.name = "Calibri"
        if col: p.font.color.rgb = col


portada()

s = nueva("El dataset y el plan", "UCI Machine Learning Repository, Bank Marketing (Moro, Cortez y Rita, 2014)")
vinetas(s, [
    "Campañas telefónicas de un banco portugués entre 2008 y 2010. Objetivo, predecir si el cliente suscribe un depósito a plazo",
    "45 211 registros, 16 atributos de entrada y la clase y",
    "Sin valores faltantes explícitos, pero job, education, contact y poutcome usan la etiqueta unknown",
    "Clase muy desbalanceada, 39 922 no frente a 5 289 sí (11.7 % de positivos)",
    "Cuatro versiones del dato, cada una probada en Classification Learner con validación cruzada de 5 particiones",
    "  T0 crudo, tal como viene",
    "  T1 arreglo de columnas, filas, faltantes y atípicos",
    "  T2 codificación y estandarización",
    "  T3 balanceo, por submuestreo (T3_1) y por sobremuestreo (T3_2)",
], 0.7, 1.6, 12, 5.3)

s = nueva("T0. Numéricas", "Histogramas de las siete variables numéricas y de la clase")
imagen(s, "fig01.png", 0.5, 1.45, 8.6)
vinetas(s, [
    "age es la única con una distribución aproximadamente simétrica",
    "balance, campaign y previous presentan colas muy pronunciadas, con valores hasta 102 127, 63 y 275",
    "pdays es casi toda -1 (82 % nunca contactados)",
    "duration se concentra en llamadas cortas",
    "y desbalanceada, 7.5 no por cada sí",
], 9.3, 1.6, 3.7, 5.5, size=16)

s = nueva("T0. Categóricas y valores unknown", "El dataset no trae faltantes, pero unknown cumple ese papel")
imagen(s, "fig03.png", 0.5, 1.45, 7.6)
tabla(s, ["Variable", "unknown", "Decisión"], [
    ["job", "288 (0.6 %)", "se eliminan las filas"],
    ["education", "1 857 (4.1 %)", "se imputa con la moda del oficio"],
    ["contact", "13 020 (28.8 %)", "se conserva como categoría"],
    ["poutcome", "36 959 (81.7 %)", "coincide con nunca contactado"],
], 8.4, 1.6, 4.6, 2.2, size=13)
vinetas(s, [
    "month muy concentrado en mayo",
    "default casi constante, 1.8 % en mora",
], 8.4, 4.4, 4.6, 1.5, size=15)

s = nueva("T1. Arreglo de columnas", "Menos columnas y con significado, con intervención mínima sobre el dato")
tabla(s, ["Columna", "Tratamiento", "Por qué"], [
    ["duration", "se elimina", "solo se conoce al terminar la llamada, es fuga de información hacia la clase"],
    ["day y month", "se unen en dia_anio (1 a 365)", "una sola columna numérica en vez de una numérica y una categórica de 12 niveles"],
    ["education", "ordinal 1, 2, 3", "los niveles tienen orden natural, no hace falta one hot"],
    ["job unknown", "se eliminan 288 filas", "no hay con qué imputar y son el 0.6 %"],
    ["pdays", "dos campos, ver siguiente lámina", "el -1 es un código de ausencia, no una cantidad de días"],
    ["age, balance, campaign", "atípicos recortados al borde de 1.5 IQR", "480, 4 712 y 3 031 valores, sin borrar filas"],
    ["previous", "recorte al percentil 99 (9)", "rango intercuartil cero, la regla de Tukey no aplica"],
], 0.5, 1.5, 12.3, 4.2, size=13)
pie(s, "Resultado 44 923 filas y 15 columnas de entrada.")

s = nueva("T1. pdays y el umbral de contacto previo", "Tasa de sí según los días desde el último contacto")
imagen(s, "fig04.png", 0.5, 1.45, 7.4)
vinetas(s, [
    "Nunca contactado responde sí el 9.2 % de las veces (línea roja)",
    "Hasta 239 días la tasa se mantiene muy por encima de la base",
    "Entre 240 y 364 días cae a 12 % y 8.6 %, ya se comporta como nunca contactado",
    "Desde 365 días la tasa vuelve a subir a 27 %, pero son 691 filas (1.5 %) y se asumen bajo el mismo umbral",
    "Umbral elegido 240 días. contactado_antes vale 1 si pdays está entre 0 y 240, y pdays se deja en 240 para el resto",
], 8.1, 1.6, 4.9, 5.5, size=15)

s = nueva("T2. Codificación y estandarización", "Todo queda numérico para la herramienta de clasificación")
tabla(s, ["Tipo", "Variables", "Método", "Columnas"], [
    ["binaria", "default, housing, loan, contactado_antes", "0 y 1", "4"],
    ["ordinal", "education", "1 primary, 2 secondary, 3 tertiary", "1"],
    ["nominal", "job, marital, contact, poutcome", "one hot, sin poutcome_unknown por redundante", "20"],
    ["numérica", "age, balance, campaign, pdays, previous, dia_anio", "z score, media cero y desviación uno", "6"],
], 0.5, 1.5, 12.3, 2.4, size=13)
vinetas(s, [
    "De 15 columnas de entrada se pasa a 31, todas numéricas",
    "Las indicadoras y education no se escalan, ya están en una escala corta y así se pueden redondear en el sobremuestreo",
    "Con todo numérico KNN funciona, cada categórica distinta entre dos clientes suma un salto fijo a la distancia",
], 0.7, 4.3, 12, 2.5, size=16)

s = nueva("T3. Balanceo por dos caminos", "Submuestreo de la clase no (T3_1) y sobremuestreo sintético de la clase sí (T3_2)")
imagen(s, "fig07.png", 0.5, 1.45, 7.4)
vinetas(s, [
    "T3_1. Se toman al azar 5 255 no para igualar a los 5 255 sí, quedan 10 510 filas",
    "T3_2. Se crean 34 413 sí sintéticos entre cada positivo y uno de sus cinco vecinos más cercanos, quedan 79 336 filas",
    "En T3_2 las indicadoras y education se redondean para no crear clientes con medio oficio",
    "El sobremuestreo se hace antes de partir, así que los sintéticos quedan al lado de sus originales en la validación cruzada",
], 8.1, 1.6, 4.9, 5.5, size=15)

s = nueva("Resultados en Classification Learner", "Mejor modelo de cada versión, validación cruzada de 5 particiones")
tabla(s, ["Versión", "Filas", "Mejor modelo", "Exactitud", "Sí acertados", "No acertados"], [
    ["T0", "45 211", "Narrow Neural Network", "90.6 %", "2 632 de 5 289 (49.8 %)", "96.0 %"],
    ["T1", "44 923", "Boosted Trees", "89.4 %", "828 de 5 255 (15.8 %)", "99.1 %"],
    ["T2", "44 923", "Boosted Trees", "89.4 %", "818 de 5 255 (15.6 %)", "99.1 %"],
    ["T3_1", "10 510", "Boosted Trees", "71.1 %", "2 943 de 5 255 (56.0 %)", "84.8 %"],
    ["T3_2", "79 336", "Fine KNN", "90.8 %", "38 439 de 39 668 (96.9 %)", "84.7 %"],
], 0.5, 1.5, 12.3, 3.0, size=14, anchos=[1.2, 1.2, 2.8, 1.5, 3.3, 2.3])
vinetas(s, [
    "Predecir siempre no ya da 88.3 % de exactitud, por eso la exactitud sola dice poco",
    "T0 gana por duration, que es información posterior a la llamada. Sin ella la exactitud baja un punto y el modelo casi deja de acertar los sí",
    "T1 y T2 dan lo mismo, la codificación y el escalado no cambian el resultado de los árboles",
], 0.7, 4.9, 12, 2.2, size=15)

s = nueva("Lectura de los resultados", "Qué versión conviene usar")
vinetas(s, [
    "T3_1 pierde exactitud global pero pasa de acertar el 16 % de los sí a acertar el 56 %, que es lo que le interesa al banco",
    "T3_2 da el mejor número, 90.8 %, pero lo consigue Fine KNN con un solo vecino, que encuentra al lado de cada sintético el positivo original del que salió",
    "Esa cifra está inflada por hacer el sobremuestreo antes de partir. Para confiar en ella habría que sobremuestrear solo dentro del entrenamiento de cada partición",
    "La versión honesta es T3_1, y la mejora real frente a T2 es de sensibilidad, no de exactitud",
    "Referencias",
    "  Moro, S., Cortez, P. y Rita, P. (2014). A data driven approach to predict the success of bank telemarketing. Decision Support Systems, 62, 22 a 31",
    "  Tukey, J. W. (1977). Exploratory Data Analysis. Addison Wesley",
], 0.7, 1.6, 12, 5.5, size=17)

prs.save("exposicion_bank.pptx")
print("Listo exposicion_bank.pptx,", len(prs.slides), "laminas")
