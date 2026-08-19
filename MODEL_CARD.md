# Model card - Clasificador experimental de régimen oncológico

## Estado y decisión

- Versión evaluada: 1.0.0, agosto de 2026.
- Estado: prueba de concepto académica.
- Decisión de avance: **NO-GO clínico**.
- Motivo: no se demuestra rendimiento superior al azar ni a los baselines.

## Modelo y objetivo

- Algoritmo seleccionado: Random Forest dentro de un `Pipeline` de scikit-learn.
- Objetivo computacional: clasificar `chemotherapy_regimen`, la etiqueta históricamente registrada.
- Clases: ABVD, CHOP, FOLFOX y Gemcitabine.
- Entradas: edad, sexo, IMC, tabaquismo, tipo de cáncer, mutación, estadio, tamaño tumoral y metástasis.
- Exclusiones: identificadores, variables redundantes y toda variable posterior a la decisión terapéutica.

La etiqueta observada no representa necesariamente el tratamiento óptimo. El modelo no estima eficacia, toxicidad, supervivencia, efecto causal ni costo-efectividad.

## Evaluación

- Holdout estratificado: 25 %, semilla 42.
- Selección: validación cruzada repetida de 5 folds por 2 repeticiones, solo dentro de train.
- F1 macro CV Random Forest: 0,2521.
- F1 macro CV Dummy estratificado: 0,2525.
- Diferencia pareada: -0,0004; IC 95 % [-0,0064; 0,0050]; Wilcoxon p = 0,9219.
- F1 macro holdout: 0,2496; IC bootstrap 95 % [0,2420; 0,2568].
- Balanced accuracy holdout: 0,2499; IC 95 % [0,2422; 0,2571].
- Prueba de aleatorización de etiquetas: p unilateral = 0,4991 con 5.000 permutaciones.
- Brier skill frente al baseline de prevalencia: -0,0118.
- Ganancia de log-loss frente a prevalencia: -0,0170.
- F1 final de la curva de aprendizaje: 0,2500.

Las pruebas convergen en la misma conclusión: el clasificador no contiene señal generalizable útil.

## Incertidumbre y abstención

La interfaz utiliza 0,45 como umbral ilustrativo de seguridad. No es un umbral clínicamente optimizado. En el holdout produce 100 % de abstención, coherente con probabilidades próximas a las prevalencias y con la ausencia de discriminación.

## Uso previsto

- Docencia de pipelines, evaluación multiclase y prevención de fuga de información.
- Auditoría metodológica de un resultado negativo.
- Demostración de una interfaz con incertidumbre, controles y abstención.

## Uso prohibido

- Recomendar, prescribir, priorizar o descartar tratamientos.
- Introducir datos de pacientes reales.
- Comparar eficacia, seguridad o supervivencia entre regímenes.
- Tomar decisiones de cobertura, financiación o asignación de recursos.
- Integrar el artefacto en sistemas asistenciales.

## Datos y riesgos

El CSV bruto incluido coincide byte a byte con la versión 1 publicada en
Kaggle y la licencia indicada es Apache 2.0. Sin embargo, su procedencia clínica
no está documentada: faltan institución, protocolo, criterios de inclusión,
aprobación ética y mecanismo de generación. Los principales riesgos son falta
de representatividad, objetivo no causal, combinaciones clínicas atípicas,
falsa certeza y uso fuera de dominio.

## Condiciones mínimas para reconsiderar el NO-GO

1. Cohorte trazable y autorización de uso.
2. Caso de uso restringido a tumor, línea terapéutica y alternativas plausibles.
3. Objetivo clínico validado por especialistas.
4. Protocolo previo con baselines y umbrales de utilidad.
5. Validación temporal y externa.
6. Calibración, análisis por subgrupos, seguridad y evaluación prospectiva.
