# Taller 1: Perceptrón y Adaline

Red de una sola neurona en MATLAB, primero como perceptrón simple con las tres reglas de corrección del taller y después como Adaline con la regla delta. Se prueba en compuertas AND y OR de 2, 3 y 4 entradas, en Iris y en el dataset de autenticación de billetes, con particiones 60-40, 70-30, 80-20 y 90-10.

## Qué hay

| Archivo | Punto del taller | Qué hace |
|---|---|---|
| `T0_Dataset_train_test.m` | base del 4 | el script de particiones de clase, sobre Iris, guardando las cuatro particiones |
| `T1_perceptron_compuertas.m` | 1, 2, 3 | perceptrón parametrizable y reporte de aprendizaje en compuertas |
| `T2_perceptron_iris.m` | 4 | perceptrón sobre las particiones de Iris con varios alpha |
| `T3_dataset_banknote.m` | 5 | el script de particiones modificado para banknote |
| `T4_perceptron_banknote.m` | 6 | perceptrón sobre las particiones de banknote |
| `T5_adaline_compuertas.m` | 7, 8, 9 | Adaline y reporte en compuertas |
| `T6_adaline_iris.m` | 10 | Adaline sobre Iris |
| `T7_adaline_banknote.m` | 11, 12 | Adaline sobre banknote |

Las funciones están aparte para no repetirlas en cada script:

| Función | Qué hace |
|---|---|
| `perceptron.m` | entrena la neurona con la regla 1, 2 o 3; parámetros en una estructura |
| `adaline.m` | entrena con la regla delta sobre la salida lineal; para por error mínimo o por estancamiento del EC |
| `predecir.m` | suma ponderada y escalón, sirve para los dos modelos |
| `compuerta.m` | tabla de verdad de AND, OR o XOR de n entradas |
| `graficar_frontera.m` | dibuja los patrones y la recta separadora en 2 entradas |
| `guardar_fig.m` | exporta la figura a `informe/figuras` con fondo claro |

Los `.mlx` ya ejecutados, con salidas y gráficas adentro, están en `mlx/`, y una versión en PDF de cada uno en `pdf/`. El informe en formato IEEE está en `informe/main.pdf`, con su fuente en `informe/main.tex`.

## Cómo correrlo

Desde la carpeta del taller, en MATLAB:

```matlab
correr_todo      % corre los ocho scripts en orden y deja tablas y figuras en informe/
generar_mlx      % convierte los .m a .mlx, los ejecuta y exporta los PDF
```

`iris.dat` se generó a partir de `fisheriris` de MATLAB con la clase codificada 1, 2, 3, porque el zip de clase no lo traía. `data_banknote_authentication.txt` es el original del taller.

Todo usa semillas fijas, así que los números se repiten.

## Para compilar el informe

```bash
cd informe
latexmk -pdf main.tex
```

Necesita la clase `IEEEtran` y `babel` en español, que vienen con MiKTeX o TeX Live.
