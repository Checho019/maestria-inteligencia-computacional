# Actividad 1. Revisión de datos y modelos en Classification Learner

Inteligencia Computacional. Datasets Ecoli y Bank Marketing de UCI.

Para cada dataset se hace lo mismo: se mira el dato tal como viene, se corrige por pasos, y después de cada paso se entrenan todos los modelos de Classification Learner para ver si mejoran. Los scripts `ecoli_pasos.mlx` y `bank_pasos.mlx` dejan en el workspace una tabla por paso.

## 1. Ecoli

336 proteínas de E. coli, 7 medidas numéricas entre 0 y 1, y la clase es el sitio de la célula donde queda la proteína (8 clases).

### 1.1 Dato crudo

Qué se ve en las gráficas:

[PANTALLAZO histogramas y boxplot crudo]

La clase está muy desbalanceada. cp tiene 143 muestras y hay tres clases con 5, 2 y 2.

[PANTALLAZO balance de clases]

Modelos con el dato crudo:

[PANTALLAZO Classification Learner con T0_crudo]

| Mejor modelo | Exactitud |
|---|---|
| | |

### 1.2 Corrigiendo outliers

Se quitó `chg` porque vale 0,5 en 335 de las 336 filas. En las demás se recortó lo que se salía de 1,5 veces el rango intercuartil: 13 valores en `gvh` y 9 en `aac`.

[PANTALLAZO boxplot sin outliers]

[PANTALLAZO Classification Learner con T1_outliers]

| Mejor modelo | Exactitud | Cambió respecto al paso anterior |
|---|---|---|
| | | |

### 1.3 Balanceando las clases

Se quitaron las tres clases con menos de 10 muestras porque no hay con qué aprenderlas, y las cinco que quedan se igualaron a 143 repitiendo filas al azar. Quedan 715 filas.

[PANTALLAZO balance después]

[PANTALLAZO Classification Learner con T2_balanceado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 1.4 Estandarizando

[PANTALLAZO Classification Learner con T3_estandarizado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 1.5 Normalizando

[PANTALLAZO Classification Learner con T4_normalizado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 1.6 Qué pasó en Ecoli

| Paso | Filas | Clases | Mejor modelo | Exactitud |
|---|---|---|---|---|
| Crudo | 336 | 8 | | |
| Sin outliers | 336 | 8 | | |
| Balanceado | 715 | 5 | | |
| Estandarizado | 715 | 5 | | |
| Normalizado | 715 | 5 | | |

Dos o tres frases sobre cuál paso ayudó y cuál no.

## 2. Bank Marketing

4521 clientes de un banco (la muestra del 10 % del dataset). 16 variables, 7 numéricas y 9 de texto, y la clase es si el cliente contrató el depósito o no.

### 2.1 Dato crudo

[PANTALLAZO histogramas y boxplots crudo]

4000 dicen que no y 521 que sí. Un modelo que diga siempre "no" acierta el 88 %, así que la exactitud sola engaña.

[PANTALLAZO balance de clases]

[PANTALLAZO Classification Learner con T0_crudo]

| Mejor modelo | Exactitud |
|---|---|
| | |

### 2.2 Corrigiendo outliers y variables raras

Se quitó `duration` porque es la duración de la llamada y eso solo se sabe después de llamar. `pdays` vale −1 cuando nunca han llamado al cliente, así que se pasó a una variable sí/no. Las de cola larga se recortaron al 1,5 del rango intercuartil.

[PANTALLAZO boxplots sin outliers]

[PANTALLAZO Classification Learner con T1_outliers]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 2.3 Balanceando las clases

Se tomaron 521 "no" al azar para igualar a los 521 "sí". Quedan 1042 filas.

[PANTALLAZO balance después]

[PANTALLAZO Classification Learner con T2_balanceado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 2.4 Estandarizando

[PANTALLAZO Classification Learner con T3_estandarizado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 2.5 Normalizando

[PANTALLAZO Classification Learner con T4_normalizado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 2.6 Qué pasó en Bank

| Paso | Filas | Mejor modelo | Exactitud |
|---|---|---|---|
| Crudo | 4521 | | |
| Sin outliers | 4521 | | |
| Balanceado | 1042 | | |
| Estandarizado | 1042 | | |
| Normalizado | 1042 | | |

Dos o tres frases.

## 3. Conclusión

Qué paso sirvió más en cada dataset y por qué. Un párrafo.
