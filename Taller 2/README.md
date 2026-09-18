# Taller 2. Redes neuronales multicapa y backpropagation

Perceptrón multicapa entrenado por retropropagación, sobre la plantilla del docente. Se completaron `init_mlp`, `forward_mlp`, `backward_mlp` y `activation_deriv` sin cambiar nombres ni argumentos, y se agregaron los experimentos de los numerales 3 a 6.

| Sección | Numeral | Qué hace |
|---|---|---|
| 9.1 y 9.2 | 3 | XOR de 2 y 3 entradas contra el Perceptrón y el Adaline del Taller 1, efecto del momento y de la activación |
| 10 | 4 | Iris multiclase, cuatro arquitecturas por tres tasas, matrices de confusión y curvas de error |
| 11 | 5 | Wine, Breast Cancer Wisconsin y billetes en las particiones 60-40, 70-30, 80-20 y 90-10, contra el Taller 1 |
| 12 | 6 | Sobreajuste en Breast Cancer variando neuronas ocultas y épocas, parada temprana por épocas sin mejora |

Cuando un experimento necesita validación, sea para la curva de error o para la parada temprana, se aparta una quinta parte del entrenamiento y la exactitud se mide siempre sobre la prueba. `Dataset_train_test_T2.m` es la versión para Wine y Breast Cancer del script de particiones del Taller 1, con la misma semilla que el live script, así que sus cortes de entrenamiento y prueba son los evaluados.

Los datos van en `datos/`, el informe en `informe/main.pdf` y lo que se sube en `entrega/`, el PDF aparte y un RAR con los dos live scripts ejecutados y los cuatro archivos de datos. Los dos live scripts corren en unos dos minutos desde una carpeta limpia. Los tiempos de entrenamiento cambian un poco entre ejecuciones, el resto de las cifras es idéntico.

Para regenerar figuras y mlx desde esta carpeta

```matlab
addpath('herramientas'); generar_t2
```
