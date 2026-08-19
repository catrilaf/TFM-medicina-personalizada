# Registro de uso de herramientas de inteligencia artificial

## Finalidad

Este registro documenta la asistencia técnica utilizada durante la preparación
del paquete reproducible. No atribuye a una herramienta la autoría académica ni
convierte sus respuestas en evidencia científica. El estudiante conserva la
responsabilidad de comprender, comprobar, corregir y defender cada decisión.

## Registro conocido

| Herramienta | Modelo o versión identificable | Periodo | Finalidad | Verificación humana/técnica |
|---|---|---|---|---|
| OpenAI Codex, aplicación de escritorio | Familia GPT-5. El identificador interno exacto de compilación no fue mostrado en los metadatos accesibles de la sesión | 13 de julio–19 de agosto de 2026 | Revisión de organización del código, apoyo en depuración, diseño de pruebas, documentación técnica y preparación del repositorio | Lectura del código; ejecución del pipeline; contraste entre CSV, tablas, figuras y metadatos; pruebas automatizadas; comprobación de hashes; revisión de advertencias clínicas |

## Límites de la asistencia

- La herramienta no acredita procedencia clínica, representatividad ni calidad
  del dataset.
- Las afirmaciones cuantitativas se aceptaron únicamente cuando podían
  reproducirse desde los archivos y scripts publicados.
- La IA no sustituye la evaluación del tutor, del tribunal ni de profesionales
  sanitarios.
- No se usó la aplicación como recomendador clínico y no se introdujeron datos
  reales de pacientes.
- La memoria publicada es responsabilidad del autor y debe coincidir con el
  registro real de herramientas que este mantenga antes del depósito.

## Comprobaciones aplicadas

1. Ejecución de `python run_all.py` desde el CSV bruto.
2. Ejecución de `python -m pytest -q`.
3. Confirmación de los hashes del archivo original y datasets derivados.
4. Verificación de que solo se usan nueve predictores pretratamiento.
5. Comparación de los modelos con baselines y holdout independiente.
6. Revisión de calibración, aleatorización de etiquetas, subgrupos y abstención.
7. Comprobación de que la memoria autorizada está identificada y que no se
   publican borradores, presentaciones ni archivos de trabajo adicionales.

## Nota que debe completar el autor antes del depósito

El modelo exacto debe declararse con el nivel de precisión que muestre la
interfaz utilizada. Como el identificador interno no estuvo disponible en esta
sesión, no se inventa uno. Si el historial o la cuenta muestran una variante
más precisa (por ejemplo, un nombre de modelo con fecha), el autor debe añadirla
a la tabla. También debe incorporar cualquier otra herramienta de IA que haya
utilizado y conservar, cuando la normativa lo exija, los prompts o sesiones
relevantes como evidencia privada o anexo institucional.
