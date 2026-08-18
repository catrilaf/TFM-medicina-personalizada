"""Pipelines, validación cruzada y entrenamiento final."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import make_scorer

from .config import (
    CATEGORICAL_FEATURES,
    CORE_FEATURES,
    NUMERIC_FEATURES,
    SEED,
    TEST_SIZE,
)
from .metrics import evaluate_multiclass


def build_preprocessor(dense: bool = False) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            (
                "categoricas",
                OneHotEncoder(handle_unknown="ignore", sparse_output=not dense),
                CATEGORICAL_FEATURES,
            ),
            ("numericas", StandardScaler(), NUMERIC_FEATURES),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def build_model_pipelines() -> dict[str, Pipeline]:
    estimators = {
        "Dummy mayoría": DummyClassifier(strategy="most_frequent"),
        "Dummy estratificado": DummyClassifier(strategy="stratified", random_state=SEED),
        "Regresión logística": LogisticRegression(
            max_iter=800,
            class_weight="balanced",
            solver="lbfgs",
            random_state=SEED,
        ),
        "Árbol CART": DecisionTreeClassifier(
            max_depth=8,
            min_samples_leaf=100,
            class_weight="balanced",
            random_state=SEED,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=160,
            max_depth=12,
            min_samples_leaf=5,
            class_weight="balanced_subsample",
            random_state=SEED,
            n_jobs=1,
        ),
        "Extra Trees": ExtraTreesClassifier(
            n_estimators=160,
            max_depth=14,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=SEED,
            n_jobs=1,
        ),
    }
    return {
        name: Pipeline([("preprocesamiento", build_preprocessor()), ("modelo", estimator)])
        for name, estimator in estimators.items()
    }


def split_holdout(df: pd.DataFrame, target: str):
    X = df[CORE_FEATURES].copy()
    y = df[target].copy()
    return train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=SEED,
    )


def cross_validate_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_splits: int = 5,
    n_repeats: int = 2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    scoring = {
        "accuracy": "accuracy",
        "balanced_accuracy": "balanced_accuracy",
        "precision_macro": make_scorer(precision_score, average="macro", zero_division=0),
        "recall_macro": make_scorer(recall_score, average="macro", zero_division=0),
        "f1_macro": make_scorer(f1_score, average="macro", zero_division=0),
        "neg_log_loss": "neg_log_loss",
    }
    cv = RepeatedStratifiedKFold(
        n_splits=n_splits,
        n_repeats=n_repeats,
        random_state=SEED,
    )
    long_rows: list[dict[str, float | int | str]] = []
    for model_name, pipeline in build_model_pipelines().items():
        scores = cross_validate(
            pipeline,
            X_train,
            y_train,
            scoring=scoring,
            cv=cv,
            n_jobs=-1,
            return_train_score=False,
            error_score="raise",
        )
        fold_count = len(scores["test_accuracy"])
        for fold in range(fold_count):
            long_rows.append(
                {
                    "modelo": model_name,
                    "fold": fold + 1,
                    "accuracy": scores["test_accuracy"][fold],
                    "balanced_accuracy": scores["test_balanced_accuracy"][fold],
                    "precision_macro": scores["test_precision_macro"][fold],
                    "recall_macro": scores["test_recall_macro"][fold],
                    "f1_macro": scores["test_f1_macro"][fold],
                    "log_loss": -scores["test_neg_log_loss"][fold],
                }
            )
    long_df = pd.DataFrame(long_rows)
    metric_columns = [
        "accuracy",
        "balanced_accuracy",
        "precision_macro",
        "recall_macro",
        "f1_macro",
        "log_loss",
    ]
    summary = long_df.groupby("modelo")[metric_columns].agg(["mean", "std"]).reset_index()
    summary.columns = [
        "modelo" if col[0] == "modelo" else f"{col[0]}_{col[1]}"
        for col in summary.columns
    ]
    summary = summary.sort_values("f1_macro_mean", ascending=False).reset_index(drop=True)
    return long_df, summary


def select_experimental_model(cv_summary: pd.DataFrame) -> str:
    eligible = cv_summary[~cv_summary["modelo"].str.startswith("Dummy")].copy()
    return str(eligible.sort_values("f1_macro_mean", ascending=False).iloc[0]["modelo"])


def fit_holdout_model(
    model_name: str,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> dict[str, object]:
    pipeline = clone(build_model_pipelines()[model_name])
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)
    classes = pipeline.named_steps["modelo"].classes_
    metrics = evaluate_multiclass(y_test, predictions, probabilities, classes)
    return {
        "pipeline": pipeline,
        "predictions": predictions,
        "probabilities": probabilities,
        "classes": classes,
        "metrics": metrics,
    }


def fit_full_and_save(
    model_name: str,
    X: pd.DataFrame,
    y: pd.Series,
    output_path: Path,
) -> Pipeline:
    pipeline = clone(build_model_pipelines()[model_name])
    pipeline.fit(X, y)
    joblib.dump(pipeline, output_path, compress=3)
    return pipeline


def feature_importance_table(pipeline: Pipeline) -> pd.DataFrame:
    feature_names = pipeline.named_steps["preprocesamiento"].get_feature_names_out()
    estimator = pipeline.named_steps["modelo"]
    if hasattr(estimator, "feature_importances_"):
        values = np.asarray(estimator.feature_importances_)
        method = "Importancia interna del ensemble"
    elif hasattr(estimator, "coef_"):
        values = np.mean(np.abs(np.asarray(estimator.coef_)), axis=0)
        method = "Media del valor absoluto de coeficientes"
    else:
        return pd.DataFrame(columns=["variable_transformada", "importancia", "metodo"])
    result = pd.DataFrame(
        {
            "variable_transformada": feature_names,
            "importancia": values,
            "metodo": method,
        }
    )
    return result.sort_values("importancia", ascending=False).reset_index(drop=True)


def prediction_table(
    ids: pd.Series,
    y_true: pd.Series,
    predictions: np.ndarray,
    probabilities: np.ndarray,
    classes: np.ndarray,
) -> pd.DataFrame:
    result = pd.DataFrame(
        {
            "patient_id": np.asarray(ids),
            "regimen_real": np.asarray(y_true),
            "regimen_predicho_experimental": predictions,
            "confianza_maxima": np.max(probabilities, axis=1),
            "prediccion_correcta": np.asarray(y_true) == predictions,
        }
    )
    for idx, label in enumerate(classes):
        result[f"prob_{label}"] = probabilities[:, idx]
    return result
