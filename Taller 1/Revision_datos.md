# Taller 1. Revisión de los datos y su efecto sobre el perceptrón y el Adaline

Inteligencia Computacional. El taller trabaja sobre dos conjuntos de datos, Iris y banknote.

Antes de entrenar la neurona se examina el conjunto de datos con el que se va a trabajar. El procedimiento es el mismo para los dos. Se observa el dato crudo, se corrige por pasos sucesivos, y sobre cada versión resultante se entrena el perceptrón y el Adaline del taller, con el fin de determinar qué paso del procesamiento beneficia a la red y cuál resulta indiferente. Los scripts `R1_revision_iris.m` y `R2_revision_banknote.m` realizan la revisión y producen cinco tablas, `T0_crudo`, `T1_outliers`, `T2_balanceado`, `T3_estandarizado` y `T4_normalizado`. El script `R3_modelos_por_paso.m` entrena los dos modelos sobre cada una de ellas. La partición en 70 por ciento de entrenamiento y 30 por ciento de prueba se genera con la semilla 2021 y los pesos iniciales de ambos modelos con la semilla 1, de manera que todos los pasos se comparan sobre la misma división y el mismo punto de partida. El perceptrón emplea la regla 3, factor de aprendizaje 0,1, umbral cero, salida codificada en menos uno y uno, y un tope de 200 épocas. El Adaline emplea factor de aprendizaje 0,01, umbral de clasificación 0,5, salida codificada en cero y uno, y un tope de 500 épocas. En las tablas, una cifra de épocas igual al tope indica que el entrenamiento no se detuvo por su propio criterio.

## 1. Los pasos de corrección

Sobre el dato crudo se aplican cuatro correcciones. La corrección de atípicos identifica los valores que se alejan más de 1,5 veces el rango intercuartil por debajo del primer cuartil o por encima del tercero, siguiendo el criterio propuesto por Tukey para el diagrama de caja (Tukey, 1977), y los recorta al borde de ese intervalo en lugar de eliminar la fila, con el fin de que un valor extremo aislado no arrastre las correcciones de peso. El balanceo iguala el número de casos de cada clase para que la neurona no aprenda a favorecer la clase mayoritaria por simple frecuencia. La estandarización lleva cada variable a media cero y desviación uno, y la normalización la reescala al intervalo de cero a uno. Estas dos últimas persiguen el mismo objetivo, que ninguna variable domine el ajuste solo por estar medida en una escala mayor, y por eso se aplican como alternativas y no de forma sucesiva, ambas partiendo del dato balanceado. Centrar las entradas y llevarlas a una dispersión comparable es una recomendación establecida para acelerar la convergencia del entrenamiento por descenso de gradiente (LeCun et al., 1998).

El escalado se calculó sobre el conjunto completo antes de separar entrenamiento y prueba, de modo que las medias y los rangos empleados incorporan también las filas de prueba. En un montaje riguroso esos parámetros se estiman solo con el conjunto de entrenamiento, y se deja constancia de la diferencia porque el objetivo aquí es comparar el efecto de cada paso y no estimar el desempeño con la mayor fidelidad posible.

## 2. Iris

150 flores, cuatro medidas en centímetros (largo y ancho del sépalo, largo y ancho del pétalo) y la especie, que puede ser setosa, versicolor o virginica.

### 2.1 Cómo viene el dato

| Variable | Mínimo | Máximo | Media | Desviación | Valores fuera de 1,5 RIC |
|---|---|---|---|---|---|
| largo del sépalo | 4,30 | 7,90 | 5,84 | 0,83 | 0 |
| ancho del sépalo | 2,00 | 4,40 | 3,06 | 0,44 | 4 |
| largo del pétalo | 1,00 | 6,90 | 3,76 | 1,77 | 0 |
| ancho del pétalo | 0,10 | 2,50 | 1,20 | 0,76 | 0 |

Ninguna de las 150 filas presenta valores faltantes, de modo que no fue necesario imputar ni descartar registros.

![Histogramas por clase](informe/figuras/rev_iris_histogramas.png)
*Las medidas del pétalo separan setosa de las otras dos especies por sí solas. Las del sépalo presentan un traslape mayor entre clases.*

