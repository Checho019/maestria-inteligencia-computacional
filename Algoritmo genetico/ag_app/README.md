# Algoritmo genético binario con interfaz gráfica

Aplicación de escritorio en Python con PySide6 que ejecuta un algoritmo genético de codificación binaria sobre Rastrigin (minimizar), Himmelblau (minimizar) y Peaks (maximizar). Desde la ventana se eligen la función, los bits por variable, los tres operadores y todos los parámetros, y las curvas de nivel y de convergencia se actualizan en cada generación.

## Instalación

Requiere Python 3.10 o posterior.

```bash
pip install -r requirements.txt
```

## Ejecución

Desde esta carpeta:

```bash
python main.py
```

Los valores por defecto son los de la tabla 6.2 de la guía (N = 50, T = 200, L = 16, Pc = 0.8, Pm = 1/ℓ, e = 1, torneo con k = 3, cruce de dos puntos y mutación bit-flip), así que basta con pulsar Iniciar. Cada parámetro explica su efecto al pasar el cursor sobre él. Con varias corridas, cada una usa la semilla siguiente y la tabla de resultados muestra la media y la desviación estándar del mejor valor final. Los botones Exportar CSV y Guardar figuras guardan los resultados y las dos gráficas.

## Estructura

| Carpeta o archivo | Contenido |
|---|---|
| `main.py` | Arranque de la interfaz |
| `interfaz/` | Vista (`ventana.py`), controlador con el hilo de ejecución (`controlador.py`) y gráficas de Matplotlib (`graficas.py`) |
| `ag/` | Motor del AG, independiente de la interfaz. `codificacion.py`, `seleccion.py` (ruleta, torneo y ranking lineal), `cruce.py` (un punto, dos puntos y uniforme), `mutacion.py` (bit-flip, un bit e inversión de segmento), `configuracion.py` (parámetros y validación) y `motor.py` (ciclo generacional, elitismo y criterios de parada) |
| `funciones/objetivo.py` | Las tres funciones con su tipo, dominio y óptimo |
| `pruebas/probar_motor.py` | Comprueba los operadores con los ejemplos de la guía y la reproducibilidad con semilla |

Cada operador es una función registrada en el diccionario `METODOS` de su módulo, así que agregar uno nuevo solo requiere escribir la función y registrarla. Los operadores son de implementación propia y no se usa ninguna librería de algoritmos genéticos.

## Uso del motor sin la interfaz

```python
from ag import Configuracion, ejecutar

resultado = ejecutar(Configuracion(funcion="Himmelblau", seleccion="Ruleta", semilla=3))
print(resultado.mejor_x, resultado.mejor_f, resultado.generacion_mejor)
```

Las comprobaciones del motor se ejecutan con `python -m pruebas.probar_motor`.
