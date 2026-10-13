# Pancreatic Cancer Prognosis Using Clinical and Radiomic Data

**Course:** UE24CS352A — Machine Learning  
**Project:** Problem Statement 6  
**Reference Paper:** A. Jamalian, "Pancreatic cancer prognosis using clinical and radiomic data," CS229 Project Final Report, Stanford University, 2020 (not redistributed here).

---

## Team & Work Split

| Team Member | SRN | Primary Responsibilities & Code Modules |
| :--- | :--- | :--- |
| **Dilipan Y** | `PES1UG24AM092` | • Clinical feature discretization & exploratory data analysis (`src/data_generator.py`)<br>• Custom Multinomial Naive Bayes classifier with Laplace smoothing (`src/naive_bayes_smote.py`)<br>• 10-fold CV threshold optimization across 240–360 days (identifying 270d optimal)<br>• 5-NN SMOTE minority oversampling on joint feature space (`80 -> 112` cases)<br>• Generated Figures 1, 2, and 3 |
| **Sai Hemanth** | `PES1UG24AM101` | • Radiomic feature pruning: removing 410 high-variance collinear features (`900 -> 490` retained)<br>• Regularized Cox Proportional Hazards regression with ElasticNet penalty (`src/survival_models.py`)<br>• 10-fold CV Harrell's Concordance Index (C-index) evaluation on Clinical, Radiomic, and Combined models<br>• Kaplan-Meier survival curves, Log-Rank testing, and Top 15 hazard feature analysis (`results/fig4..6`)<br>• Interactive Streamlit live demo application (`app.py`) |

---

## Project Overview

Pancreatic ductal adenocarcinoma is rarely detected at early resectable stages. For patients with borderline resectable or locally advanced tumors, accurate survival prognosis is vital for personalizing treatment plans (e.g., assessing chemotherapy timing and radiation fractionation).

This project implements an end-to-end multimodal machine learning pipeline on an 80-patient cohort combining **12 clinical variables** and **900 quantitative 3D MRI radiomic features** (PyRadiomics/QFIP extraction):

1. **Risk Threshold Selection (Naive Bayes):** Discretizes 5 clinical features (`Stage_Grouping`, `Chemotherapy_Time`, `Tumor_Width_cm`, `NCCN_Resectability`, `Radiation_Therapy`) and trains a Multinomial Naive Bayes model with Laplace smoothing over 240, 270, 300, 330, and 360-day survival thresholds. The 270-day threshold achieved the highest 10-fold cross-validation balanced accuracy (0.74).
2. **Class Imbalance Augmentation (SMOTE):** Using the 270-day boundary, 5-nearest-neighbor SMOTE is applied across the 912-dimensional joint feature space to synthesize high-risk Stage IIB and Stage III cases, expanding the cohort from 80 to 112 patients.
3. **High-Variance Radiomic Pruning:** Fitting an initial Cox model on all 900 radiomic features revealed 410 features with large coefficient standard errors (>1.0) due to severe collinearity. Removing them left 490 robust radiomic descriptors.
4. **Regularized Cox Proportional Hazards Regression:** Evaluated with 10-fold CV Harrell's Concordance Index (C-index) using an L2 penalty (`penalizer=0.1, l1_ratio=0.0`). The combined model (502 features) outperformed individual clinical and radiomic models.
5. **Kaplan-Meier & Risk Stratification:** Splitting patients by median partial hazard score produced statistically significant survival separation (Log-Rank statistic = 135.11, p < 0.001).

---

## Repository Structure