![Boxplot crudo](informe/figuras/rev_iris_boxplot_crudo.png)
*Las cuatro están en centímetros y en rangos parecidos, entre 0 y 8. No hay una que domine a las demás por escala.*

![Balance de clases](informe/figuras/rev_iris_balance.png)
*50 de cada clase. El conjunto ya viene balanceado.*

![Dispersión](informe/figuras/rev_iris_dispersion.png)
*Largo contra ancho del pétalo. Setosa queda aislada abajo a la izquierda. Versicolor y virginica se traslapan en la frontera.*

### 2.2 Efecto de cada paso sobre el dato

La corrección de atípicos solo alcanza a 4 valores del ancho del sépalo y el boxplot resultante es prácticamente igual al del dato crudo. El balanceo no tiene nada que hacer, ya que hay 50 flores de cada clase, y `T2_balanceado` coincide con `T1_outliers`. La estandarización y la normalización cambian las unidades pero no la forma de las distribuciones, porque las cuatro variables ya estaban en escalas comparables.

![Boxplot estandarizado](informe/figuras/rev_iris_boxplot_estandarizado.png)
*Tras la estandarización las cuatro medidas quedan con media 0 y desviación 1.*

### 2.3 Perceptrón y Adaline sobre cada versión

La neurona es una sola, así que se arman dos problemas de dos clases. El problema A es setosa contra las otras dos, que se separa con una recta. El problema B es versicolor contra virginica, que no se separa del todo. La exactitud se mide en el 30 por ciento de prueba, 45 flores en A y 30 en B.

| Problema | Paso | Perceptrón, épocas | Perceptrón, exactitud | Adaline, épocas | Adaline, exactitud |
|---|---|---|---|---|---|
| A | crudo | 2 | 100 % | 372 | 100 % |
| A | sin outliers | 2 | 100 % | 346 | 100 % |
| A | balanceado | 2 | 100 % | 346 | 100 % |
| A | estandarizado | 2 | 100 % | 40 | 100 % |
| A | normalizado | 4 | 100 % | 500 | 100 % |
| B | crudo | 200 | 100 % | 500 | 93,3 % |
| B | sin outliers | 200 | 100 % | 500 | 93,3 % |
| B | balanceado | 200 | 100 % | 500 | 93,3 % |
| B | estandarizado | 200 | 96,7 % | 211 | 100 % |
| B | normalizado | 200 | 90,0 % | 500 | 100 % |

![Exactitud por paso en Iris](informe/figuras/rev_iris_modelos.png)
*Perceptrón y Adaline sobre las cinco versiones de Iris.*

**Resultados.** En el problema A los dos modelos alcanzan el 100 por ciento de exactitud en las cinco versiones del dato. El perceptrón converge en 2 épocas y ese número no varía con ningún paso del procesamiento. Sobre el Adaline el escalado no modifica la exactitud, pero sí el número de épocas que transcurren hasta que el error cuadrático deja de cambiar. Con el dato crudo se requieren 372 épocas y con el dato estandarizado 40. El comportamiento se explica por la regla delta, en la que la corrección de cada peso es proporcional al valor de la entrada correspondiente. Al estar las cuatro medidas centradas en cero y con dispersión comparable, las correcciones tienen magnitudes similares entre variables y el error desciende de forma más regular. La versión normalizada, en cambio, agota el tope de 500 épocas sin que el error deje de descender, porque al comprimir las entradas al intervalo de cero a uno cada corrección es de menor magnitud y el mismo factor de aprendizaje avanza más despacio.

En el problema B el perceptrón no converge y agota las 200 épocas en las cinco versiones, dado que versicolor y virginica no admiten una separación lineal exacta. Aun así clasifica correctamente las 30 flores de prueba con el dato crudo, y desciende a 96,7 y 90 por ciento con el dato estandarizado y normalizado. Ese 100 por ciento admite una lectura matizada. Al no haber convergencia, los pesos finales corresponden a la última corrección aplicada dentro de la época 200, de modo que el resultado sobre 30 flores de prueba depende del estado particular en que el entrenamiento quedó interrumpido y no de una solución estable. El Adaline muestra el comportamiento inverso. Obtiene 93,3 por ciento con el dato crudo y 100 por ciento con el dato escalado, y con el dato estandarizado el error cuadrático se estabiliza en 211 épocas, por debajo del tope de 500.

