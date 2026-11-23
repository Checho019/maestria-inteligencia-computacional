"""Lectura de los campos de la ventana. Convierte el formulario en una
Configuracion y en mensajes de error claros, sin tocar la interfaz."""

import math

from ag import Configuracion, validar
from ag.codificacion import bits_por_precision
from ag.configuracion import verbo
from funciones import personalizada
from funciones.objetivo import FUNCIONES, PERSONALIZADA


def texto_numerico(campo):
    return campo.text().strip().replace(",", ".")


def numero_opcional(campo):
    """Número finito o None si el campo está vacío. Lanza ValueError si no es número."""
    texto = texto_numerico(campo)
    if not texto:
        return None
    valor = float(texto)
    if not math.isfinite(valor):
        raise ValueError
    return valor


def n_elegido(v):
    """Número de variables de la función elegida, o None si el campo no es entero."""
    nombre = v.funcion.currentText()
    fijo = FUNCIONES[nombre].n_fijo if nombre in FUNCIONES else None
    try:
        return fijo or int(v.n.text())
    except ValueError:
        return None


def objetivo_elegido(v):
    """Función elegida y un mensaje si la personalizada no es válida."""
    nombre = v.funcion.currentText()
    if nombre != PERSONALIZADA:
        return FUNCIONES[nombre], ""
    try:
        n = int(v.n.text())
    except ValueError:
        return None, "El número de variables n debe ser un entero entre 2 y 50."
    try:
        a, b = float(texto_numerico(v.a)), float(texto_numerico(v.b))
    except ValueError:
        return None, "Los límites a y b deben ser números."
    try:
        optimo = numero_opcional(v.optimo_personalizada)
    except ValueError:
        return None, "El valor óptimo debe ser un número o quedar vacío."
    if not (math.isfinite(a) and math.isfinite(b) and a < b and 2 <= n <= 50):
        return None, "Revise el dominio (a < b) y el número de variables (2 a 50)."
    try:
        return personalizada.crear(v.expresion.text(), a, b,
                                   v.tipo_personalizada.currentText() == "Maximizar", optimo, n), ""
    except ValueError as error:
        return None, str(error)


def bits_elegidos(v, objetivo):
    """L del campo o calculado con la precisión, o None si no se puede leer."""
    try:
        if v.modo_L.currentText() == "Bits por variable":
            return int(v.L.text())
        a, b = objetivo.dominio
        return bits_por_precision(a, b, float(texto_numerico(v.eps)))
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


class _Lector:
    """Lee campos numéricos y acumula los errores. Un campo ilegible toma su valor
    por defecto para no provocar errores de rango en cadena."""

    def __init__(self):
        self.errores, self.ilegibles = [], []
        self.defecto = Configuracion()

    def numero(self, campo, nombre, tipo, clave=None):
        try:
            valor = tipo(texto_numerico(campo))
            if math.isfinite(valor):
                return valor
        except ValueError:
            pass
        clase = "un número entero" if tipo is int else "un número finito"
        self.errores.append(f"{nombre} {verbo(nombre)} ser {clase} (se recibió \"{campo.text()}\").")
        self.ilegibles.append(nombre)
        return getattr(self.defecto, clave) if clave else tipo(1)

    def si(self, activo, campo, nombre, tipo, clave):
        """Solo se leen los campos activos, así un texto olvidado en un campo oculto
        no bloquea la ejecución."""
        return self.numero(campo, nombre, tipo, clave) if activo else getattr(self.defecto, clave)


def leer(v):
    """Devuelve ((cfg, ejecuciones, pausa), errores) a partir de la ventana v."""
    lector = _Lector()
    numero, si = lector.numero, lector.si
    seleccion, cruce, mutacion = v.seleccion.currentText(), v.cruce.currentText(), v.mutacion.currentText()
    bit_flip = mutacion == "Bit-flip por bit"
    cfg = Configuracion(
        funcion=v.funcion.currentText(),
        n=numero(v.n, "El número de variables n", int, "n"),
        N=numero(v.N, "El tamaño de población N", int, "N"),
        T=numero(v.T, "Las generaciones T", int, "T"),
        pc=numero(v.pc, "La probabilidad de cruce Pc", float, "pc"),
        elites=numero(v.elites, "El número de élites e", int, "elites"),
        semilla=numero(v.semilla, "La semilla", int, "semilla"),
        seleccion=seleccion,
        k=si(seleccion == "Torneo", v.k, "El tamaño del torneo k", int, "k"),
        s=si(seleccion == "Ranking lineal", v.s, "La presión selectiva s", float, "s"),
        cruce=cruce,
        p0=si(cruce == "Uniforme", v.p0, "La probabilidad de intercambio p0", float, "p0"),
        mutacion=mutacion,
        pm=None if v.pm_auto.isChecked() or not bit_flip
        else numero(v.pm, "La probabilidad de mutación por bit Pm", float),
        pmi=si(not bit_flip, v.pmi, "La probabilidad de mutación por individuo Pmi", float, "pmi"),
        parar_por_error=v.parar_error.isChecked(),
        tolerancia=si(v.parar_error.isChecked(), v.tolerancia, "La tolerancia del error", float, "tolerancia"),
        parar_por_estancamiento=v.parar_estancamiento.isChecked(),
        G=si(v.parar_estancamiento.isChecked(), v.G, "Las generaciones sin mejora G", int, "G"),
    )
    if cfg.funcion == PERSONALIZADA:
        cfg.expresion = v.expresion.text()
        cfg.a = numero(v.a, "El límite inferior a", float, "a")
        cfg.b = numero(v.b, "El límite superior b", float, "b")
        cfg.maximizar = v.tipo_personalizada.currentText() == "Maximizar"
        cfg.optimo = (None if not v.optimo_personalizada.text().strip()
                      else numero(v.optimo_personalizada, "El valor óptimo", float))
    _leer_bits(v, cfg, lector)
    ejecuciones = numero(v.ejecuciones, "El número de ejecuciones", int)
    pausa = numero(v.pausa, "La pausa por generación", int)

    errores, ilegibles = lector.errores, lector.ilegibles
    # Los rangos se revisan aunque otro campo no se haya leído, sin repetir los ilegibles
    errores += [e for e in validar(cfg) if not any(e.startswith(n) for n in ilegibles)]
    if "El número de ejecuciones" not in ilegibles and not 1 <= ejecuciones <= 100:
        errores.append(f"El número de ejecuciones debe estar entre 1 y 100 (se recibió {ejecuciones}).")
    if "La pausa por generación" not in ilegibles and not 0 <= pausa <= 2000:
        errores.append(f"La pausa debe estar entre 0 y 2000 ms (se recibió {pausa}).")
    return (cfg, ejecuciones, pausa), errores


def _leer_bits(v, cfg, lector):
    """Fija cfg.L desde el campo L o desde la precisión ε."""
    if v.modo_L.currentText() == "Bits por variable":
        cfg.L = lector.numero(v.L, "Los bits por variable L", int, "L")
        return
    eps = lector.numero(v.eps, "La precisión ε", float)
    a, b = (cfg.a, cfg.b) if cfg.funcion == PERSONALIZADA else cfg.objetivo.dominio
    if eps <= 0:
        lector.errores.append("La precisión ε debe ser mayor que 0.")
    elif "La precisión ε" not in lector.ilegibles and a < b:
        try:
            cfg.L = bits_por_precision(a, b, eps)
        except (OverflowError, ValueError):
            lector.errores.append(f"La precisión ε = {eps:g} es demasiado pequeña.")
