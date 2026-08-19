# Despliegue de la aplicación Streamlit

La aplicación puede revisarse localmente o publicarse como demostración
académica. No requiere secretos, base de datos ni servicios externos.

## Ejecución local

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit muestra la URL local en la terminal. Las pruebas funcionales pueden
ejecutarse sin navegador mediante:

```bash
python -m pytest -q tests/test_streamlit_app.py
```

## Publicación en Streamlit Community Cloud

1. Fusionar en `main` una revisión que haya superado GitHub Actions.
2. Acceder a <https://share.streamlit.io/> con la cuenta vinculada a GitHub.
3. Seleccionar `catrilaf/TFM-medicina-personalizada`, rama `main`.
4. Indicar `app.py` como archivo principal.
5. Elegir Python 3.12 si la interfaz lo solicita y desplegar.
6. Abrir la URL pública en una sesión privada y probar las cinco secciones, un
   caso válido, el perfil inconsistente y la abstención.
7. Añadir al README únicamente la URL comprobada.

## Controles antes de compartir la URL

- El encabezado debe indicar “prototipo académico no asistencial”.
- Un perfil válido debe finalizar en `ABSTENCIÓN` con el modelo actual.
- “Estadio I con metástasis” debe producir una advertencia.
- No deben solicitarse nombre, historia clínica ni identificadores.
- La página de evidencia debe mostrar F1 macro 0,2496 en holdout y comparación
  con el Dummy estratificado.
- La aplicación no debe registrar ni afirmar una recomendación terapéutica.

El repositorio no declara una URL pública hasta que el autor complete estos
pasos y confirme su disponibilidad. GitHub permite auditar el código; no
sustituye el despliegue de Streamlit.
