# Dataset Description:
This dataset contains around 50,000 records of patient data related to chemotherapy treatment and clinical outcomes. The data captures important demographic, genetic, tumor characteristics, treatment details, side effects, and survival outcomes that are essential for analyzing chemotherapy effectiveness and patient responses.

# Columns Description:
## 1. Patient Demographics:
Patient_ID → Unique identifier for each patient
Age → Patient's age (30–85 years)
Sex → Male or Female
BMI → Body Mass Index (18.5–35.0)
Smoking_Status → Smoking history categorized as Never, Former, or Current
## 2. Genetic & Molecular Data:
Cancer_Type → Type of cancer (Breast, Lung, Colon, Leukemia, Lymphoma)
Genetic_Mutation → Key genetic mutations associated with cancer (TP53, BRCA1, EGFR, KRAS, None)
## 3. Clinical & Tumor Characteristics:
Tumor_Stage → Cancer stage (I, II, III, IV)
Tumor_Size → Tumor size in cm (1.0–10.0)
Metastasis_Status → Indicates whether cancer has spread (Yes/No)
## 4. Chemotherapy Treatment Details:
Chemotherapy_Regimen → Treatment protocol (FOLFOX, ABVD, CHOP, Gemcitabine, None)
Dosage (mg/m²) → Chemotherapy drug dosage per body surface area (50–600 mg/m²)
Cycles_Completed → Number of chemotherapy cycles completed (1–8 cycles)
## 5. Side Effects & Toxicity Scores:
Nausea_Severity → Nausea severity graded from 1 (mild) to 5 (severe)
Neutropenia → Indicator of low white blood cell count (Yes/No)
## 6. Treatment Outcomes:
Tumor_Response → Categorized as Complete, Partial, Stable, or Progressive response
Overall_Survival_Months → Patient survival duration in months (6 months to 10 years)
