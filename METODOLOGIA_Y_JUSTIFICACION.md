# Metodología y justificación académica

## 1. Marco de trabajo

El estudio se estructura con CRISP-DM, siguiendo el material docente de paradigmas de minería de datos y los ejemplos Ames Housing y Super Telco Churn:

1. Comprensión del problema.
2. Comprensión de los datos.
3. Preparación del dato.
4. Modelado.
5. Evaluación.
6. Prototipo y plan de despliegue.

El problema se formula como clasificación multiclase del régimen históricamente registrado. Esto no equivale a estimar el mejor tratamiento para un paciente: para esa pregunta serían necesarios datos clínicos acreditados, comparadores, ajuste causal y validación prospectiva.

## 2. Unidad de análisis y variable objetivo

Cada fila representa un registro de paciente. La variable objetivo es `chemotherapy_regimen`, con cuatro etiquetas conocidas: ABVD, CHOP, FOLFOX y Gemcitabine. Los registros sin régimen se conservan en el dataset limpio para auditoría, pero se excluyen del modelado supervisado.

## 3. Calidad del dato

Se documentan:

- dimensiones y tipos;
- faltantes y duplicados;
- rangos de variables numéricas;
- outliers mediante IQR;
- consistencia entre estadio y metástasis;
- distribución de clases;
- asociaciones categóricas con V de Cramér corregido.

Los outliers no se eliminan automáticamente. Los materiales docentes señalan que un valor extremo puede ser error, señal o subgrupo relevante; sin conocimiento clínico y procedencia acreditada, excluirlo sería una decisión no justificable.

## 4. Prevención de data leakage

Los predictores principales son edad, sexo, IMC, tabaquismo, tipo de cáncer, mutación, estadio, tamaño tumoral y metástasis. Se excluyen:

- identificadores;
- variables derivadas redundantes;
- dosis y ciclos completados;
- náusea, neutropenia y toxicidad;
- respuesta tumoral y progresión;
- supervivencia.

Las variables excluidas ocurren después de la elección terapéutica o resumen desenlaces. Utilizarlas para predecir el régimen registrado filtraría información del futuro.

## 5. Diseño experimental

- Holdout estratificado del 25 %, congelado con semilla 42.
- Validación cruzada estratificada de 5 folds y 2 repeticiones dentro del 75 % de entrenamiento.
- Preprocesamiento encapsulado en `Pipeline` y `ColumnTransformer` para evitar que escalado y codificación aprendan del fold de validación.
- One-hot encoding para categorías y estandarización de variables numéricas.

## 6. Modelos comparados

- Dummy de clase mayoritaria.
- Dummy estratificado.
- Regresión logística multiclase como baseline interpretable.
- Árbol CART podado por profundidad y tamaño mínimo de hoja.
- Random Forest.
- Extra Trees.

La selección se basa en F1 macro medio de validación cruzada entre los modelos no Dummy. Un modelo se conserva como artefacto técnico incluso si no supera al azar; el metadato y la interfaz bloquean su interpretación clínica.

## 7. Métricas

Se reportan:

- accuracy;
- balanced accuracy;
- precision, recall y F1 macro;
- F1 ponderado;
- Matthews Correlation Coefficient;
- log-loss;
- Brier multiclase;
- top-2 accuracy;
- matriz de confusión;
- media y desviación entre folds.
- intervalos de confianza bootstrap estratificados en holdout;
- comparación pareada entre modelos sobre los mismos folds;
- calibración top-label y Expected Calibration Error;
- cobertura y rendimiento selectivo según el umbral de abstención.
- prueba de aleatorización de etiquetas en holdout;
- curva de aprendizaje dentro del conjunto de entrenamiento;
- Brier skill y ganancia de log-loss frente a un baseline de prevalencia.

Accuracy no se usa como criterio único porque FOLFOX es la clase mayoritaria. F1 macro y balanced accuracy otorgan el mismo peso a las cuatro clases. Log-loss y Brier evalúan la calidad probabilística y penalizan el exceso de confianza.

