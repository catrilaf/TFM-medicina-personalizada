"""Aplicación Streamlit para explorar el prototipo y su evidencia.

La interfaz está conectada al pipeline serializado, pero aplica abstención y no
presenta su salida como recomendación clínica.
"""

from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import joblib
import pandas as pd
import streamlit as st

from src.app_logic import (
    build_input_frame,
    clinical_consistency_alerts,
    uncertainty_indicators,
)

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "outputs" / "models" / "modelo_experimental_full.joblib"
METADATA_PATH = ROOT / "outputs" / "models" / "model_metadata.json"
SOURCE_METADATA_PATH = ROOT / "data" / "SOURCE_METADATA.json"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
MODEL_CARD_PATH = ROOT / "MODEL_CARD.md"

st.set_page_config(
    page_title="Auditoría de IA oncológica",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root { --navy:#173B5E; --blue:#245783; --orange:#E84A0C; --soft:#F4F7FA; }
    .stApp { background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 22%); }
    .block-container { max-width: 1240px; padding-top: 1.4rem; padding-bottom: 3rem; }
    .hero { padding: 1.5rem 1.65rem; border-radius: 18px; color: white;
            background: linear-gradient(120deg, #173B5E 0%, #245783 70%, #356F9F 100%);
            box-shadow: 0 12px 28px rgba(23,59,94,.16); margin-bottom: 1rem; }
    .hero h1 { margin:0 0 .35rem 0; font-size:2rem; }
    .hero p { margin:0; color:#EAF2F8; max-width:900px; }
    .status { display:inline-block; padding:.28rem .65rem; border-radius:999px;
              background:#FFF1E8; color:#A33A06; font-weight:700; font-size:.83rem; }
    .note { border-left:4px solid #E84A0C; background:#FFF7F2; padding:.85rem 1rem;
            border-radius:0 10px 10px 0; }
    div[data-testid="stMetric"] { background:white; border:1px solid #E4EAF0;
                                  padding:12px 14px; border-radius:13px; }
    div[data-testid="stForm"] { background:#FFFFFF; border:1px solid #DDE6EE;
                                padding:1.15rem; border-radius:16px; }
    .small-muted { color:#667085; font-size:.9rem; }
    .gate { display:flex; gap:.8rem; align-items:flex-start; border:1px solid #F4C7B5;
            background:#FFF8F5; padding:1rem 1.1rem; border-radius:13px; margin:.8rem 0; }
    .gate strong { color:#9A3412; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_artifacts():
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError("Ejecute primero: python run_all.py")
    return (
        joblib.load(MODEL_PATH),
        json.loads(METADATA_PATH.read_text(encoding="utf-8")),
    )


@st.cache_data
def load_table(filename: str) -> pd.DataFrame:
    path = TABLES / filename
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def option_index(options: list[str], value: str) -> int:
    return options.index(value) if value in options else 0


def show_image(filename: str, caption: str) -> None:
    path = FIGURES / filename
    if path.exists():
        st.image(str(path), caption=caption, width="stretch")


try:
    model, metadata = load_artifacts()
except FileNotFoundError as error:
    st.exception(error)
    st.stop()

categories = metadata["category_values"]
ranges = metadata["numeric_ranges"]
threshold = float(metadata["abstention_threshold"])
holdout_metrics = metadata["holdout_metrics"]
f1_interval = metadata.get("holdout_intervals_95", {}).get("f1_macro", [None, None])

st.markdown(
    """
    <section class="hero">
      <span class="status">PROTOTIPO ACADÉMICO · NO ASISTENCIAL</span>
      <h1>Sistema web de recomendación personalizada en oncología</h1>
      <p>Explora el pipeline, su incertidumbre y las razones por las que el sistema se abstiene.
      La salida reproduce una etiqueta del dataset; no selecciona un tratamiento óptimo.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Dictamen", "NO-GO clínico")
metric_2.metric("F1 macro CV", f"{metadata['cv_f1_macro_mean']:.3f}")
metric_3.metric("Δ F1 vs Dummy", f"{metadata['delta_f1_vs_dummy_stratified']:+.4f}")
metric_4.metric("Abstención holdout", f"{metadata['holdout_abstention_rate']:.0%}")

st.markdown(
    '<div class="note"><b>Resultado central:</b> el modelo no supera al baseline estratificado. '
    "La aplicación está diseñada para mostrar esa limitación, no para esconderla.</div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Lectura rápida")
    st.write(metadata["evidence_conclusion"])
    st.caption(f"Artefacto generado: {metadata.get('generated_on', 'sin fecha')}")
    st.divider()
    st.markdown("**Criterios de seguridad**")
    st.write(f"- Umbral de abstención: {threshold:.0%}")
    st.caption(metadata.get("abstention_threshold_status", "Umbral experimental"))
    st.write("- Validación de rangos y categorías")
    st.write("- Sin datos identificables")
    st.write("- Sin recomendación terapéutica")
    st.divider()
    st.caption(metadata["data_provenance"])
    if MODEL_CARD_PATH.exists():
        st.download_button(
            "Descargar model card",
            MODEL_CARD_PATH.read_bytes(),
            file_name="MODEL_CARD.md",
            mime="text/markdown",
            width="stretch",
        )

simulator_tab, evidence_tab, data_tab, method_tab, hospital_tab = st.tabs(
    [
        "Simulador seguro",
        "Evidencia del modelo",
        "Datos y límites",
        "Metodología",
        "Implantación hospitalaria",
    ]
)

with simulator_tab:
    st.subheader("Simulación de una fila pretratamiento")
    st.caption(
        "Los perfiles solo sirven para comprobar la integración técnica. "
        "No introduzca información identificable. La aplicación no guarda los valores enviados."
    )

    presets = {
        "Perfil mediano del dataset": {
            "age": int(ranges["age"]["median"]),
            "sex": categories["sex"][0],
            "bmi": float(ranges["bmi"]["median"]),
            "smoking_status": categories["smoking_status"][0],
            "cancer_type": categories["cancer_type"][0],
            "genetic_mutation": "Not_reported",
            "tumor_stage": "II",
            "tumor_size_cm": float(ranges["tumor_size_cm"]["median"]),
            "metastasis_status": "No",
        },
        "Control de consistencia: estadio I con metástasis": {
            "age": 58,
            "sex": "Female",
            "bmi": 27.0,
            "smoking_status": "Never",
            "cancer_type": "Lung",
            "genetic_mutation": "EGFR",
            "tumor_stage": "I",
            "tumor_size_cm": 3.0,
            "metastasis_status": "Yes",
        },
        "Perfil avanzado dentro del rango": {
            "age": 76,
            "sex": "Male",
            "bmi": 24.5,
            "smoking_status": "Former",
            "cancer_type": "Colon",
            "genetic_mutation": "KRAS",
            "tumor_stage": "IV",
            "tumor_size_cm": 8.0,
            "metastasis_status": "Yes",
        },
    }
    preset_name = st.selectbox("Perfil de demostración", list(presets))
    preset = presets[preset_name]

    with st.form("profile_form"):
        left, middle, right = st.columns(3)
        with left:
            age = st.number_input(
                "Edad (años)",
                min_value=int(ranges["age"]["min"]),
                max_value=int(ranges["age"]["max"]),
                value=int(preset["age"]),
            )
            sex = st.selectbox(
                "Sexo registrado",
                categories["sex"],
                index=option_index(categories["sex"], str(preset["sex"])),
            )
            bmi = st.number_input(
                "IMC",
                min_value=float(ranges["bmi"]["min"]),
                max_value=float(ranges["bmi"]["max"]),
                value=float(preset["bmi"]),
                step=0.1,
            )
        with middle:
            smoking_status = st.selectbox(
                "Estado tabáquico",
                categories["smoking_status"],
                index=option_index(categories["smoking_status"], str(preset["smoking_status"])),
            )
            cancer_type = st.selectbox(
                "Tipo de cáncer",
                categories["cancer_type"],
                index=option_index(categories["cancer_type"], str(preset["cancer_type"])),
            )
            genetic_mutation = st.selectbox(
                "Mutación registrada",
                categories["genetic_mutation"],
                index=option_index(categories["genetic_mutation"], str(preset["genetic_mutation"])),
            )
        with right:
            tumor_stage = st.selectbox(
                "Estadio tumoral",
                categories["tumor_stage"],
                index=option_index(categories["tumor_stage"], str(preset["tumor_stage"])),
            )
            tumor_size_cm = st.number_input(
                "Tamaño tumoral (cm)",
                min_value=float(ranges["tumor_size_cm"]["min"]),
                max_value=float(ranges["tumor_size_cm"]["max"]),
                value=float(preset["tumor_size_cm"]),
                step=0.1,
            )
            metastasis_status = st.selectbox(
                "Metástasis registrada",
                categories["metastasis_status"],
                index=option_index(categories["metastasis_status"], str(preset["metastasis_status"])),
            )
        submitted = st.form_submit_button(
            "Evaluar incertidumbre",
            type="primary",
            width="stretch",
        )

    if submitted:
        values = {
            "age": age,
            "sex": sex,
            "bmi": bmi,
            "smoking_status": smoking_status,
            "cancer_type": cancer_type,
            "genetic_mutation": genetic_mutation,
            "tumor_stage": tumor_stage,
            "tumor_size_cm": tumor_size_cm,
            "metastasis_status": metastasis_status,
        }
        row = build_input_frame(values)
        probabilities = model.predict_proba(row)[0]
        classes = model.named_steps["modelo"].classes_
        indicators = uncertainty_indicators(probabilities)
        probability_table = (
            pd.DataFrame({"régimen": classes, "probabilidad": probabilities})
            .sort_values("probabilidad", ascending=False)
            .reset_index(drop=True)
        )
        top_label = str(probability_table.iloc[0]["régimen"])
        confidence = indicators["confianza_maxima"]

        for alert in clinical_consistency_alerts(tumor_stage, metastasis_status):
            st.warning(alert)

        st.divider()
        result_left, result_right = st.columns([1.05, 1.6])
        with result_left:
            st.markdown("#### Incertidumbre")
            a, b, c = st.columns(3)
            a.metric("Confianza máxima", f"{confidence:.1%}")
            b.metric("Margen top-2", f"{indicators['margen_top2']:.1%}")
            c.metric("Entropía", f"{indicators['entropia_normalizada']:.1%}")
            st.progress(
                min(confidence / threshold, 1.0),
                text=f"{confidence:.1%} de confianza frente a umbral {threshold:.0%}",
            )
            if confidence < threshold:
                st.error(
                    "ABSTENCIÓN. La evidencia es insuficiente y no se emite una etiqueta como decisión."
                )
            else:
                st.warning(
                    f"Etiqueta histórica con mayor probabilidad: {top_label} ({confidence:.1%}). "
                    "No constituye una recomendación terapéutica."
                )
        with result_right:
            st.markdown("#### Distribución de probabilidades")
            probability_chart = (
                alt.Chart(probability_table)
                .mark_bar(color="#245783")
                .encode(
                    x=alt.X(
                        "probabilidad:Q",
                        title="Probabilidad experimental",
                        scale=alt.Scale(domain=[0, 1]),
                        axis=alt.Axis(format="%"),
                    ),
                    y=alt.Y("régimen:N", title="Régimen registrado", sort="-x"),
                    tooltip=[
                        alt.Tooltip("régimen:N", title="Régimen"),
                        alt.Tooltip("probabilidad:Q", title="Probabilidad", format=".1%"),
                    ],
                )
                .properties(height=220)
            )
            st.altair_chart(probability_chart, width="stretch")
            st.dataframe(
                probability_table.style.format({"probabilidad": "{:.1%}"}),
                width="stretch",
                hide_index=True,
            )

        export = row.copy()
        export["resultado_sistema"] = "ABSTENCION" if confidence < threshold else top_label
        export["confianza_maxima"] = confidence
        export["margen_top2"] = indicators["margen_top2"]
        export["entropia_normalizada"] = indicators["entropia_normalizada"]
        for label, probability in zip(classes, probabilities):
            export[f"prob_{label}"] = probability
        st.download_button(
            "Descargar resultado de esta simulación",
            export.to_csv(index=False).encode("utf-8"),
            file_name="simulacion_academica.csv",
            mime="text/csv",
        )

with evidence_tab:
    st.subheader("Revisión comparativa de modelos")
    st.write(
        "La selección usa validación cruzada repetida dentro de train. El holdout se consulta una sola vez "
        "para estimar el rendimiento final."
    )
    cv = load_table("12_cv_resumen_modelos.csv")
    if not cv.empty:
        columns = [
            "modelo",
            "f1_macro_mean",
            "f1_macro_std",
            "balanced_accuracy_mean",
            "log_loss_mean",
        ]
        st.dataframe(cv[columns].style.format(precision=4), width="stretch", hide_index=True)
    show_image("06_comparacion_cv.png", "Validación cruzada repetida")

    st.markdown("#### ¿La diferencia frente al baseline es consistente?")
    paired = load_table("26_comparaciones_cv_pareadas.csv")
    if not paired.empty:
        st.dataframe(
            paired[
                [
                    "comparador",
                    "delta_f1_macro_medio",
                    "delta_f1_ic95_inferior",
                    "delta_f1_ic95_superior",
                    "p_wilcoxon_f1",
                    "lectura",
                ]
            ].style.format(precision=4),
            width="stretch",
            hide_index=True,
        )
    show_image("16_comparaciones_cv_pareadas.png", "Diferencias pareadas de F1 macro")

    st.markdown("#### Prueba directa de señal y curva de aprendizaje")
    randomization = load_table("32_prueba_aleatorizacion_etiquetas.csv")
    skill = load_table("35_skill_probabilistico.csv")
    signal_left, signal_right = st.columns([1, 1.15])
    with signal_left:
        if not randomization.empty:
            result = randomization.iloc[0]
            st.metric("p de aleatorización", f"{result['p_unilateral_superior']:.3f}")
            st.write(result["conclusion"])
        show_image("17_prueba_aleatorizacion.png", "F1 observado frente a etiquetas permutadas")
    with signal_right:
        if not skill.empty:
            st.dataframe(skill.style.format(precision=4), width="stretch", hide_index=True)
        show_image("18_curva_aprendizaje.png", "Evolución del F1 con más datos de entrenamiento")
    st.caption(
        "La aleatorización pregunta si la concordancia del holdout supera la esperable por azar. "
        "La curva de aprendizaje muestra si aumentar el número de filas modifica el rendimiento fuera de muestra."
    )

    st.markdown("#### Incertidumbre del holdout")
    bootstrap = load_table("25_ic_bootstrap_holdout.csv")
    if not bootstrap.empty:
        st.dataframe(bootstrap.style.format(precision=4), width="stretch", hide_index=True)
    if f1_interval[0] is not None:
        st.info(
            f"F1 macro holdout: {holdout_metrics['f1_macro']:.4f}; "
            f"IC 95 % bootstrap [{f1_interval[0]:.4f}, {f1_interval[1]:.4f}]."
        )

    chart_left, chart_right = st.columns(2)
    with chart_left:
        show_image("13_calibracion_top_label.png", "Calibración top-label")
    with chart_right:
        show_image("14_rendimiento_selectivo.png", "Cobertura y abstención")
    st.caption(
        "Un umbral más alto reduce la cobertura, pero no crea evidencia clínica. El umbral de 0,45 "
        "produce abstención total porque las probabilidades permanecen próximas al azar."
    )

    st.markdown("#### Importancia robusta")
    permutation = load_table("29_importancia_permutacion.csv")
    if not permutation.empty:
        st.dataframe(permutation.style.format(precision=4), width="stretch", hide_index=True)
    show_image("15_importancia_permutacion.png", "Importancia por permutación en holdout")
    st.caption(
        "Si los intervalos cruzan cero, permutar la variable no produce una pérdida estable de F1. "
        "Es una lectura más prudente que la importancia interna del bosque."
    )

with data_tab:
    st.subheader("Datos, contrato y límites")
    a, b, c = st.columns(3)
    a.metric("Registros limpios", "52.321")
    b.metric("Model-ready", "49.765")
    c.metric("Clases", len(metadata["classes"]))
    st.warning(metadata["data_provenance"])
    if SOURCE_METADATA_PATH.exists():
        source_metadata = json.loads(SOURCE_METADATA_PATH.read_text(encoding="utf-8"))
        st.caption(
            f"Kaggle v{source_metadata['version']} · {source_metadata['license']} · "
            f"SHA-256 {source_metadata['raw_sha256'][:12]}…"
        )

    st.markdown("#### Variables utilizadas")
    feature_table = pd.DataFrame(
        {
            "variable": metadata["features"],
            "momento": "Pretratamiento",
            "uso": "Clasificador experimental",
        }
    )
    st.dataframe(feature_table, width="stretch", hide_index=True)

    consistency = load_table("05_consistencia_clinica.csv")
    associations = load_table("08_asociaciones_cramers_v.csv")
    numeric_associations = load_table("31_asociaciones_numericas_target.csv")
    integrity = load_table("30_integridad_perfiles_predictores.csv")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Consistencia clínica")
        st.dataframe(consistency, width="stretch", hide_index=True)
    with right:
        st.markdown("#### Asociación con el objetivo")
        if not associations.empty:
            st.dataframe(
                associations[
                    ["variable", "cramers_v_corregido", "p_value_fdr_bh", "interpretacion"]
                ],
                width="stretch",
                hide_index=True,
            )
    st.markdown("#### Integridad de perfiles y predictores numéricos")
    integrity_left, integrity_right = st.columns(2)
    with integrity_left:
        if not integrity.empty:
            st.dataframe(integrity, width="stretch", hide_index=True)
    with integrity_right:
        if not numeric_associations.empty:
            st.dataframe(
                numeric_associations.style.format(precision=6),
                width="stretch",
                hide_index=True,
            )
    st.markdown(
        '<div class="note"><b>Qué no puede concluirse:</b> eficacia comparada, seguridad, '
        "causalidad, reducción de eventos adversos, supervivencia o costo-efectividad.</div>",
        unsafe_allow_html=True,
    )

with method_tab:
    st.subheader("Cómo se evaluó")
    st.markdown(
        """
        1. Se congeló un **holdout estratificado del 25 %** con semilla 42.
        2. La selección se realizó solo en train mediante **5 folds × 2 repeticiones**.
        3. Codificación y escalado viven dentro de `Pipeline` y `ColumnTransformer`.
        4. Se compararon dos Dummy, regresión logística, CART, Random Forest y Extra Trees.
        5. Se añadieron **IC bootstrap**, comparación pareada, calibración, importancia por permutación y análisis selectivo.
        6. Una **prueba de aleatorización** contrasta el F1 observado con 5.000 permutaciones del target.
        7. Una **curva de aprendizaje** comprueba si el rendimiento mejora al aumentar el entrenamiento.
        8. El modelo se reentrenó con todos los datos únicamente después de conservar la evidencia holdout.
        """
    )
    st.markdown(
        '<div class="gate"><div><strong>Criterio de avance:</strong><br>'
        "no desplegar ni interpretar clínicamente mientras el modelo no supere baselines, "
        "la fuente no sea trazable y no exista validación externa.</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("#### Por qué no se hizo una búsqueda agresiva de hiperparámetros")
    st.write(
        "Los predictores apenas se asocian con el objetivo y ningún algoritmo supera de forma estable "
        "al baseline. Ajustar cientos de configuraciones aumentaría el riesgo de seleccionar ruido. "
        "La siguiente mejora debe estar en los datos y la formulación clínica, no en perseguir décimas artificiales."
    )
    st.code(
        "python run_all.py\npython -m pytest -q\nstreamlit run app.py",
        language="bash",
    )

with hospital_tab:
    st.subheader("Condiciones antes de cualquier piloto hospitalario")
    st.write(
        "El prototipo actual no cumple los requisitos para uso asistencial. "
        "Una implantación real exigiría redefinir el caso de uso y comenzar con datos institucionales trazables."
    )
    hospital_conditions = pd.DataFrame(
        [
            ("Gobernanza", "Responsable clínico, comité de datos, DPO y trazabilidad de versiones."),
            ("Datos", "Cohorte autorizada, longitudinal, con línea terapéutica y criterios de inclusión."),
            ("Objetivo", "Outcome clínico causal o utilidad definida; no imitación de una etiqueta histórica."),
            ("Validación", "Temporal, externa, por subgrupos y prospectiva antes de influir en decisiones."),
            ("Interoperabilidad", "Integración controlada con HCE mediante estándares y registro de auditoría."),
            ("Seguridad", "Abstención, revisión humana obligatoria, monitorización de drift y retirada segura."),
            ("Regulación", "Evaluación jurídica y regulatoria como software sanitario cuando corresponda."),
            ("Operación", "Piloto silencioso, simulación de impacto y formación de usuarios."),
        ],
        columns=["área", "condición mínima"],
    )
    st.dataframe(hospital_conditions, width="stretch", hide_index=True)
    st.error(
        "Estado actual: NO-GO clínico. La siguiente mejora prioritaria son datos y diseño clínico, no más complejidad algorítmica."
    )

st.divider()
st.caption(
    "La decisión clínica requiere guías, historia completa, revisión multidisciplinar, validación externa, "
    "calibración y evaluación prospectiva. Esta aplicación no sustituye ninguna de esas condiciones."
)
