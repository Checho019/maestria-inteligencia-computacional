# Inteligencia Computacional

Trabajos del curso de Inteligencia Computacional, segundo semestre de maestría. Todo está hecho en MATLAB R2026a con la Statistics and Machine Learning Toolbox, y todo es reproducible con una semilla fija.

## Primera actividad. Revisión estadística de variables en datasets de clasificación

Se toman dos datasets del repositorio UCI, se les aplican las pruebas estadísticas que corresponden según su tamaño y la naturaleza de sus variables, y se mide cómo cambia el desempeño de cinco clasificadores a medida que se van corrigiendo los datos.

| Dataset | Registros | Predictoras | Clase | Desbalance |
|---|---|---|---|---|
| [Ecoli](https://archive.ics.uci.edu/dataset/39/ecoli) | 336 | 7 continuas y binarias | 8 niveles | 71,5 a 1 |
| [Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing) | 45.211 | 7 numéricas y 9 categóricas | binaria | 7,55 a 1 |

La cadena de corrección es la misma en los dos casos. Se parte del dataset crudo, se corrigen atípicos y variables mal codificadas, se balancea la clase, y sobre el resultado se prueban dos ramas alternativas de escalado, estandarización y normalización, más una última etapa de selección de variables. Cada una de esas seis versiones se guarda en un CSV listo para abrir en Classification Learner.

### Resultados principales

**Balancear antes de particionar solo infla las métricas cuando el método sintetiza datos.** En Ecoli, aplicar SMOTE sobre el dataset completo y después validar sube la exactitud balanceada 7,4 puntos de promedio, y hasta 10,4 en el KNN. En Bank, aplicar submuestreo aleatorio antes de particionar no la mueve nada, 0,000 de promedio. La diferencia está en que SMOTE construye puntos interpolando vecinos que van a terminar en el bloque de prueba, mientras que recortar filas no crea información nueva.

**El escalado le sirve a unos modelos y a otros no.** En Bank el KNN gana 8,7 puntos al estandarizar y la regresión logística 2,6, mientras que el árbol y el LDA no se mueven ni una milésima. En Ecoli no gana nadie, porque las variables ya venían entre 0 y 1 de fábrica.

**Varios pasos de corrección no sirvieron, y quedan reportados igual.** Corregir atípicos en Ecoli no cambió nada. La selección de variables empeoró los dos datasets. La distancia de Mahalanobis marcó el 30,4 por ciento de Ecoli como atípico, que como criterio de limpieza es inservible. Y la regresión logística sobre Bank crudo predice "no" para los 45.211 clientes con una exactitud de 0,883 que parece buena y no lo es.

### Cómo correrlo

Hay que descomprimir los dos zip dentro de `Primera actividad/data` de modo que queden `data/ecoli/ecoli.data` y `data/bank/bank-full.csv`. Después, desde MATLAB, con la carpeta `codigo` como directorio de trabajo:

```matlab
run_todo
```

Tarda unos 17 minutos. Genera los dos libros de Excel, las 43 figuras y los 12 CSV de etapas. Usa semilla fija en todo, así que los números salen idénticos en cada corrida.

Para pasar los informes de Markdown a Word hace falta Python con `python-docx`:

```bash
python codigo/md_a_docx.py
```

### Qué hay en cada carpeta

```
Primera actividad/
  Informe_Ecoli.md, .docx, .pdf             informe completo del primer dataset
  Informe_Bank.md, .docx, .pdf              informe completo del segundo
  TECNICO_Ecoli.md, .docx, .pdf             recorrido del codigo paso por paso
  TECNICO_Bank.md, .docx, .pdf              lo mismo para el segundo dataset
  Resultados_Ecoli.xlsx                     26 hojas, una por prueba estadística
  Resultados_Bank.xlsx                      24 hojas
  bank+marketing.zip, ecoli.zip             los datos originales tal como vienen de UCI
  codigo/
    run_todo.m                              corre los 10 scripts en orden
    paso0_validar_pruebas.m                 valida por simulación las funciones propias
    paso1_exploracion_*.m                   carga, tipificación, descriptivos, gráficos
    paso2_pruebas_*.m                       normalidad, varianzas, comparación, correlación, relevancia, atípicos
    paso3_etapas_*.m                        construye las seis versiones del dataset
    paso4_modelos_*.m                       entrena y valida, directa y honesta
    paso5_resumen.m                         bitácora de etapas y figuras de cierre
    md_a_docx.py                            convierte los informes a Word
    funciones/                              las diez funciones auxiliares
  resultados/
    validacion/                             figuras de la validación de las pruebas propias
    ecoli/figuras, bank/figuras             43 PNG
    ecoli/etapas, bank/etapas               los CSV para Classification Learner
```

Los CSV de etapas y los `.mat` intermedios no están versionados porque pesan 22 MB y se regeneran corriendo `run_todo`. Las carpetas de datos descomprimidos tampoco, por lo mismo.

Los dos documentos `TECNICO_` son distintos de los informes. Los informes cuentan qué se hizo con los datos y qué salió. Los técnicos cuentan qué hace el código: el diagrama del pipeline con qué script produce qué archivo, el recorrido bloque por bloque con nombres y dimensiones reales de cada variable, el algoritmo de cada función auxiliar, los puntos donde el código se rompe si se toca, y una tabla de recetas para modificarlo. Van en horizontal porque sus tablas tienen seis columnas.

### Funciones que hubo que programar

MATLAB no trae varias de las pruebas que pide la guía del curso, así que están implementadas en `codigo/funciones`.

| Archivo | Qué hace |
|---|---|
| `swtest.m` | Prueba de normalidad de Shapiro Wilk, con el algoritmo de Royston |
| `dagostino_k2.m` | Prueba de normalidad de D'Agostino Pearson K cuadrado |
| `cramersv.m` | Chi cuadrado de independencia más V de Cramér |
| `calcular_vif.m` | Factor de inflación de la varianza |
| `tratar_outliers.m` | Winsorización o eliminación por la regla de 1,5 por IQR, con protección para el caso de IQR igual a cero |
| `smote_simple.m` | SMOTE básico por interpolación con k vecinos |
| `balancear.m` | SMOTE, sobremuestreo con reemplazo o submuestreo aleatorio |
| `metricas_clf.m` | Exactitud, exactitud balanceada, F1 macro, kappa de Cohen, recall y precisión de la clase positiva |
| `evaluar_cv.m` | Validación cruzada manual que aplica balanceo y escalado solo dentro del bloque de entrenamiento |
| `guardar_fig.m` | Exporta la figura a PNG con fondo blanco |

Las dos pruebas de normalidad se validaron por simulación dentro de MATLAB, sin comparar contra ninguna otra herramienta. Con 2000 repeticiones sobre datos que sí son normales, `swtest` rechaza entre 5,05 y 5,65 por ciento cuando debería rechazar 5, y `dagostino_k2` entre 5,30 y 6,00 por ciento, indistinguible de `lillietest` y `adtest` que sí son nativas. El detalle está en la primera sección de los dos informes.

## Requisitos

MATLAB R2026a o posterior con Statistics and Machine Learning Toolbox. Para la conversión a Word, Python 3 con `python-docx`, que es opcional porque los informes también están en Markdown.

## Nota sobre los datos

Los dos datasets son públicos y vienen del [UCI Machine Learning Repository](https://archive.ics.uci.edu/). Los zip incluidos son los originales sin modificar. Ecoli fue donado por Paul Horton y Kenta Nakai. Bank Marketing fue donado por Sérgio Moro, Paulo Cortez y Paulo Rita.

El PDF con la guía de pruebas estadísticas del curso y el syllabus no se incluyen en este repositorio porque son material del docente.
