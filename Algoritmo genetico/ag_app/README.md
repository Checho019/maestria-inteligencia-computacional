# Algoritmo genético binario con interfaz gráfica

Aplicación de escritorio en Python con PySide6 que ejecuta un algoritmo genético de codificación binaria. Trae las tres funciones de la tarea, Rastrigin (minimizar), Himmelblau (minimizar) y Peaks (maximizar), siete funciones de prueba de GEATbx (Esfera, Rosenbrock, Ackley, Griewank, Schwefel, Easom y Goldstein-Price) y una función personalizada que se escribe como expresión. Desde la ventana se eligen la función, los bits por variable, los tres operadores y todos los parámetros, y las curvas de nivel y de convergencia se actualizan en cada generación.

## Ejecución sin instalar nada

En Windows, `AlgoritmoGenetico.exe` (en la raíz de la entrega) abre la aplicación con doble clic. Tarda unos 10 segundos la primera vez.

## Instalación desde el código

Requiere Python 3.10 o posterior.

```bash
pip install -r requirements.txt
```

## Ejecución desde el código

Desde esta carpeta:

```bash
python main.py
```

Los valores por defecto son los de la tabla 6.2 de la guía (N = 50, T = 200, L = 16, Pc = 0.8, Pm = 1/ℓ, e = 1, torneo con k = 3, cruce de dos puntos y mutación bit-flip), así que basta con pulsar Iniciar. Cada parámetro explica su efecto al pasar el cursor sobre él. Con varias ejecuciones, cada una usa la semilla siguiente, la tabla muestra cada ejecución y debajo aparecen la media y la desviación estándar del mejor valor final. Una ejecución detenida con el botón Detener no entra en ese resumen. Los botones Exportar CSV y Guardar figuras guardan los resultados y las dos gráficas.

## Función personalizada

Al elegir Personalizada se escribe f como expresión de x1, ..., xn (x e y valen por x1 y x2), por ejemplo `sin(x1) * cos(x2) + 0.1*(x1**2 + x2**2)`, y se fijan el tipo de problema, el dominio [a, b] y, si se conoce, el valor óptimo. La expresión admite números, `+ - * / ** ^` y las funciones sin, cos, tan, exp, log, log10, sqrt, abs, tanh y arctan con las constantes pi y e. Se revisa con el árbol sintáctico de Python antes de evaluarla, así que no ejecuta otro código, y se rechaza si da valores no definidos dentro del dominio. Sin valor óptimo no se calcula el error ni se puede usar la parada por error.

## Estructura

| Carpeta o archivo | Contenido |
|---|---|
| `main.py` | Arranque de la interfaz |
| `interfaz/` | Vista (`ventana.py`), controlador con el hilo de ejecución (`controlador.py`) y gráficas de Matplotlib (`graficas.py`) |
| `ag/` | Motor del AG, independiente de la interfaz. `codificacion.py`, `seleccion.py` (ruleta, torneo y ranking lineal), `cruce.py` (un punto, dos puntos y uniforme), `mutacion.py` (bit-flip, un bit e inversión de segmento), `configuracion.py` (parámetros y validación) y `motor.py` (ciclo generacional, elitismo y criterios de parada) |
| `funciones/objetivo.py` | Las diez funciones de prueba con su tipo, dominio y óptimo |
| `funciones/personalizada.py` | Revisión y evaluación de la función escrita por el usuario |
| `pruebas/probar_motor.py` | Comprueba los operadores con los ejemplos de la guía, el óptimo de cada función, la función personalizada y la reproducibilidad con semilla |

Cada operador es una función registrada en el diccionario `METODOS` de su módulo, y cada función de prueba una entrada de `FUNCIONES`, así que agregar uno nuevo solo requiere escribirlo y registrarlo. Los operadores son de implementación propia y no se usa ninguna librería de algoritmos genéticos.

## Uso del motor sin la interfaz

```python
from ag import Configuracion, ejecutar

resultado = ejecutar(Configuracion(funcion="Himmelblau", seleccion="Ruleta", semilla=3))
print(resultado.mejor_x, resultado.mejor_f, resultado.generacion_mejor)
```

Las comprobaciones del motor se ejecutan con `python -m pruebas.probar_motor`.

## Construcción del ejecutable

El ejecutable se genera desde esta carpeta con PyInstaller:

```bash
pip install pyinstaller
pyinstaller main.py --onefile --windowed --name AlgoritmoGenetico --exclude-module scipy --exclude-module pandas --exclude-module tkinter
```
