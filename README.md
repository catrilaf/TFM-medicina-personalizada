# Sistema web de recomendación de tratamientos personalizados en oncología

[![Validación reproducible](https://github.com/catrilaf/TFM-medicina-personalizada/actions/workflows/ci.yml/badge.svg)](https://github.com/catrilaf/TFM-medicina-personalizada/actions/workflows/ci.yml)
[![Aplicación Streamlit](https://img.shields.io/badge/Streamlit-aplicación_pública-FF4B4B?logo=streamlit&logoColor=white)](https://tfm-medicina-personalizada.streamlit.app/)

Repositorio técnico y reproducible del Trabajo Fin de Máster en Inteligencia
Artificial Aplicada de Enrique Catrilaf González.

El proyecto estudia si nueve variables disponibles antes del tratamiento
permiten clasificar el régimen de quimioterapia registrado. Se construyó una
cadena reproducible de preparación, análisis exploratorio, prevención de fuga
de información, comparación de modelos, validación, auditorías de robustez y
una interfaz web con abstención.

> **Resultado principal: NO-GO clínico.** Ningún modelo demostró una mejora
> material frente al baseline aleatorio. La aplicación es un prototipo
> académico, no prescribe ni recomienda tratamientos y se abstiene cuando la
> confianza no supera el umbral ilustrativo. No debe utilizarse con pacientes
> reales ni para decisiones asistenciales.

La memoria final está disponible en formatos
[`DOCX`](memoria/TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.docx) y
[`PDF`](memoria/TFM_ENRIQUE_CATRILAF_ENTREGA_FINAL_VIU_2026.pdf). La versión
oficial será siempre la que el autor deposite en la plataforma universitaria.

## Revisión rápida

- [Ejecución completa: `run_all.py`](run_all.py)
- [Aplicación web: `app.py`](app.py)
- [Configuración reproducible](src/config.py)
- [Preparación y control de datos](src/preprocessing.py)
- [Modelos y validación cruzada](src/modeling.py)
- [Métricas multiclase](src/metrics.py)
- [Auditorías de robustez](src/robustness.py)
- [Lógica segura de la aplicación](src/app_logic.py)
- [Pruebas automáticas](tests/)
- [Notebook ejecutado](notebooks/01_estudio_completo_oncologia.ipynb)
- [Informe técnico HTML](reports/Estudio_Completo_Oncologia.html)
- [Índice de auditoría y correspondencia con anexos](docs/INDICE_AUDITORIA.md)
- [Ruta de revisión para la comisión](docs/REVISION_COMISION.md)
- [Matriz de cumplimiento de la pauta VIU](docs/MATRIZ_CUMPLIMIENTO_VIU.md)
- [Despliegue verificable de Streamlit](docs/DESPLIEGUE_STREAMLIT.md)
- [Registro del uso de herramientas de IA](docs/REGISTRO_USO_IA.md)
- [Comprobación personal de autoría y defensa](docs/AUTORIA_Y_DEFENSA.md)
- [Ficha del dataset](data/DATASET_CARD.md)
- [Ficha del modelo](MODEL_CARD.md)
- [Control de calidad realizado](QA_VERIFICACION.md)
- [Inventario SHA-256](MANIFEST_SHA256.csv)

## Datos y variable objetivo

El archivo original procede de Kaggle v1 y se conserva sin modificar en
[`data/raw/chemotherapy_patient_data.csv`](data/raw/chemotherapy_patient_data.csv).
La identidad se comprobó mediante SHA-256. La fuente publica una licencia
Apache 2.0, reproducida en [`data/LICENSE_DATASET.txt`](data/LICENSE_DATASET.txt).

- Archivo original: 52.321 filas y 17 variables.
- Dataset de modelado: 49.765 filas.
- Variable objetivo: `chemotherapy_regimen`.
- Predictores: edad, sexo, IMC, tabaquismo, tipo de cáncer, mutación, estadio,
  tamaño tumoral y metástasis.
- Clases: ABVD, CHOP, FOLFOX y Gemcitabine.

La coincidencia técnica con Kaggle no acredita procedencia clínica. La fuente
no identifica institución sanitaria, protocolo de recogida, aprobación ética
ni mecanismo de generación. Por ello no se afirma que los registros sean una
cohorte de pacientes reales ni que resulten clínicamente representativos.

## Modelos y validación

Se compararon:

1. Dummy de mayoría.
2. Dummy estratificado.
3. Regresión logística multinomial.
4. Árbol CART.
5. Random Forest.
6. Extra Trees.

El holdout estratificado del 25 % se separa antes del entrenamiento. La
comparación se realiza exclusivamente sobre el 75 % restante mediante
validación cruzada estratificada repetida de 5 particiones × 2 repeticiones.
El preprocesamiento queda dentro de cada `Pipeline` para impedir que el ajuste
use información de validación. El holdout queda fuera de la selección del
modelo y se utiliza después para la evaluación comparativa y auditorías post
hoc; constituye una validación interna, no externa.

Resultados de referencia:

| Indicador | Resultado |
|---|---:|
| F1 macro CV, Random Forest | 0,2521 |
| F1 macro CV, Dummy estratificado | 0,2525 |
| Diferencia pareada | −0,0004 |
| F1 macro holdout, Random Forest | 0,2496 |
| Balanced accuracy holdout | 0,2499 |
| Aleatorización de etiquetas, p unilateral | 0,4991 |
| Brier skill frente a prevalencia | −0,0118 |
| Cobertura con umbral de confianza 0,45 | 0 % |
| Abstención en holdout | 100 % |

Estas cifras describen ausencia de señal predictiva generalizable, no eficacia
clínica. Los resultados completos están en [`outputs/tables/`](outputs/tables/)
y las figuras en [`outputs/figures/`](outputs/figures/).

## Reproducción local

Requiere Python 3.12.

```bash
git clone https://github.com/catrilaf/TFM-medicina-personalizada.git
cd TFM-medicina-personalizada
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run_all.py
python -m pytest -q
python tools/verify_repository.py
```

`run_all.py` parte del CSV bruto, comprueba su hash, reconstruye los dos
datasets derivados, separa train/holdout, ajusta y evalúa los modelos, realiza
las auditorías y regenera tablas, figuras, metadatos y el artefacto serializado.

Para ejecutar la interfaz:

```bash
streamlit run app.py
```

Para revisar el estudio interactivo:

```bash
python tools/render_notebook.py
jupyter notebook notebooks/01_estudio_completo_oncologia.ipynb
```

Los mismos accesos se ofrecen mediante `make reproduce`, `make test`,
`make audit`, `make notebook` y `make web`.

## Revisión pública

- Repositorio: <https://github.com/catrilaf/TFM-medicina-personalizada>
- Ejecuciones automáticas: <https://github.com/catrilaf/TFM-medicina-personalizada/actions>
- Aplicación Streamlit pública:
  <https://tfm-medicina-personalizada.streamlit.app/>.
- Configuración remota comprobada: rama `main`, entrada `app.py` y Python 3.12.
- Verificación funcional realizada el 19 de agosto de 2026: carga de las cinco
  secciones, abstención del perfil válido y advertencia para estadio I con
  metástasis.

## Estructura

```text
.
├── app.py                       # interfaz Streamlit
├── run_all.py                   # ejecución integral
├── src/                         # implementación modular
├── tests/                       # contratos y pruebas funcionales
├── tools/                       # reconstrucción, notebook y manifiesto
├── data/                        # fuente, derivados, muestra y diccionario
├── outputs/
│   ├── figures/                 # 18 gráficos reproducibles
│   ├── tables/                  # 35 tablas reproducibles
│   └── models/                  # pipeline serializado y metadatos
├── notebooks/                   # estudio ejecutado paso a paso
├── reports/                     # informe técnico HTML
├── docs/                        # auditoría y trazabilidad
├── memoria/                     # memoria final en DOCX y PDF
├── .github/workflows/           # validación automática
├── .streamlit/                  # configuración de la interfaz
└── legacy/                      # scripts recibidos, solo trazabilidad
```

## Límites de uso

Este repositorio no valida un dispositivo médico ni estima el tratamiento
óptimo. La etiqueta observada es el régimen registrado, no un resultado causal.
El proyecto tampoco prueba supervivencia, toxicidad, eficacia, seguridad,
costo-efectividad ni impacto IR-GRD. Cualquier evolución hospitalaria exigiría
una cohorte trazable, aprobación ética, definición clínica del objetivo,
validación temporal y externa, calibración, análisis de sesgos, evaluación
prospectiva, gobernanza y supervisión profesional.

## Autoría, asistencia técnica y licencia

El autor mantiene la responsabilidad académica sobre las decisiones, el
código, las comprobaciones y la defensa. El uso de herramientas de IA para
apoyo técnico se documenta en
[`docs/REGISTRO_USO_IA.md`](docs/REGISTRO_USO_IA.md); sus propuestas no se
aceptaron como evidencia sin verificación mediante ejecución, pruebas y
contraste con los artefactos generados.

La licencia Apache 2.0 indicada en este repositorio corresponde al **dataset de
origen**, no concede automáticamente una licencia sobre el código. Salvo
indicación expresa del autor, el código se publica para revisión académica con
los derechos reservados.
