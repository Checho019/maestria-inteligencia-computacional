"""Gráficas de la interfaz, embebidas con Matplotlib (sección 8.3 de la guía)."""

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

COLOR_MEJOR = "#D85A30"
COLOR_MEDIA = "#378ADD"
COLOR_PEOR = "#888780"
COLOR_OPTIMO = "#1D9E75"


class GraficaNiveles(FigureCanvasQTAgg):
    """Curvas de nivel de la función con la población decodificada encima."""

    def __init__(self):
        self.figura = Figure(figsize=(5, 4.4), layout="constrained")
        super().__init__(self.figura)
        self.ejes = self.figura.add_subplot()
        self.poblacion = None
        self.mejor = None
        self.fondo = None       # curvas de nivel guardadas, en cada generación se repinta solo la población
        self.mpl_connect("draw_event", self._al_dibujar)

    def _al_dibujar(self, _evento):
        self.fondo = self.copy_from_bbox(self.ejes.bbox)
        self._pintar_poblacion()

    def _pintar_poblacion(self):
        if self.poblacion is not None:
            self.ejes.draw_artist(self.poblacion)
            self.ejes.draw_artist(self.mejor)

    def preparar(self, objetivo, n):
        """Dibuja el fondo una sola vez por función. Con más de 2 variables se
        muestra el corte en x1 y x2 con las demás en el valor `corte` de la
        función (su coordenada óptima, o el centro del dominio si no se conoce)."""
        self.ejes.clear()
        a, b = objetivo.dominio
        malla = np.linspace(a, b, 250)
        X1, X2 = np.meshgrid(malla, malla)
        puntos = np.full((X1.size, n), objetivo.corte)
        puntos[:, 0], puntos[:, 1] = X1.ravel(), X2.ravel()
        Z = objetivo.f(puntos).reshape(X1.shape)
        self.ejes.contourf(X1, X2, Z, levels=30, cmap="viridis", alpha=0.85)
        self.ejes.contour(X1, X2, Z, levels=15, colors="k", linewidths=0.3, alpha=0.5)
        if objetivo.x_optimos:
            optimos = np.array(objetivo.x_optimos)
            self.ejes.plot(optimos[:, 0], optimos[:, 1], "x", color="white", ms=9, mew=2,
                           label="Óptimo conocido")
        self.poblacion, = self.ejes.plot([], [], "o", color="white", mec="k", ms=5,
                                         label="Población", animated=True)
        self.mejor, = self.ejes.plot([], [], "*", color=COLOR_MEJOR, mec="k", ms=16,
                                     label="Mejor hallado", animated=True)
        self.ejes.set_xlim(a, b)
        self.ejes.set_ylim(a, b)
        self.ejes.set_xlabel("$x_1$")
        self.ejes.set_ylabel("$x_2$")
        nombre = f"f = {objetivo.expresion}" if objetivo.expresion else objetivo.nombre
        if len(nombre) > 45:
            nombre = nombre[:44] + "…"
        corte = f" ($x_3..x_{{{n}}}={objetivo.corte:g}$)" if n > 2 else ""
        self.ejes.set_title(f"{nombre}{corte}", fontsize=10)
        self.ejes.legend(loc="upper right", fontsize=8, framealpha=0.8)
        self.fondo = None
        self.draw_idle()

    def actualizar(self, estado):
        self.poblacion.set_data(estado.X[:, 0], estado.X[:, 1])
        self.mejor.set_data([estado.mejor_x[0]], [estado.mejor_x[1]])
        if self.fondo is None:
            self.draw_idle()
            return
        self.restore_region(self.fondo)
        self._pintar_poblacion()
        self.blit(self.ejes.bbox)

    def guardar(self, ruta, dpi=200):
        """Guarda la figura con la población, que por el blitting no entra en el
        dibujo normal."""
        for artista in (self.poblacion, self.mejor):
            artista.set_animated(False)
        try:
            self.figura.savefig(ruta, dpi=dpi)
        finally:
            for artista in (self.poblacion, self.mejor):
                artista.set_animated(True)
            self.draw_idle()


class GraficaConvergencia(FigureCanvasQTAgg):
    """Mejor, media y peor valor de f por generación, con el óptimo punteado."""

    def __init__(self):
        self.figura = Figure(figsize=(5, 4.4), layout="constrained")
        super().__init__(self.figura)
        self.ejes = self.figura.add_subplot()
        self.lineas = {}

    def preparar(self, objetivo, T, logaritmica=False, tolerancia=1e-3, f_optimo=None):
        """La escala logarítmica solo se ofrece para funciones con mínimo 0. Sin
        óptimo conocido no se dibuja la línea de referencia."""
        self.ejes.clear()
        # Límites fijos mientras no hay datos, el ajuste automático se enciende al final
        centro = 0.0 if f_optimo is None else f_optimo
        if logaritmica:
            self.ejes.set_ylim(tolerancia / 10, 100)
            self.ejes.set_yscale("log")
        else:
            self.ejes.set_ylim(centro - 1, centro + 1)
        for nombre, color, ancho in (("Peor", COLOR_PEOR, 1.0), ("Media", COLOR_MEDIA, 1.2),
                                     ("Mejor", COLOR_MEJOR, 1.8)):
            self.lineas[nombre], = self.ejes.plot([], [], color=color, lw=ancho, label=nombre)
        if f_optimo is not None and not logaritmica:
            self.ejes.axhline(f_optimo, color=COLOR_OPTIMO, ls="--", lw=1.2,
                              label=f"Óptimo ({f_optimo:.4f})")
        elif f_optimo is not None:
            # El 0 no cabe en escala logarítmica, se marca la tolerancia
            self.ejes.axhline(tolerancia, color=COLOR_OPTIMO, ls="--", lw=1.2,
                              label=f"Óptimo 0 más la tolerancia ({tolerancia:g})")
        self.ejes.set_xlim(0, max(T, 1))
        self.ejes.set_xlabel("Generación")
        self.ejes.set_ylabel("f(x)")
        self.ejes.set_title(f"Convergencia ({objetivo.tipo.lower()})", fontsize=10)
        self.ejes.grid(alpha=0.3)
        self.ejes.legend(loc="best", fontsize=8)
        self.ejes.set_autoscaley_on(True)
        self.draw_idle()

    def actualizar(self, estado):
        generaciones = np.arange(len(estado.mejor))
        for nombre, valores in (("Mejor", estado.mejor), ("Media", estado.media),
                                ("Peor", estado.peor)):
            self.lineas[nombre].set_data(generaciones, valores)
        self.ejes.relim()
        self.ejes.autoscale_view(scalex=False)
        self.draw_idle()
