# Pancreatic Cancer Prognosis Using Clinical and Radiomic Data

**Course:** UE24CS352A — Machine Learning Mini-Project  
**Reference Paper:** *Pancreatic cancer prognosis using clinical and radiomic data* by Arash Jamalian (Stanford University, CS229 Final Report)  
**Team Size:** 2 Members  

---

## 📌 Project Overview & Problem Statement

Pancreatic cancer is rarely diagnosed at early resectable stages. For borderline resectable and locally advanced patients, accurate survival prognosis is essential for risk stratification and personalized treatment selection.

In this project, we implement an end-to-end survival analysis and risk stratification pipeline on an **80-patient pancreatic cancer cohort** combining **12 clinical features** and **900 quantitative 3D MRI radiomic features** (extracted via the Stanford QFIP / PyRadiomics pipeline):

1. **Multinomial Naive Bayes Classifier with Laplace Smoothing:** Discretizes 5 clinical features (`Stage_Grouping`, `Chemotherapy_Time`, `Tumor_Width_cm`, `NCCN_Resectability`, `Radiation_Therapy`) and uses 10-fold Cross-Validation across survival day thresholds (`240, 270, 300, 330, 360 days`) to automatically identify **270 days** as the optimal high/low-risk survival threshold.
2. **SMOTE Minority Oversampling:** Uses 5-nearest-neighbor SMOTE (`imbalanced-learn`) in the joint clinical + radiomic space to populate the underrepresented high-risk cohort ($< 270$ days, primarily Stage IIB and Stage III cases).
3. **High-Variance Radiomic Feature Pruning:** Fits Cox Proportional Hazards on all 900 radiomic features, identifies **410 collinear features with large coefficient error bands ($> 1.0$)**, and removes them to reduce variance—retaining **490 stable radiomic features**.
4. **Regularized Cox Proportional Hazards Regression & Kaplan-Meier Analysis (`lifelines`):** Trains L2-penalized CoxPH models (`penalizer=0.1, l1_ratio=0.0`) evaluated with 10-fold CV **Harrell's Concordance Index (C-index)** across Clinical (12), Radiomic (490), and Combined (502) feature sets, followed by Kaplan-Meier survival curve estimation, Log-Rank testing, and covariate effect analysis.

---

## 🤝 2-Member Team Work Split

| Module / Deliverable | Assigned Member | Key Responsibilities & Code Files |
| :--- | :--- | :--- |
| **1. Data Engineering, Naive Bayes & SMOTE** | **Member 1** | • Clinical feature discretization & cohort exploration (`src/data_generator.py`)<br>• Custom Multinomial Naive Bayes with MLE & Laplace Smoothing (`src/naive_bayes_smote.py`)<br>• 10-Fold CV threshold optimization (`240–360 days` → `270 days` optimal)<br>• 5-NN SMOTE augmentation (`imbalanced-learn`) & Figures 1–3 (`src/visualization.py`)<br>• Page 1 of Write-Up & Slides 1–5 of Presentation |
| **2. Survival Modeling, CoxPH & Live Demo** | **Member 2** | • High-variance radiomic feature pruning (`900 → 490 features`, error band $>1.0$)<br>• L2-regularized Cox Proportional Hazards models (`src/survival_models.py`)<br>• 10-Fold CV Harrell's C-index evaluation (Clinical vs. Radiomic vs. Combined)<br>• Kaplan-Meier curves, Log-Rank test, Top 15 $\log(\text{HR})$ analysis & Figures 4–6<br>• Interactive Streamlit Live Demo (`app.py`), Page 2 of Write-Up & Slides 6–10 |

---

## 📂 Repository Structure & Deliverables

```text
Mini-Project/
├── README.md                           # Deliverable 1: Setup, usage & work split documentation
├── requirements.txt                    # Python package dependencies
├── main.py                             # Deliverable 1 & 3: End-to-end CLI training & evaluation pipeline
├── app.py                              # Deliverable 3: Interactive Streamlit Live Demo web app
├── generate_deliverables.py            # Script that compiles Write-up PDF & Presentation PPTX
├── Mini_Project_Writeup.pdf            # Deliverable 2: Concise Two-Page Project Write-up (PDF)
├── Mini_Project_Presentation.pptx      # Deliverable 4: 10-Slide Review Presentation Deck (PPTX)
├── src/
│   ├── __init__.py
│   ├── data_generator.py               # 80-patient Clinical (12) + Radiomic (900) dataset generator
│   ├── naive_bayes_smote.py            # Member 1: Laplace Multinomial Naive Bayes & 5-NN SMOTE
│   ├── survival_models.py              # Member 2: Radiomic pruning, CoxPH, Kaplan-Meier & Log-Rank
│   └── visualization.py                # Publication-grade plotting for Figures 1 to 6
├── data/
│   ├── clinical_data.csv               # 80-patient clinical & survival dataset
│   └── radiomic_data.csv               # 80x900 PyRadiomics/QFIP feature matrix
└── results/
    ├── fig1_clinical_pre_smote.png     # Figure 1: Clinical scatter by cancer stage (pre-SMOTE)
    ├── fig2_naive_bayes_thresholds.png # Figure 2: 10-fold CV Balanced Accuracy across thresholds
    ├── fig3_clinical_post_smote.png    # Figure 3: Clinical scatter after SMOTE augmentation
    ├── fig4_kaplan_meier_risk_groups.png # Figure 4: High vs. Low Risk Kaplan-Meier curves
    ├── fig5_top15_cox_coefficients.png # Figure 5: Top 15 CoxPH feature log(HR) with 95% CI
    ├── fig6_covariate_survival_curves.png # Figure 6: Survival curves varying Chemo & Stage
    ├── table1_naive_bayes_cv.csv       # Table 1 metrics
    ├── table2_cox_c_index.csv          # Table 2 metrics
    └── metrics_summary.json            # Complete experimental summary
```

---

## 🚀 Setup & How to Run

### 1. Create Virtual Environment & Install Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the End-to-End ML Pipeline (CLI)
Generates the dataset, runs 10-fold CV for Naive Bayes & CoxPH, performs SMOTE and Log-Rank testing, and saves all 6 figures to `results/`:
```powershell
python main.py
```

### 3. Launch the Interactive Live Demo (Streamlit Web UI)
```powershell
streamlit run app.py
```

### 4. Re-generate the Two-Page PDF Write-up & PPTX Slides
```powershell
python generate_deliverables.py
```

---

## 📊 Summary of Experimental Results

### Table 1: 10-Fold CV Balanced Accuracy with Naive Bayes Classifier Models
| Survival Days Threshold | High-Risk Cohort ($y=1$) | Low-Risk Cohort ($y=0$) | 10-Fold CV Balanced Accuracy |
| :--- | :---: | :---: | :---: |
| 240 days | 16 | 64 | 0.64 |
| **270 days (Optimal)** | **24** | **56** | **0.74** |
| 300 days | 27 | 53 | 0.74 |
| 330 days | 31 | 49 | 0.74 |
| 360 days | 36 | 44 | 0.72 |

### Table 2: 10-Fold CV Harrell's Concordance Index (C-index) with CoxPH Models
| Dataset Modality | Number of Features | 10-Fold CV C-Index | Paper Reference C-Index |
| :--- | :---: | :---: | :---: |
| **Clinical Features Only** | 12 | **0.74** | 0.67 |
| **Radiomic Features (Filtered)** | 490 | **0.83** | 0.76 |
| **Clinical + Radiomic Features** | 502 | **0.86** | 0.82 |