## 3. Banknote

El conjunto reúne 1372 billetes. De cada uno se obtuvo una imagen digitalizada a la que se aplicó una transformada wavelet, y de los coeficientes resultantes se derivaron cuatro descriptores de textura, la varianza, la asimetría, la curtosis y la entropía. La variable de clase indica si el billete es auténtico o falso.

### 3.1 Cómo viene el dato

| Variable | Mínimo | Máximo | Media | Desviación | Valores fuera de 1,5 RIC |
|---|---|---|---|---|---|
| varianza | −7,04 | 6,82 | 0,43 | 2,84 | 0 |
| asimetría | −13,77 | 12,95 | 1,92 | 5,87 | 0 |
| curtosis | −5,29 | 17,93 | 1,40 | 4,31 | 57 |
| entropía | −8,55 | 2,45 | −1,19 | 2,10 | 33 |

Las 1372 filas están completas y no se detectaron valores faltantes en ninguna de las cuatro variables.

![Histogramas por clase](informe/figuras/rev_banknote_histogramas.png)
*La varianza discrimina apreciablemente entre las dos clases y los billetes falsos se concentran en valores negativos. La entropía apenas aporta separación.*

![Boxplot crudo](informe/figuras/rev_banknote_boxplot_crudo.png)
*Cuatro escalas distintas. La curtosis llega a 18 y la entropía no pasa de 2,5.*

![Balance de clases](informe/figuras/rev_banknote_balance.png)
*La distribución es de 762 billetes auténticos frente a 610 falsos, un desbalance moderado.*

![Dispersión](informe/figuras/rev_banknote_dispersion.png)
*Varianza contra asimetría. Las dos nubes están separadas, pero la línea que las divide no es recta.*

### 3.2 Efecto de cada paso sobre el dato

El recorte de atípicos afecta las colas de la curtosis y de la entropía, que son las dos variables con valores fuera del intervalo del rango intercuartil. El balanceo toma 610 auténticos al azar para igualar a los 610 falsos, con lo que quedan 1220 filas. La estandarización lleva las cuatro variables a una escala común, y ese es el cambio visible más importante de todo el procesamiento en este conjunto.

![Boxplot sin outliers](informe/figuras/rev_banknote_boxplot_outliers.png)
*El recorte afecta las colas de la curtosis y de la entropía.*

![Boxplot estandarizado](informe/figuras/rev_banknote_boxplot_estandarizado.png)
*Tras la estandarización las cuatro variables quedan en una escala común y sus dispersiones resultan comparables.*

### 3.3 Perceptrón y Adaline sobre cada versión

La exactitud se mide en el 30 por ciento de prueba, 412 billetes en las dos primeras versiones y 366 en las balanceadas.

| Paso | Filas | Perceptrón, épocas | Perceptrón, exactitud | Adaline, épocas | Adaline, error cuadrático final | Adaline, exactitud |
|---|---|---|---|---|---|---|
| crudo | 1372 | 200 | 99,0 % | 6 | 46,8 | 97,3 % |
| sin outliers | 1372 | 200 | 98,8 % | 6 | 32,1 | 97,3 % |
| balanceado | 1220 | 43 | 98,9 % | 6 | 29,4 | 95,9 % |
| estandarizado | 1220 | 23 | 99,2 % | 7 | 13,4 | 97,5 % |
| normalizado | 1220 | 42 | 98,9 % | 161 | 13,1 | 97,3 % |

![Exactitud por paso en banknote](informe/figuras/rev_banknote_modelos.png)
*Perceptrón y Adaline sobre las cinco versiones de banknote.*

**Resultados.** La exactitud permanece prácticamente constante. El perceptrón se sitúa entre 98,8 y 99,2 por ciento y el Adaline entre 95,9 y 97,5 por ciento en las cinco versiones. Lo que varía de forma apreciable es el proceso de entrenamiento que conduce a ese resultado.

