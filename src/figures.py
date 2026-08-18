"""Visualizaciones reproducibles con criterios de data storytelling."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

BLUE = "#245783"
ORANGE = "#E84A0C"
LIGHT_BLUE = "#DCE6F1"
GRAY = "#6B7280"


def setup_style() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 180,
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "font.family": "DejaVu Sans",
        }
    )


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_target_distribution(target_table: pd.DataFrame, path: Path) -> None:
    setup_style()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=target_table, x="chemotherapy_regimen", y="n", color=BLUE, ax=ax)
    for index, row in target_table.reset_index(drop=True).iterrows():
        ax.text(index, row["n"] + 180, f"{row['proporcion']:.1%}", ha="center", fontsize=9)
    ax.set(title="Distribución del régimen registrado", xlabel="Régimen", ylabel="Registros")
    ax.text(
        0.5,
        -0.22,
        "El target no está perfectamente equilibrado; FOLFOX es la clase mayoritaria.",
        transform=ax.transAxes,
        ha="center",
        color=GRAY,
        fontsize=9,
    )
    _save(fig, path)


def plot_numeric_eda(df: pd.DataFrame, path: Path) -> None:
    setup_style()
    columns = [("age", "Edad"), ("bmi", "IMC"), ("tumor_size_cm", "Tamaño tumoral (cm)")]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, (column, label) in zip(axes, columns):
        sns.histplot(df[column], bins=25, kde=True, color=BLUE, ax=ax)
        ax.set(title=label, xlabel=label, ylabel="Frecuencia")
    fig.suptitle("Distribuciones de variables numéricas pretratamiento", y=1.02, fontsize=14)
    _save(fig, path)


def plot_categorical_eda(df: pd.DataFrame, path: Path) -> None:
    setup_style()
    items = [
        ("cancer_type", "Tipo de cáncer"),
        ("tumor_stage", "Estadio tumoral"),
        ("smoking_status", "Estado tabáquico"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    for ax, (column, title) in zip(axes, items):
        order = df[column].value_counts().index
        sns.countplot(data=df, x=column, order=order, color=BLUE, ax=ax)
        ax.set(title=title, xlabel="", ylabel="Registros")
        ax.tick_params(axis="x", rotation=35)
    fig.suptitle("Composición del conjunto model-ready", y=1.02, fontsize=14)
    _save(fig, path)


def plot_target_by_cancer(df: pd.DataFrame, path: Path) -> None:
    setup_style()
    table = pd.crosstab(
        df["cancer_type"],
        df["chemotherapy_regimen"],
        normalize="index",
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.heatmap(table, annot=True, fmt=".1%", cmap="Blues", vmin=0, vmax=0.36, ax=ax)
    ax.set(
        title="Distribución del régimen dentro de cada tipo de cáncer",
        xlabel="Régimen registrado",
        ylabel="Tipo de cáncer",
    )
    _save(fig, path)


def plot_associations(associations: pd.DataFrame, path: Path) -> None:
    setup_style()
    data = associations.sort_values("cramers_v_corregido", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=data, x="cramers_v_corregido", y="variable", color=BLUE, ax=ax)
    ax.axvline(0.10, color=ORANGE, linestyle="--", label="Umbral descriptivo 0,10")
    ax.set(
        title="Asociación categórica con el régimen registrado",
        xlabel="V de Cramér corregido",
        ylabel="Variable",
        xlim=(0, max(0.12, data["cramers_v_corregido"].max() * 1.25)),
    )
    ax.legend(loc="lower right")
    _save(fig, path)


def plot_cv_comparison(cv_summary: pd.DataFrame, path: Path) -> None:
    setup_style()
    data = cv_summary.sort_values("f1_macro_mean", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    positions = range(len(data))
    ax.barh(
        [p - 0.18 for p in positions],
        data["f1_macro_mean"],
        height=0.34,
        xerr=data["f1_macro_std"],
        label="F1 macro",
        color=BLUE,
        alpha=0.9,
    )
    ax.barh(
        [p + 0.18 for p in positions],
        data["balanced_accuracy_mean"],
        height=0.34,
        xerr=data["balanced_accuracy_std"],
        label="Balanced accuracy",
        color=ORANGE,
        alpha=0.85,
    )
    ax.set_yticks(list(positions), data["modelo"])
    ax.axvline(0.25, color=GRAY, linestyle="--", linewidth=1.2, label="Azar aproximado (4 clases)")
    ax.set(
        title="Validación cruzada repetida en el conjunto de entrenamiento",
        xlabel="Métrica media (± desviación estándar)",
        ylabel="",
        xlim=(0, max(0.34, data[["f1_macro_mean", "balanced_accuracy_mean"]].max().max() + 0.04)),
    )
    ax.legend(loc="lower right")
    _save(fig, path)


def plot_confusion(normalized: pd.DataFrame, path: Path) -> None:
    setup_style()
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    sns.heatmap(normalized, annot=True, fmt=".1%", cmap="Blues", vmin=0, vmax=1, ax=ax)
    ax.set(
        title="Matriz de confusión normalizada - holdout",
        xlabel="Predicción experimental",
        ylabel="Régimen registrado",
    )
    _save(fig, path)


def plot_feature_importance(importance: pd.DataFrame, path: Path, top_n: int = 15) -> None:
    setup_style()
    data = importance.head(top_n).sort_values("importancia", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(data=data, x="importancia", y="variable_transformada", color=BLUE, ax=ax)
    ax.set(
        title="Importancia interna del modelo experimental",
        xlabel="Importancia relativa",
        ylabel="Variable transformada",
    )
    _save(fig, path)


def plot_confidence(predictions: pd.DataFrame, path: Path) -> None:
    setup_style()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(
        data=predictions,
        x="confianza_maxima",
        hue="prediccion_correcta",
        bins=30,
        stat="density",
        common_norm=False,
        element="step",
        palette={True: BLUE, False: ORANGE},
        ax=ax,
    )
    ax.axvline(0.45, color=GRAY, linestyle="--", label="Umbral de abstención del prototipo")
    ax.set(
        title="Confianza máxima del modelo en holdout",
        xlabel="Probabilidad máxima",
        ylabel="Densidad",
    )
    ax.legend(title="Correcta / umbral")
    _save(fig, path)


def plot_subgroups(subgroups: pd.DataFrame, path: Path) -> None:
    setup_style()
    data = subgroups.copy()
    data["etiqueta"] = data["atributo"] + ": " + data["grupo"]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.barplot(data=data, x="f1_macro", y="etiqueta", hue="atributo", dodge=False, ax=ax)
    ax.axvline(0.25, color=GRAY, linestyle="--", label="Azar aproximado")
    ax.set(
        title="Rendimiento exploratorio por subgrupos",
        xlabel="F1 macro",
        ylabel="",
        xlim=(0, max(0.35, data["f1_macro"].max() + 0.05)),
    )
    ax.legend(loc="lower right")
    _save(fig, path)


def plot_cluster_evaluation(evaluation: pd.DataFrame, path: Path) -> None:
    setup_style()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    sns.lineplot(data=evaluation, x="k", y="silhouette", marker="o", color=BLUE, ax=axes[0])
    axes[0].set(title="Coeficiente de Silhouette", xlabel="Número de clusters (k)", ylabel="Silhouette")
    sns.lineplot(data=evaluation, x="k", y="davies_bouldin", marker="o", color=ORANGE, ax=axes[1])
    axes[1].set(title="Índice Davies-Bouldin", xlabel="Número de clusters (k)", ylabel="DBI (menor es mejor)")
    fig.suptitle("Selección exploratoria del número de clusters", y=1.02, fontsize=14)
    _save(fig, path)


def plot_cluster_pca(pca_sample: pd.DataFrame, path: Path) -> None:
    setup_style()
    fig, ax = plt.subplots(figsize=(8, 5.5))
    sns.scatterplot(
        data=pca_sample,
        x="pc1",
        y="pc2",
        hue="cluster",
        palette="tab10",
        alpha=0.45,
        s=18,
        linewidth=0,
        ax=ax,
    )
    ax.set(
        title="Proyección PCA de los perfiles pretratamiento",
        xlabel="Componente principal 1",
        ylabel="Componente principal 2",
    )
    ax.legend(title="Cluster", bbox_to_anchor=(1.02, 1), loc="upper left")
    _save(fig, path)


def plot_calibration(calibration: pd.DataFrame, path: Path) -> None:
    """Representa confianza media frente a acierto observado por intervalo."""

    setup_style()
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    ax.plot([0, 1], [0, 1], linestyle="--", color=GRAY, label="Calibración ideal")
    sizes = 70 + 650 * calibration["peso"]
    ax.scatter(
        calibration["confianza_media"],
        calibration["accuracy_observada"],
        s=sizes,
        color=BLUE,
        edgecolor="white",
        linewidth=0.8,
        alpha=0.9,
    )
    for _, row in calibration.iterrows():
        ax.annotate(
            f"n={int(row['n'])}",
            (row["confianza_media"], row["accuracy_observada"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set(
        title="Calibración top-label en holdout",
        xlabel="Confianza media",
        ylabel="Accuracy observada",
        xlim=(0.20, 0.50),
        ylim=(0.15, 0.50),
    )
    ax.legend(loc="upper left")
    _save(fig, path)


def plot_permutation_importance(importance: pd.DataFrame, path: Path) -> None:
    """Muestra la pérdida de F1 al permutar cada variable original."""

    setup_style()
    data = importance.sort_values("importancia_media", ascending=True)
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.errorbar(
        data["importancia_media"],
        data["variable"],
        xerr=2 * data["importancia_desviacion"],
        fmt="o",
        color=BLUE,
        ecolor=LIGHT_BLUE,
        elinewidth=5,
        capsize=3,
    )
    ax.axvline(0, color=ORANGE, linestyle="--", linewidth=1.2)
    ax.set(
        title="Importancia por permutación en holdout",
        xlabel="Disminución de F1 macro (media ± 2 DE)",
        ylabel="Variable original",
    )
    _save(fig, path)


def plot_selective_performance(selective: pd.DataFrame, path: Path) -> None:
    """Relaciona umbral, cobertura y rendimiento de los casos retenidos."""

    setup_style()
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.plot(
        selective["umbral"],
        selective["cobertura"],
        marker="o",
        color=BLUE,
        label="Cobertura",
    )
    ax.plot(
        selective["umbral"],
        selective["f1_macro_selectivo"],
        marker="o",
        color=ORANGE,
        label="F1 macro no abstenciones",
    )
    ax.axvline(0.45, color=GRAY, linestyle="--", label="Umbral del prototipo")
    ax.set(
        title="Cobertura y rendimiento según el umbral",
        xlabel="Umbral de confianza",
        ylabel="Proporción / métrica",
        ylim=(-0.02, 1.02),
    )
    ax.legend(loc="upper right")
    _save(fig, path)


def plot_paired_cv(comparisons: pd.DataFrame, path: Path) -> None:
    """Visualiza diferencias pareadas de F1 del modelo seleccionado."""

    setup_style()
    data = comparisons.sort_values("delta_f1_macro_medio", ascending=True)
    center = data["delta_f1_macro_medio"].to_numpy()
    lower = center - data["delta_f1_ic95_inferior"].to_numpy()
    upper = data["delta_f1_ic95_superior"].to_numpy() - center
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.errorbar(
        center,
        data["comparador"],
        xerr=np.vstack([lower, upper]),
        fmt="o",
        color=BLUE,
        ecolor=LIGHT_BLUE,
        elinewidth=5,
        capsize=4,
    )
    ax.axvline(0, color=ORANGE, linestyle="--", linewidth=1.2)
    ax.set(
        title="Diferencia pareada de F1 macro en validación cruzada",
        xlabel="F1 seleccionado - F1 comparador (IC 95 % bootstrap)",
        ylabel="Comparador",
    )
    _save(fig, path)


def plot_label_randomization(
    summary: pd.DataFrame,
    distribution: pd.DataFrame,
    path: Path,
) -> None:
    """Compara el F1 observado con la distribución nula por permutación."""

    setup_style()
    observed = float(summary.iloc[0]["f1_macro_observado"])
    null_low = float(summary.iloc[0]["f1_macro_nulo_ic95_inferior"])
    null_high = float(summary.iloc[0]["f1_macro_nulo_ic95_superior"])
    fig, ax = plt.subplots(figsize=(8.5, 5))
    sns.histplot(distribution["f1_macro_nulo"], bins=35, color=LIGHT_BLUE, ax=ax)
    ax.axvspan(null_low, null_high, color=BLUE, alpha=0.12, label="IC 95 % bajo H0")
    ax.axvline(observed, color=ORANGE, linewidth=2, label=f"Observado = {observed:.4f}")
    ax.set(
        title="Prueba de aleatorización de etiquetas en holdout",
        xlabel="F1 macro con etiquetas permutadas",
        ylabel="Frecuencia",
    )
    ax.legend(loc="upper left")
    _save(fig, path)


def plot_learning_curve(curve: pd.DataFrame, path: Path) -> None:
    """Muestra F1 de validación al aumentar el tamaño de entrenamiento."""

    setup_style()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    palette = {"Random Forest": BLUE, "Dummy estratificado": ORANGE}
    for model_name, group in curve.groupby("modelo", sort=False):
        group = group.sort_values("n_entrenamiento_por_fold")
        color = palette.get(model_name, GRAY)
        axes[0].errorbar(
            group["n_entrenamiento_por_fold"],
            group["f1_validacion_media"],
            yerr=group["f1_validacion_std"],
            marker="o",
            capsize=3,
            color=color,
            label=model_name,
        )
    axes[0].axhline(0.25, color=GRAY, linestyle=":", label="Azar aproximado")
    axes[0].set(
        title="Generalización al aumentar los datos",
        xlabel="Registros usados para entrenar en cada fold",
        ylabel="F1 macro (media ± DE)",
        ylim=(0.20, 0.36),
    )
    axes[0].legend(loc="upper right")

    selected_name = next(name for name in curve["modelo"].unique() if name != "Dummy estratificado")
    selected = curve.loc[curve["modelo"] == selected_name].sort_values(
        "n_entrenamiento_por_fold"
    )
    axes[1].errorbar(
        selected["n_entrenamiento_por_fold"],
        selected["f1_train_media"],
        yerr=selected["f1_train_std"],
        marker="o",
        capsize=3,
        color=BLUE,
        label="Entrenamiento",
    )
    axes[1].errorbar(
        selected["n_entrenamiento_por_fold"],
        selected["f1_validacion_media"],
        yerr=selected["f1_validacion_std"],
        marker="o",
        capsize=3,
        color=ORANGE,
        label="Validación",
    )
    axes[1].set(
        title=f"Brecha train-validación: {selected_name}",
        xlabel="Registros usados para entrenar en cada fold",
        ylabel="F1 macro (media ± DE)",
        ylim=(0.20, 1.00),
    )
    axes[1].legend(loc="center right")
    fig.suptitle("Curva de aprendizaje dentro del conjunto de entrenamiento", y=1.03, fontsize=14)
    _save(fig, path)
