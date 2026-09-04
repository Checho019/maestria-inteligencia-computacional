# Bank Marketing. Preparación del dato paso a paso

Un solo live script, `procesar_bank.mlx`, que toma el dataset Bank Marketing de UCI y deja cuatro versiones listas para Classification Learner.

| Paso | Qué hace |
|---|---|
| T0 | dato crudo, histogramas, cajas y categóricas |
| T1 | quita `duration`, une `day` y `month` en `dia_anio`, `education` ordinal, `pdays` en dos campos con umbral de 240 días, atípicos recortados con 1.5 IQR |
| T2 | binarias en 0 y 1, one hot en `job`, `marital`, `contact` y `poutcome`, z score (`T2z`) y rango 0 a 1 (`T2n`) |
| T3 | submuestreo de la clase no hasta 5255 por clase (`T3z`, `T3n`) |

Las tablas quedan en `bank_pasos.mat`. En Classification Learner se importa la tabla desde el workspace con `y` como respuesta.

El dataset va en `data/bank-full.csv`, se saca de `bank+marketing.zip` de la Primera actividad. La exposición está en `exposicion_bank.pptx`.

Para regenerar figuras, mlx y presentación desde la carpeta

```matlab
addpath('herramientas'); generar
```

```bash
python herramientas/hacer_pptx.py
```
