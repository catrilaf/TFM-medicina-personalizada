# Despliegue de la aplicación Streamlit

La aplicación puede revisarse localmente o publicarse como demostración
académica. No requiere secretos, base de datos ni servicios externos.

**Instancia pública verificada:**
<https://tfm-medicina-personalizada.streamlit.app/>

La instancia usa el repositorio `catrilaf/TFM-medicina-personalizada`, la rama
`main`, `app.py` como archivo principal y Python 3.12. El acceso está configurado
como público y localizable en los ajustes de Streamlit Community Cloud.

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

## Verificación del despliegue vigente

El 19 de agosto de 2026 se comprobó en la instancia pública que:

- las cinco secciones de la interfaz cargan;
- el perfil mediano termina en abstención con una confianza máxima de 26,1 %;
- el control «estadio I con metástasis» genera una advertencia de consistencia
  y también termina en abstención;
- el panel muestra el dictamen `NO-GO clínico`, F1 macro CV 0,252 y abstención
  del 100 % en holdout;
- no se solicitan identificadores ni se muestra una recomendación terapéutica.

La primera construcción automática seleccionó Python 3.14 y no completó el
aprovisionamiento. Se fijó Python 3.12 desde los ajustes de Community Cloud,
tras lo cual se instalaron las 97 dependencias declaradas y el servidor inició
correctamente. Esta configuración coincide con la versión indicada para la
reproducción local.

## Controles antes de compartir la URL

- El encabezado debe indicar “prototipo académico no asistencial”.
- Un perfil válido debe finalizar en `ABSTENCIÓN` con el modelo actual.
- “Estadio I con metástasis” debe producir una advertencia.
- No deben solicitarse nombre, historia clínica ni identificadores.
- La página de evidencia debe mostrar F1 macro 0,2496 en holdout y comparación
  con el Dummy estratificado.
- La aplicación no debe registrar ni afirmar una recomendación terapéutica.

GitHub permite auditar el código y Streamlit facilita la revisión funcional.
Ninguno de los dos convierte el prototipo en un sistema clínicamente validado.
