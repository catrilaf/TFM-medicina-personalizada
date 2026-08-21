# Registro de uso de herramientas de inteligencia artificial

## Finalidad

Este registro documenta la asistencia técnica utilizada durante la preparación
del paquete reproducible. No atribuye a una herramienta la autoría académica ni
convierte sus respuestas en evidencia científica. El estudiante conserva la
responsabilidad de comprender, comprobar, corregir y defender cada decisión.

## Registro confirmado por el autor

| Herramienta | Modelo o versión identificable | Periodo | Finalidad | Verificación humana/técnica |
|---|---|---|---|---|
| ChatGPT | GPT-5.6 Sol, versión declarada por el autor y no acreditada mediante log adjunto | Julio–agosto de 2026 | Ordenación de etapas CRISP-DM, contraste metodológico, explicación de procedimientos y apoyo en depuración y documentación técnica | `run_all.py`, hashes, tablas, figuras, pruebas automatizadas y revisión del autor |
| Claude | Claude 4.8, versión declarada por el autor y no acreditada mediante log adjunto | Julio–agosto de 2026 | Contraste metodológico, revisión de coherencia de procedimientos y apoyo en explicación y depuración de código | Ejecución local del pipeline, comparación con métricas regeneradas y revisión del autor |
| Gemini | Gemini 3.1 Flash, versión declarada por el autor y no acreditada mediante log adjunto | Julio–agosto de 2026 | Contraste de enfoques y apoyo en documentación y procedimientos de programación | Comparación con el código ejecutado y los resultados reproducibles |
| OpenAI Codex, aplicación de escritorio | Familia GPT-5; el identificador interno exacto de compilación no fue mostrado en los metadatos accesibles de la sesión | 13 de julio–21 de agosto de 2026 | Revisión de organización del código, apoyo en depuración, diseño de pruebas, documentación técnica, auditoría y preparación del repositorio | Lectura del código; ejecución del pipeline; contraste entre CSV, tablas, figuras y metadatos; pruebas automatizadas; comprobación de hashes; revisión funcional local y pública |

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
5. Comparación de los modelos con baselines y holdout interno reservado de la selección.
6. Revisión de calibración, aleatorización de etiquetas, subgrupos y abstención.
7. Comprobación de que la memoria autorizada está identificada y que no se
   publican borradores, presentaciones ni archivos de trabajo adicionales.

## Revisión antes del depósito

Las denominaciones de ChatGPT, Claude y Gemini reproducen la declaración del
autor; el repositorio no contiene logs que permitan verificar esas versiones.
La denominación de Codex se limita a la información observable de esta sesión y
no inventa un identificador interno.
Antes del depósito, el autor debe comprobar que no falta ninguna herramienta y
conservar, cuando la normativa lo exija, los prompts o sesiones relevantes como
evidencia privada o anexo institucional.
