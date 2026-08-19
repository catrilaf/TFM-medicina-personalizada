"""Análisis no supervisado exploratorio de perfiles pretratamiento."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.metrics import davies_bouldin_score, silhouette_score

from .config import CORE_FEATURES, SEED, TARGET
from .data import cramers_v_with_p_value
from .modeling import build_preprocessor


def run_clustering(df: pd.DataFrame) -> dict[str, object]:
    preprocessor = build_preprocessor(dense=True)
    matrix = preprocessor.fit_transform(df[CORE_FEATURES])
    evaluations: list[dict[str, float | int]] = []
    fitted: dict[int, MiniBatchKMeans] = {}
    for k in range(2, 7):
        model = MiniBatchKMeans(
            n_clusters=k,
            random_state=SEED,
            n_init=10,
            batch_size=2048,
        )
        labels = model.fit_predict(matrix)
        fitted[k] = model
        evaluations.append(
            {
                "k": k,
                "inercia": float(model.inertia_),
                "silhouette": float(
                    silhouette_score(
                        matrix,
                        labels,
                        sample_size=min(5000, len(df)),
                        random_state=SEED,
                    )
                ),
                "davies_bouldin": float(davies_bouldin_score(matrix, labels)),
            }
        )
    evaluation_df = pd.DataFrame(evaluations)
    best_k = int(evaluation_df.sort_values("silhouette", ascending=False).iloc[0]["k"])
    best_model = fitted[best_k]
    labels = best_model.predict(matrix)

    clustered = df.copy()
    clustered["cluster"] = labels
    rows: list[dict[str, object]] = []
    for cluster, subset in clustered.groupby("cluster"):
        rows.append(
            {
                "cluster": int(cluster),
                "n": len(subset),
                "proporcion": float(len(subset) / len(clustered)),
                "age_mean": float(subset["age"].mean()),
                "bmi_mean": float(subset["bmi"].mean()),
                "tumor_size_cm_mean": float(subset["tumor_size_cm"].mean()),
                "sex_mode": str(subset["sex"].mode().iloc[0]),
                "cancer_type_mode": str(subset["cancer_type"].mode().iloc[0]),
                "tumor_stage_mode": str(subset["tumor_stage"].mode().iloc[0]),
                "metastasis_yes_rate": float((subset["metastasis_status"] == "Yes").mean()),
                "regimen_mode": str(subset[TARGET].mode().iloc[0]),
            }
        )
    profiles = pd.DataFrame(rows).sort_values("cluster").reset_index(drop=True)
    v_value, p_value = cramers_v_with_p_value(clustered["cluster"], clustered[TARGET])

    pca = PCA(n_components=2, random_state=SEED)
    components = pca.fit_transform(matrix)
    rng = np.random.default_rng(SEED)
    sample_indices = rng.choice(len(df), size=min(5000, len(df)), replace=False)
    pca_sample = pd.DataFrame(
        {
            "pc1": components[sample_indices, 0],
            "pc2": components[sample_indices, 1],
            "cluster": labels[sample_indices],
        }
    )
    assignments = pd.DataFrame(
        {
            "patient_id": df["patient_id"].to_numpy(),
            "cluster": labels,
        }
    )
    association = pd.DataFrame(
        [
            {
                "variable_1": "cluster",
                "variable_2": TARGET,
                "cramers_v_corregido": v_value,
                "p_value_chi2": p_value,
                "interpretacion": "No valida utilidad clínica; solo mide asociación exploratoria.",
            }
        ]
    )
    return {
        "evaluation": evaluation_df,
        "best_k": best_k,
        "profiles": profiles,
        "assignments": assignments,
        "pca_sample": pca_sample,
        "pca_explained_variance": pca.explained_variance_ratio_.tolist(),
        "target_association": association,
    }
