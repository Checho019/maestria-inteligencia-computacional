# Taller 1. Perceptrón y Adaline

## Versión 2, sobre la plantilla del profesor

En `v2/` está la entrega definitiva. El profesor entregó un live script base con las funciones `init_perceptron`, `compute_delta`, `train_adaline` y `split_dataset` por completar y un formato de informe en LaTeX, y pidió que se conservaran los nombres y argumentos de las funciones. `v2/Taller1_Perceptron_Adaline_LiveScript.mlx` es ese script completado y ejecutado, con los reportes de aprendizaje (tres reglas, alpha, umbral, pesos iniciales) y las particiones de billetes para los dos modelos. El informe está en `v2/informe/main.pdf` y la carpeta `v2/entrega_v2/` con el zip `Taller1_v2_SergioDuarte.zip` trae lo que se sube, el mlx, el dataset y el PDF.

Para regenerar figuras y mlx desde la carpeta del taller

```matlab
addpath('herramientas'); generar_v2
```

## Versión 1

Red de una sola neurona en MATLAB, primero como perceptrón simple con las tres reglas de corrección del taller y después como Adaline con la regla delta. Se prueba en compuertas AND y OR de 2, 3 y 4 entradas, en Iris y en el dataset de autenticación de billetes, con particiones 60-40, 70-30, 80-20 y 90-10.

## Scripts

| Archivo | Punto del taller |
|---|---|
| `T0_Dataset_train_test.m` | el script de particiones de clase, sobre Iris |
| `T1_perceptron_compuertas.m` | 1, 2, 3 |
| `T2_perceptron_iris.m` | 4 |
| `T3_dataset_banknote.m` | 5 |
| `T4_perceptron_banknote.m` | 6 |
| `T5_adaline_compuertas.m` | 7, 8, 9 |
| `T6_adaline_iris.m` | 10 |
| `T7_adaline_banknote.m` | 11, 12 |
| `R1_revision_iris.m`, `R2_revision_banknote.m` | revisión de los datos, una tabla por paso |
| `R3_modelos_por_paso.m` | perceptrón y Adaline sobre cada versión del dato |

Funciones que usan los scripts

| Función | Qué hace |
|---|---|
| `perceptron.m` | entrena la neurona con la regla 1, 2 o 3 |
| `adaline.m` | entrena con la regla delta sobre la salida lineal |
| `predecir.m` | suma ponderada y escalón |
| `compuerta.m` | tabla de verdad de AND, OR o XOR de n entradas |
| `graficar_frontera.m` | patrones y recta separadora en 2 entradas |

Los `.mlx` ya ejecutados están en `mlx/` y su PDF en `pdf/`. El informe está en `informe/main.pdf`. La revisión de datos está en `Revision_datos.docx`.

`iris.dat` se generó desde `fisheriris` de MATLAB con la clase codificada 1, 2, 3, porque el zip de clase no lo traía. `data_banknote_authentication.txt` es el original del taller.

## Para regenerar todo

Desde la carpeta del taller, en MATLAB

```matlab
addpath('herramientas'); correr_todo
```