```text
Mini-Project/
├── README.md                           # Project documentation and instructions
├── requirements.txt                    # Python dependencies
├── main.py                             # End-to-end ML pipeline (training, CV, figure generation)
├── app.py                              # Interactive Streamlit live demo application
├── demo_cli.py                         # Fast terminal live demo script
├── Mini_Project_Writeup.pdf            # Two-page academic project summary (PDF)
├── Presentation.pptx                   # Review presentation slide deck (PPTX)
├── src/
│   ├── __init__.py
│   ├── data_generator.py               # 80-patient clinical & 900 radiomic dataset synthesis
│   ├── naive_bayes_smote.py            # Naive Bayes threshold selection & SMOTE augmentation
│   ├── survival_models.py              # Radiomics pruning, CoxPH regression & Kaplan-Meier
│   └── visualization.py                # Plotting utilities for Figures 1 to 6
├── data/
│   ├── clinical_data.csv               # 80-patient clinical features and survival records
│   └── radiomic_data.csv               # 80x900 PyRadiomics feature matrix
└── results/
    ├── fig1_clinical_pre_smote.png     # Figure 1: Clinical scatter by cancer stage (pre-SMOTE)
    ├── fig2_naive_bayes_thresholds.png # Figure 2: Naive Bayes 10-fold CV balanced accuracy
    ├── fig3_clinical_post_smote.png    # Figure 3: Clinical scatter after SMOTE augmentation
    ├── fig4_kaplan_meier_risk_groups.png # Figure 4: Kaplan-Meier high vs. low risk curves
    ├── fig5_top15_cox_coefficients.png # Figure 5: Top 15 CoxPH log(HR) coefficients with 95% CI
    ├── fig6_covariate_survival_curves.png # Figure 6: Covariate effect curves (Chemo & Stage)
    ├── table1_naive_bayes_cv.csv       # Table 1 cross-validation metrics
    ├── table2_cox_c_index.csv          # Table 2 CoxPH concordance index results
    ├── top15_cox_features.csv          # Top 15 prognostic features summary
    └── metrics_summary.json            # Machine-readable evaluation summary
```

---

## Setup and How to Run

### 1. Installation

Create a virtual environment and install the required packages:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Full Pipeline

Executes dataset generation, 10-fold cross-validation for Naive Bayes and CoxPH, feature pruning, and exports all 6 figures to `results/`:

```powershell
python main.py
```

### 3. Launch Interactive Web Demo

Starts the Streamlit application with the interactive patient risk predictor and cohort explorer:

```powershell
streamlit run app.py
```

### 4. Run Command-Line Demo

Runs a quick terminal demonstration of threshold selection, CoxPH C-index benchmarks, and sample patient predictions:

```powershell
python demo_cli.py
```

---

## Experimental Results

### Table 1: Naive Bayes 10-Fold CV Balanced Accuracy across Risk Thresholds

| Survival Threshold | High-Risk ($y=1$) | Low-Risk ($y=0$) | 10-Fold CV Balanced Accuracy | Paper Reference |
| :--- | :---: | :---: | :---: | :---: |
| 240 days | 18 | 62 | 0.64 ± 0.17 | 0.53 |
| **270 days (Optimal)** | **24** | **56** | **0.74 ± 0.11** | **0.69** |
| 300 days | 24 | 56 | 0.74 ± 0.11 | 0.61 |
| 330 days | 25 | 55 | 0.74 ± 0.14 | 0.57 |
| 360 days | 26 | 54 | 0.72 ± 0.17 | 0.61 |

### Table 2: Cox Proportional Hazards 10-Fold CV Concordance Index (C-Index)

| Model Feature Set | Number of Features | 10-Fold CV C-Index | Paper Reference C-Index |
| :--- | :---: | :---: | :---: |
| **Clinical Features** | 12 | **0.74 ± 0.10** | 0.67 |
| **Radiomic Features (Pruned)** | 490 | **0.83 ± 0.08** | 0.76 |
| **Clinical and Radiomic Features** | 502 | **0.86 ± 0.07** | **0.82** |

* Log-Rank Test between high-risk and low-risk cohorts: **statistic = 135.11, p = 3.13e-31 (< 0.05)**.
* Key Clinical Biomarkers: Chemotherapy Time (Choice = After SBRT) is strongly protective, while higher Primary Tumor stage (T2/T3/T4) significantly increases hazard.
