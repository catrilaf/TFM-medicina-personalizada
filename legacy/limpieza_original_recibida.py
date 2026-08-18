import pandas as pd
import numpy as np
import re

INPUT_PATH = "chemotherapy_patient_data.csv"
OUTPUT_CLEAN = "chemotherapy_patient_data_clean_tfm.csv"
OUTPUT_MODEL_READY = "chemotherapy_patient_data_model_ready_recommender_tfm.csv"
OUTPUT_DICTIONARY = "diccionario_variables_recomendador_oncologia.csv"
OUTPUT_SUMMARY = "resumen_limpieza_recomendador_oncologia.csv"

def snake(s):
    s = str(s).strip().replace("²", "2")
    s = re.sub(r"[\(\)/]+", " ", s)
    s = s.replace("%", "pct")
    s = re.sub(r"[^0-9A-Za-z]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_").lower()

def age_group(age):
    if age < 50:
        return "<50"
    if age < 65:
        return "50-64"
    if age < 75:
        return "65-74"
    return ">=75"

def bmi_category(bmi):
    if bmi < 18.5:
        return "Bajo_peso"
    if bmi < 25:
        return "Normopeso"
    if bmi < 30:
        return "Sobrepeso"
    return "Obesidad"

def clinical_risk(row):
    if row["tumor_stage"] == "IV" or row["metastasis_status"] == "Yes":
        return "Alto"
    if row["tumor_stage"] == "III" or row["tumor_size_cm"] >= 5:
        return "Intermedio"
    return "Bajo"

def frailty_risk(row):
    if row["age"] >= 75 or row["bmi"] < 20:
        return "Alto"
    if row["age"] >= 65 or row["bmi"] >= 30:
        return "Intermedio"
    return "Bajo"

df = pd.read_csv(INPUT_PATH)
original_shape = df.shape

clean = df.copy()
clean.columns = [snake(c) for c in clean.columns]
for col in clean.select_dtypes(include="object").columns:
    clean[col] = clean[col].astype("string").str.strip()

clean["genetic_mutation"] = clean["genetic_mutation"].fillna("Not_reported")
clean["chemotherapy_regimen_missing"] = clean["chemotherapy_regimen"].isna().astype(int)
clean["chemotherapy_regimen"] = clean["chemotherapy_regimen"].fillna("Not_recorded")

clean["bmi"] = clean["bmi"].round(1)
clean["tumor_size_cm"] = clean["tumor_size"].round(1)
clean = clean.drop(columns=["tumor_size"])
clean["dosage_mg_m2"] = clean["dosage_mg_m2"].round(1)

stage_map = {"I": 1, "II": 2, "III": 3, "IV": 4}
clean["tumor_stage_numeric"] = clean["tumor_stage"].map(stage_map).astype("Int64")
clean["metastasis_binary"] = clean["metastasis_status"].map({"Yes": 1, "No": 0}).astype("Int64")
clean["neutropenia_binary"] = clean["neutropenia"].map({"Yes": 1, "No": 0}).astype("Int64")

clean["age_group"] = clean["age"].apply(age_group)
clean["bmi_category"] = clean["bmi"].apply(bmi_category)
clean["clinical_risk_group"] = clean.apply(clinical_risk, axis=1)
clean["frailty_risk_pre"] = clean.apply(frailty_risk, axis=1)

clean["response_favorable"] = clean["tumor_response"].isin(["Complete", "Partial"]).astype(int)
clean["progressive_disease"] = (clean["tumor_response"] == "Progressive").astype(int)
clean["severe_toxicity_observed"] = ((clean["neutropenia"] == "Yes") | (clean["nausea_severity"] >= 4)).astype(int)
clean["survival_12m"] = (clean["overall_survival_months"] >= 12).astype(int)
clean["survival_24m"] = (clean["overall_survival_months"] >= 24).astype(int)
clean["record_quality_for_recommender"] = np.where(
    clean["chemotherapy_regimen"] == "Not_recorded",
    "missing_target_regimen",
    "complete_for_recommender"
)

ordered_cols = [
    "patient_id", "age", "age_group", "sex", "bmi", "bmi_category", "smoking_status",
    "cancer_type", "genetic_mutation", "tumor_stage", "tumor_stage_numeric", "tumor_size_cm",
    "metastasis_status", "metastasis_binary", "clinical_risk_group", "frailty_risk_pre",
    "chemotherapy_regimen", "chemotherapy_regimen_missing", "dosage_mg_m2", "cycles_completed",
    "nausea_severity", "neutropenia", "neutropenia_binary", "severe_toxicity_observed",
    "tumor_response", "response_favorable", "progressive_disease",
    "overall_survival_months", "survival_12m", "survival_24m", "record_quality_for_recommender"
]
clean = clean[ordered_cols]

model_ready = clean[clean["chemotherapy_regimen"] != "Not_recorded"].copy()
predictor_cols = [
    "patient_id", "age", "age_group", "sex", "bmi", "bmi_category", "smoking_status",
    "cancer_type", "genetic_mutation", "tumor_stage", "tumor_stage_numeric", "tumor_size_cm",
    "metastasis_status", "metastasis_binary", "clinical_risk_group", "frailty_risk_pre",
    "chemotherapy_regimen"
]
secondary_outcome_cols = [
    "dosage_mg_m2", "cycles_completed", "nausea_severity", "neutropenia", "neutropenia_binary",
    "severe_toxicity_observed", "tumor_response", "response_favorable", "progressive_disease",
    "overall_survival_months", "survival_12m", "survival_24m"
]
model_ready = model_ready[predictor_cols + secondary_outcome_cols]

clean.to_csv(OUTPUT_CLEAN, index=False)
model_ready.to_csv(OUTPUT_MODEL_READY, index=False)

summary = pd.DataFrame([
    {"indicador": "Registros originales", "valor": original_shape[0]},
    {"indicador": "Columnas originales", "valor": original_shape[1]},
    {"indicador": "Registros dataset limpio", "valor": clean.shape[0]},
    {"indicador": "Columnas dataset limpio", "valor": clean.shape[1]},
    {"indicador": "Patient_ID duplicados", "valor": int(df["Patient_ID"].duplicated().sum())},
    {"indicador": "Genetic_Mutation faltante imputado como Not_reported", "valor": int(df["Genetic_Mutation"].isna().sum())},
    {"indicador": "Chemotherapy_Regimen faltante en original", "valor": int(df["Chemotherapy_Regimen"].isna().sum())},
    {"indicador": "Registros model-ready con régimen conocido", "valor": model_ready.shape[0]},
])
summary.to_csv(OUTPUT_SUMMARY, index=False)
print("Archivos generados:", OUTPUT_CLEAN, OUTPUT_MODEL_READY, OUTPUT_SUMMARY)
