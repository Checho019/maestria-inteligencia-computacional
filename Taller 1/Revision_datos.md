# Taller 1. Revisión de los datos antes de la red

Inteligencia Computacional. Datasets del taller: Iris y banknote.

Antes de entrenar el perceptrón y el Adaline hay que mirar con qué datos se va a trabajar. Para cada dataset se hace lo mismo: se mira el dato crudo, se corrige por pasos, y después de cada paso se entrenan todos los modelos de Classification Learner para ver si mejoran. Los scripts `R1_revision_iris.mlx` y `R2_revision_banknote.mlx` dejan en el workspace una tabla por paso: `T0_crudo`, `T1_outliers`, `T2_balanceado`, `T3_estandarizado` y `T4_normalizado`.

## 1. Iris

150 flores, cuatro medidas en centímetros (largo y ancho del sépalo, largo y ancho del pétalo) y la especie: setosa, versicolor o virginica.

### 1.1 Dato crudo

![Histogramas por clase](informe/figuras/rev_iris_histogramas.png)
*Las medidas del pétalo separan setosa de las otras dos sin ayuda. Las del sépalo se pisan más.*

![Boxplot crudo](informe/figuras/rev_iris_boxplot_crudo.png)
*Las cuatro están en centímetros y en rangos parecidos, entre 0 y 8. No hay una que domine a las demás por escala.*

![Balance de clases](informe/figuras/rev_iris_balance.png)
*50 de cada clase. Ya viene balanceado.*

![Dispersión](informe/figuras/rev_iris_dispersion.png)
*Largo contra ancho del pétalo. Setosa queda sola abajo a la izquierda; versicolor y virginica se traslapan en la frontera.*

Modelos con el dato crudo:

[PANTALLAZO Classification Learner con T0_crudo]

| Mejor modelo | Exactitud |
|---|---|
| | |

### 1.2 Corrigiendo outliers

Regla del 1,5 por rango intercuartil, recortando al borde en vez de borrar la fila. Solo el ancho del sépalo tenía unos pocos valores fuera.

![Boxplot sin outliers](informe/figuras/rev_iris_boxplot_outliers.png)
*Casi igual al crudo. En Iris este paso no cambia nada.*

[PANTALLAZO Classification Learner con T1_outliers]

| Mejor modelo | Exactitud | Cambió respecto al paso anterior |
|---|---|---|
| | | |

### 1.3 Balanceando las clases

No hay nada que balancear, son 50, 50 y 50. La tabla `T2_balanceado` es la misma que `T1_outliers` y se deja con ese nombre para seguir el orden.

### 1.4 Estandarizando

![Boxplot estandarizado](informe/figuras/rev_iris_boxplot_estandarizado.png)
*Media 0 y desviación 1 en las cuatro.*

[PANTALLAZO Classification Learner con T3_estandarizado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 1.5 Normalizando

![Boxplot normalizado](informe/figuras/rev_iris_boxplot_normalizado.png)
*Todo entre 0 y 1.*

[PANTALLAZO Classification Learner con T4_normalizado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 1.6 Qué pasó en Iris

| Paso | Filas | Mejor modelo | Exactitud |
|---|---|---|---|
| Crudo | 150 | | |
| Sin outliers | 150 | | |
| Balanceado | 150 | igual al anterior | |
| Estandarizado | 150 | | |
| Normalizado | 150 | | |

Dos o tres frases sobre cuál paso ayudó y cuál no.

## 2. Banknote

1372 billetes. A cada uno le tomaron una foto, le aplicaron una transformada wavelet y de ahí sacaron cuatro números que describen la textura: varianza, asimetría, curtosis y entropía. La clase es si el billete es auténtico o falso.

### 2.1 Dato crudo

![Histogramas por clase](informe/figuras/rev_banknote_histogramas.png)
*La varianza separa bastante: los falsos se concentran en valores negativos. La entropía casi no distingue.*

![Boxplot crudo](informe/figuras/rev_banknote_boxplot_crudo.png)
*Cuatro escalas distintas. La curtosis llega a 18 y la entropía no pasa de 2,5. Aquí sí va a importar escalar.*

![Balance de clases](informe/figuras/rev_banknote_balance.png)
*762 auténticos y 610 falsos. Desbalance suave.*

![Dispersión](informe/figuras/rev_banknote_dispersion.png)
*Varianza contra asimetría. Con solo esas dos ya casi se separan.*

[PANTALLAZO Classification Learner con T0_crudo]

| Mejor modelo | Exactitud |
|---|---|
| | |

### 2.2 Corrigiendo outliers

Regla del 1,5 por rango intercuartil, recortando al borde.

![Boxplot sin outliers](informe/figuras/rev_banknote_boxplot_outliers.png)
*Se recortan las colas de la curtosis y la entropía.*

[PANTALLAZO Classification Learner con T1_outliers]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 2.3 Balanceando las clases

Se toman 610 auténticos al azar para igualar a los 610 falsos. Quedan 1220 filas.

![Balance después](informe/figuras/rev_banknote_balance_despues.png)
*610 y 610.*

[PANTALLAZO Classification Learner con T2_balanceado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 2.4 Estandarizando

![Boxplot estandarizado](informe/figuras/rev_banknote_boxplot_estandarizado.png)
*Ahora las cuatro se comparan.*

[PANTALLAZO Classification Learner con T3_estandarizado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 2.5 Normalizando

![Boxplot normalizado](informe/figuras/rev_banknote_boxplot_normalizado.png)
*Todo entre 0 y 1.*

[PANTALLAZO Classification Learner con T4_normalizado]

| Mejor modelo | Exactitud | Cambió |
|---|---|---|
| | | |

### 2.6 Qué pasó en banknote

| Paso | Filas | Mejor modelo | Exactitud |
|---|---|---|---|
| Crudo | 1372 | | |
| Sin outliers | 1372 | | |
| Balanceado | 1220 | | |
| Estandarizado | 1220 | | |
| Normalizado | 1220 | | |

Dos o tres frases.

## 3. Conclusión

Qué paso sirvió más en cada dataset y por qué. Un párrafo.