## 8. Explicabilidad y confianza

Se publica la importancia interna del modelo seleccionado, la importancia por permutación sobre el holdout y la distribución de la probabilidad máxima. La permutación cuantifica cuánto disminuye F1 macro al romper cada variable original y evita presentar la importancia interna del bosque como evidencia suficiente. Ninguna importancia se interpreta como causalidad. Si el modelo no supera baselines, tampoco se consideran fiables sus explicaciones individuales.

La aplicación utiliza un umbral de abstención del 45 %. Con probabilidades próximas a 25 %, la salida habitual es "abstención", que es la conducta correcta ante evidencia insuficiente.

El umbral se acompaña de una curva de cobertura-rendimiento. Esta curva permite comprobar si conservar solo los casos de mayor confianza mejora de forma material el resultado. Un umbral no valida el modelo por sí mismo y no debe elegirse retrospectivamente para aparentar utilidad.

## 9. Robustez y comparación estadística

El holdout se complementa con 500 réplicas bootstrap estratificadas para F1 macro, balanced accuracy, MCC, log-loss, Brier y top-2 accuracy. Los intervalos cuantifican incertidumbre muestral, pero no sustituyen una cohorte externa.

Los resultados por fold se comparan de forma pareada porque todos los modelos reciben las mismas particiones. Se reportan la diferencia media de F1, un intervalo bootstrap de la diferencia y la prueba de rangos con signo de Wilcoxon. Con solo diez pares, el contraste se interpreta con prudencia y junto con el tamaño del efecto.

La calibración top-label compara confianza máxima con acierto observado. También se calcula Expected Calibration Error como resumen descriptivo. Estas comprobaciones son técnicas y no equivalen a calibración clínica.

La prueba de aleatorización mantiene fijas las predicciones del modelo seleccionado y permuta 5.000 veces las etiquetas del holdout. Su hipótesis nula es la independencia entre predicción y etiqueta. El resultado p = 0,4991 no aporta evidencia de concordancia superior al azar. Esta prueba complementa, pero no reemplaza, la comparación pareada en validación cruzada.

La curva de aprendizaje se calcula exclusivamente dentro de train mediante tres folds y cinco tamaños de entrenamiento. Random Forest mantiene F1 de validación próximo a 0,25 mientras su F1 de entrenamiento permanece muy superior, lo que evidencia aprendizaje de particularidades no generalizables. En el tamaño máximo, F1 de validación = 0,2500.

El análisis probabilístico compara el modelo con probabilidades uniformes y con las prevalencias estimadas en train. Random Forest obtiene Brier skill = -0,0118 y ganancia de log-loss = -0,0170 frente al baseline de prevalencia; los valores negativos indican peor calidad probabilística que ese baseline.

## 10. Análisis no supervisado

Se evalúan K = 2 a 6 mediante Silhouette, Davies-Bouldin e inercia. Los clusters se proyectan con PCA y se describen por variables pretratamiento. Este análisis busca estructura geométrica, pero no demuestra que un cluster corresponda a una indicación terapéutica.

## 11. Subgrupos y outcomes

El rendimiento se desglosa por sexo y grupo de edad como control exploratorio. Los outcomes se resumen por régimen únicamente de forma descriptiva; no se comparan tratamientos causalmente porque no existe aleatorización ni ajuste de confusores.

## 12. Criterios de avance

Para evolucionar hacia un sistema clínico serían necesarios:

1. fuente y licencia verificables;
2. diccionario y protocolo de generación del dato;
3. variables clínicas y temporales relevantes;
4. cohortes externas multicéntricas;
5. calibración y análisis de utilidad clínica;
6. revisión oncológica y farmacológica;
7. aprobación ética y evaluación prospectiva;
8. trazabilidad, monitorización y gobierno del modelo.

Hasta cumplirlos, el sistema debe presentarse como demostrador académico de un pipeline de IA, no como recomendador médico.

El criterio operativo actual es **NO-GO clínico**. El umbral de 0,45 es una barrera ilustrativa de seguridad y no un punto de decisión optimizado o validado.
