# train_model.py - Entrenamiento reproducible sobre dataset Kaggle limpiado
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import classification_report

df = pd.read_csv("chemotherapy_patient_data_model_ready_recommender_tfm.csv")
features = ["age","age_group","sex","bmi","bmi_category","smoking_status","cancer_type","genetic_mutation","tumor_stage","tumor_stage_numeric","tumor_size_cm","metastasis_status","metastasis_binary","clinical_risk_group","frailty_risk_pre"]
X = df[features]
y = df["chemotherapy_regimen"]
cat = [c for c in features if X[c].dtype == "object"]
num = [c for c in features if c not in cat]
pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), cat), ("num", StandardScaler(), num)])
model = Pipeline([("prep", pre), ("model", ExtraTreesClassifier(n_estimators=120, max_depth=14, random_state=42, class_weight="balanced"))])
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.25, random_state=42)
model.fit(X_train, y_train)
print(classification_report(y_test, model.predict(X_test)))
