# Bank Marketing. Preparación del dato paso a paso

Un solo live script, `procesar_bank.mlx`, que toma el dataset Bank Marketing de UCI y deja el dato en varias versiones listas para Classification Learner.

| Paso | Qué hace | Tablas |
|---|---|---|
| T0 | dato crudo, histogramas, cajas y categóricas | `T0` |
| T1 | quita `duration`, une `day` y `month` en `dia_anio`, `education` ordinal 1 a 3, `pdays` en dos campos con umbral de 240 días, atípicos recortados con 1.5 IQR | `T1` |
| T2 | binarias en 0 y 1, one hot en `job`, `marital`, `contact` y `poutcome`, z score o rango 0 a 1 sobre las seis numéricas | `T2z`, `T2n` |
| T3_1 | submuestreo aleatorio de la clase no hasta 5255 por clase | `T3_1z`, `T3_1n` |
| T3_2 | sobremuestreo sintético de la clase sí entre vecinos hasta 39668 por clase, con las indicadoras y `education` redondeadas | `T3_2z`, `T3_2n` |

Las tablas quedan en `bank_pasos.mat`. En Classification Learner se importa la tabla desde el workspace con `y` como respuesta.

El escalado y el sobremuestreo se calculan sobre todo el conjunto porque la partición se delega a Classification Learner. Por eso la validación cruzada sobre `T3_2` sale algo optimista y la comparación de referencia es `T3_1`.

El dataset va en `data/bank-full.csv`, se saca de `bank+marketing.zip` de la Primera actividad. La exposición está en `exposicion_bank.pptx` y su PDF en `exposicion_bank.pdf`.

Para regenerar figuras, mlx y presentación desde la carpeta

```matlab
addpath('herramientas'); generar
```

```bash
python herramientas/hacer_pptx.py
python herramientas/pptx_a_pdf.py
```
