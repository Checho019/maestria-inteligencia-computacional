# Algoritmo genético binario con interfaz gráfica

Entrega de la tarea de algoritmos genéticos de Inteligencia Computacional Aplicada.

| Carpeta o archivo | Contenido |
|---|---|
| `AlgoritmoGenetico.exe` | La aplicación lista para usar en Windows, sin instalar nada. Se abre con doble clic |
| `ag_app/` | Código fuente de la aplicación (motor del AG e interfaz en PySide6). Su `README.md` explica la instalación y la ejecución |
| `experimentos/` | Guiones de los experimentos E1, E2 y E3 y sus resultados en CSV |
| `informe/` | Fuente LaTeX del informe, figuras y guion de las capturas de la interfaz |

## Ejecutar la aplicación

En Windows, después de descomprimir la entrega, basta con abrir `AlgoritmoGenetico.exe` con doble clic. Es un solo archivo que trae Python y las bibliotecas, y tarda unos segundos en abrir la primera vez porque se descomprime en una carpeta temporal. Si Windows muestra el aviso de SmartScreen, se elige "Más información" y "Ejecutar de todas formas", porque el ejecutable no está firmado.

En cualquier sistema con Python 3.10 o posterior:

```bash
cd ag_app
pip install -r requirements.txt
python main.py
```

## Repetir los experimentos

Los experimentos usan el mismo motor que la aplicación, con las semillas 1 a 10.

```bash
cd experimentos
pip install -r ../ag_app/requirements.txt pandas scipy
python ejecutar_experimentos.py
python analizar_resultados.py
```

`ejecutar_experimentos.py` escribe `resultados/ejecuciones.csv` (una fila por ejecución) y `resultados/curvas.csv` (mejor, media, peor y diversidad por generación). `analizar_resultados.py` calcula las métricas de la tabla del informe (`resultados/metricas.csv`), las pruebas estadísticas, revisa las ejecuciones sin éxito (`resultados/estancamientos.csv`) y regenera la figura de convergencia, la tabla y las cifras que cita el informe en `informe/`. Las capturas de la interfaz se regeneran con `python capturar_interfaz.py` desde `informe/`.
