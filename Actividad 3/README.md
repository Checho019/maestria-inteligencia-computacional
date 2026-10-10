# Actividad 3. Aprendizaje profundo

Cinco puntos del aula. Cada carpeta corresponde a un entregable, y lo que se sube está en su subcarpeta `entrega/`. Todo se entrega en el punto 5 del aula antes del 13 de octubre.

| Carpeta | Punto | Qué se entrega |
|---|---|---|
| `1 Quiz videos` | 1, videos de 3Blue1Brown | el cuestionario en Google Forms, se responde en línea |
| `2 Onramp` | 2, curso Deep Learning Onramp de MATLAB | el certificado de progreso al 100 % |
| `3 Taller resuelto` | 3, ejecutar y analizar el cuaderno resuelto | `entrega/Informe_TallerResuelto_SergioDuarte.pdf` |
| `4 Taller propuesto` | 4, resolver el cuaderno propuesto | `entrega/Informe_TallerPropuesto_SergioDuarte.pdf` y `entrega/TallerPropuesto_KMNIST_SergioDuarte.ipynb` |

Los cuadernos se ejecutaron con PyTorch 2.12 y CUDA en local. KMNIST se descargó con curl desde el servidor de CODH porque Python no validaba su certificado, y torchvision verificó los cuatro archivos con su MD5. Los datos quedan en `datos/` dentro de cada taller y no se versionan.