El perceptrón no converge con el dato crudo ni con el dato sin atípicos, y agota en ambos casos las 200 épocas. Con el dato balanceado converge en 43 épocas, con el estandarizado en 23 y con el normalizado en 42. La lectura es que el conjunto de entrenamiento completo no admite una separación lineal exacta dentro del tope de épocas fijado, mientras que el subconjunto que resulta de retirar 152 billetes auténticos al azar sí la admite, y la neurona encuentra el plano separador. La exactitud en prueba no cambia y se mantiene alrededor del 99 por ciento, porque los billetes que ningún plano clasifica correctamente permanecen en el conjunto de prueba, que el balanceo no altera.

Sobre el Adaline el paso determinante es el escalado, y su efecto se aprecia en el error cuadrático final, que pasa de 46,8 con el dato crudo a 13,4 con el estandarizado. Sin escalar, la curtosis, cuyos valores llegan a 18, domina las correcciones de peso y el error se estanca en un valor alto, que es el efecto previsto cuando las entradas presentan escalas muy desiguales (LeCun et al., 1998). Conviene notar que el entrenamiento se detiene cuando el error cuadrático deja de cambiar entre épocas consecutivas, no cuando alcanza un valor pequeño, de modo que las 6 épocas de las tres primeras versiones no indican una convergencia rápida sino un estancamiento temprano en un error elevado. Con el dato normalizado el error final es 13,1, equivalente al del dato estandarizado, pero se alcanza en 161 épocas frente a 7, porque al quedar todas las entradas comprimidas en el intervalo de cero a uno cada corrección tiene menor magnitud y, con el mismo factor de aprendizaje de 0,01, el descenso del error se reparte a lo largo de más épocas.

El techo de aproximadamente 99 por ciento del perceptrón se explica por la geometría del problema. El teorema de convergencia del perceptrón garantiza que, si las dos clases son linealmente separables, el entrenamiento converge en un número finito de correcciones (Novikoff, 1962). El hecho de que sobre el conjunto completo no converja dentro de las 200 épocas fijadas constituye por tanto evidencia de que no existe un plano que deje todos los billetes auténticos a un lado y todos los falsos al otro, aunque el tope de épocas impide afirmarlo de forma concluyente. La gráfica de dispersión de varianza contra asimetría de la sección 3.1 muestra dos nubes bien diferenciadas, sin regiones donde ambas clases compartan los mismos valores, pero separadas por una frontera curva que un plano no puede reproducir. Una neurona única define exclusivamente fronteras lineales, y ninguno de los cuatro pasos de procesamiento modifica esa limitación. El recorte de atípicos al borde del intervalo no traslada ningún billete al lado opuesto de la frontera, el balanceo retira filas sin alterar la forma de las nubes, y el escalado cambia las unidades pero no la geometría.

## 4. Conclusión

En ninguno de los dos conjuntos de datos el procesamiento mejoró la exactitud de forma apreciable, y ese es el resultado principal de la revisión. Iris llega balanceado, con las cuatro variables en una misma escala, y plantea un problema linealmente separable y otro que no lo es. Banknote presenta escalas heterogéneas y un desbalance moderado, pero sus clases no se superponen y la frontera que las divide es curva. En ambos casos el procesamiento sí modificó el entrenamiento. El escalado redujo en el Adaline las épocas de 372 a 40 en Iris y el error cuadrático final de 46,8 a 13,4 en banknote, y el balanceo permitió que el perceptrón convergiera en banknote cuando con el conjunto completo no lo hacía. La exactitud final se mantiene porque el límite no proviene de la calidad del dato sino de la capacidad del modelo. Una neurona única define una única frontera lineal, y allí donde las clases no admiten una separación lineal ningún paso de preparación del dato compensa esa restricción.

## Referencias

LeCun, Y., Bottou, L., Orr, G. B. y Müller, K. R. (1998). Efficient BackProp. En G. B. Orr y K. R. Müller (Eds.), *Neural Networks: Tricks of the Trade* (Lecture Notes in Computer Science, vol. 1524, pp. 9 a 50). Springer.

Novikoff, A. B. J. (1962). On convergence proofs on perceptrons. En *Proceedings of the Symposium on the Mathematical Theory of Automata* (vol. 12, pp. 615 a 622). Polytechnic Institute of Brooklyn.

Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley.
