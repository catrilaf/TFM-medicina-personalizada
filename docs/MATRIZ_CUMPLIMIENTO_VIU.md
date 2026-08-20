# Matriz de cumplimiento de la pauta VIU

Revisión realizada sobre la memoria final DOCX/PDF, las instrucciones de
realización del TFT, la guía docente 10PIAA y el protocolo de defensa aportados
por el autor. Esta matriz es una comprobación técnica; no sustituye la
autorización del tutor, el informe de Turnitin ni la evaluación del tribunal.

| Requisito | Estado | Evidencia u observación |
|---|---|---|
| Portada con título, fecha, titulación, curso, estudiante, tutor y convocatoria | Cumple | Portada de la memoria, página 1. El autor debe confirmar que los datos administrativos siguen vigentes el día del depósito. |
| Índice general con páginas | Cumple | Índice automático en las páginas iniciales. |
| Índices de tablas y figuras | Cumple | Ambos índices están incluidos y numerados. |
| Resumen de 200–300 palabras | Cumple | El recuento automatizado de la versión final obtiene 293 palabras en español. |
| Abstract en inglés | Cumple | El recuento automatizado obtiene 223 palabras. |
| Entre 4 y 8 palabras clave | Cumple | Se incluyen ocho palabras clave y ocho keywords. |
| Introducción, objetivos, estado del arte, metodología, resultados, discusión y conclusiones | Cumple | Estructura completa y coherente con un estudio de viabilidad. |
| Limitaciones y líneas futuras | Cumple | Se distinguen falta de procedencia clínica, ausencia de señal, NO-GO y requisitos hospitalarios. |
| Referencias y citas | Cumple con revisión final del autor | La bibliografía se presenta con sangría francesa y las citas principales tienen correspondencia. El autor debe realizar la última comprobación APA y de enlaces. |
| Arial 11, epígrafes de nivel 1 a 18 y nivel 2 a 14 | Cumple | Estilos del DOCX auditados; interlineado 1,5 en el cuerpo. |
| Capítulos principales en página nueva | Cumple | La paginación observada respeta los saltos de nivel 1. |
| Tablas y figuras identificadas, explicadas y con fuente | Cumple | Se incluyen leyendas, referencias en texto y fuente de elaboración propia o bibliográfica. |
| Anexos técnicos pertinentes | Cumple | Fichas, riesgos, reproducibilidad, procedencia, contrato, NO-GO, web, trazabilidad y fragmentos esenciales. |
| Originalidad y redacción autónoma | Responsabilidad del autor | No puede certificarse mediante revisión técnica. Turnitin solo se ejecuta en el depósito oficial y el autor debe releer y asumir cada párrafo. |
| Declaración del uso de IA | Cumple, pendiente de confirmación final del autor | La memoria y `docs/REGISTRO_USO_IA.md` declaran ChatGPT, Claude, Gemini y Codex, con alcance, límites y verificaciones. Las versiones declaradas deben ser confirmadas por el autor antes del depósito. |
| Paquete Python reproducible | Cumple | `run_all.py`, dependencias fijadas, tests, notebook ejecutado, 35 tablas, 18 figuras, modelo, metadatos y manifiesto. La conclusión NO-GO se comprueba con tolerancia numérica entre sistemas operativos. |
| Aplicación web segura | Cumple como prototipo | Streamlit carga el pipeline, valida entradas, genera alertas y se abstiene; no es una herramienta clínica. |
| Enlace público auditable | Cumple | Código: <https://github.com/catrilaf/TFM-medicina-personalizada>. Aplicación: <https://tfm-medicina-personalizada.streamlit.app/>. La instancia se verificó con Python 3.12, cinco secciones navegables, abstención y alerta de consistencia. |
| Diagnóstico del proceso generador de datos | Cumple | La subsección 6.14 de Resultados integra aleatorización de etiquetas, curva de aprendizaje y skill probabilístico; los cálculos proceden de `src/robustness.py`. |
| Enlace directo de cada anexo a su código | Cumple | [`ANEXOS_Y_CODIGO.md`](ANEXOS_Y_CODIGO.md) relaciona los anexos A-L con scripts y salidas; la auditoría comprueba la existencia de los enlaces. |

## Defensa

El protocolo aportado establece un máximo de 20 minutos para un TFT individual,
seguido de preguntas. Una exposición de 10 minutos no infringe el máximo, pero
puede resultar corta frente a la recomendación de ajustar bien el tiempo. Antes
de preparar la versión definitiva conviene confirmar con el tutor si espera
10 minutos o una duración más próxima a 15–18 minutos. El PDF usado en la
defensa debe nombrarse conforme a la convocatoria indicada por la universidad.
