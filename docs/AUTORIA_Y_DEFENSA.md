# Autoría, trazabilidad y preparación de la defensa

Este documento no sustituye la declaración institucional de autoría. Su
finalidad es ayudar al estudiante a comprobar que puede explicar y defender el
trabajo publicado. La autoría no se demuestra ocultando herramientas, sino
comprendiendo las decisiones, verificando los resultados y declarando con
exactitud la asistencia recibida.

## Comprobaciones personales antes del depósito

El autor debe poder realizar sin ayuda externa estas acciones:

1. Explicar por qué la variable objetivo es el régimen histórico registrado y no
   el tratamiento óptimo para un paciente.
2. Identificar los nueve predictores pretratamiento y justificar la exclusión de
   dosis, ciclos, toxicidad, respuesta y supervivencia por riesgo de leakage.
3. Explicar la diferencia entre validación cruzada dentro de train, holdout
   interno y validación externa.
4. Ejecutar `python run_all.py`, `python -m pytest -q` y
   `python tools/verify_repository.py`, e interpretar cualquier fallo.
5. Justificar F1 macro y balanced accuracy en un problema multiclase y comparar
   Random Forest con los dos baselines Dummy.
6. Explicar por qué F1 macro cercano a 0,25, p de aleatorización 0,4991 y skill
   probabilístico negativo conducen a una decisión NO-GO.
7. Demostrar que la aplicación se abstiene y que sus probabilidades no son una
   recomendación ni una estimación de beneficio causal.
8. Distinguir la procedencia técnica verificada del archivo de su procedencia
   clínica no acreditada.
9. Describir qué datos, aprobaciones y validaciones harían falta antes de un
   posible estudio hospitalario.
10. Confirmar que el registro de herramientas de IA coincide con el uso real y
    con la declaración incluida en la memoria.

## Respuesta central ante el tribunal

> El modelo no está validado clínicamente. El resultado responsable fue impedir
> que una probabilidad cercana al azar se convirtiera en recomendación. La
> contribución del TFM es el pipeline reproducible, la auditoría de señal, la
> prevención de leakage, la trazabilidad y la abstención segura.

## Límite de la declaración

La ejecución correcta del repositorio acredita reproducibilidad técnica, no
autoría intelectual por sí sola. Antes del depósito, el estudiante debe releer
la memoria, confirmar las herramientas realmente utilizadas y conservar la
evidencia exigida por la normativa de su universidad.
