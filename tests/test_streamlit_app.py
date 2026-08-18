"""Pruebas funcionales de la interfaz sin levantar un navegador externo."""

from streamlit.testing.v1 import AppTest


def _app() -> AppTest:
    return AppTest.from_file("app.py", default_timeout=30).run()


def test_valid_profile_finishes_in_abstention():
    app = _app()
    app.button[0].click().run()

    assert not app.exception
    messages = [str(item.value) for item in app.error]
    assert any("ABSTENCIÓN" in message for message in messages)
    result_metrics = {metric.label: metric.value for metric in app.metric}
    assert result_metrics["Confianza máxima"] == "26.1%"


def test_inconsistent_profile_warns_and_abstains():
    app = _app()
    app.selectbox[0].select("Control de consistencia: estadio I con metástasis").run()
    app.button[0].click().run()

    assert not app.exception
    warnings = [str(item.value) for item in app.warning]
    errors = [str(item.value) for item in app.error]
    assert any("estadio I con metástasis" in message for message in warnings)
    assert any("ABSTENCIÓN" in message for message in errors)


def test_nine_inputs_have_closed_ranges_or_categories():
    app = _app()

    assert len(app.number_input) == 3
    assert len(app.selectbox) - 1 == 6  # se excluye el selector del perfil
    bounds = {widget.label: (widget.min, widget.max) for widget in app.number_input}
    assert bounds == {
        "Edad (años)": (30.0, 84.0),
        "IMC": (18.5, 35.0),
        "Tamaño tumoral (cm)": (1.0, 10.0),
    }
