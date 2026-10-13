# Pancreatic Cancer Prognosis Using Clinical and Radiomic Data

**Course:** UE24CS352A — Machine Learning  
**Project:** Problem Statement 6  
**Reference Paper:** A. Jamalian, "Pancreatic cancer prognosis using clinical and radiomic data," CS229 Project Final Report, Stanford University, 2020 (not redistributed here).

---

## Dataset Disclaimer

> [!IMPORTANT]
> **Synthetic Data Notice:** The original Stanford Cancer Center dataset evaluated in Jamalian (2020) is proprietary and protected under a Non-Disclosure Agreement (NDA). All patient records in `data/clinical_data.csv` and `data/radiomic_data.csv` are **synthetic**, generated via `src/data_generator.py` to replicate the structure, feature distributions, and dimensionality of the paper's cohort (80 synthetic patients, 12 clinical variables, 900 radiomic features). These records are **NOT real patient data**. Consequently, results obtained here are **NOT directly comparable** to the paper's published metrics and must not be interpreted as outperforming the original study.

---

## Team & Work Split

| Team Member | SRN | Primary Responsibilities & Code Modules |
| :--- | :--- | :--- |
| **Dilipan Y** | `PES1UG24AM092` | • Clinical feature discretization & exploratory data analysis (`src/data_generator.py`)<br>• Custom Multinomial Naive Bayes classifier with Laplace smoothing (`src/naive_bayes_smote.py`)<br>• 10-fold CV threshold optimization across 240–360 days with deterministic tie-breaking (selecting 270d)<br>• 5-NN SMOTE minority oversampling on joint feature space (`80 -> 112` cases)<br>• Generated Figures 1, 2, and 3 |
| **Sai Hemanth** | `PES1UG24AM101` | • Radiomic feature pruning: removing 410 high-variance collinear features (`900 -> 490` retained)<br>• Regularized Cox Proportional Hazards regression with L2 penalty (`penalizer=0.1, l1_ratio=0.0`) (`src/survival_models.py`)<br>• 10-fold CV Harrell's Concordance Index (C-index) evaluation (honest leak-free vs. leaky comparison)<br>• Kaplan-Meier survival curves, Log-Rank testing, and Top 15 hazard feature analysis (`results/fig4..6`)<br>• Interactive Streamlit live demo application (`app.py`) |

---

## Project Overview

Pancreatic ductal adenocarcinoma is rarely detected at early resectable stages. For patients with borderline resectable or locally advanced tumors, accurate survival prognosis is vital for personalizing treatment plans (e.g., assessing chemotherapy timing and radiation fractionation).

This project implements an end-to-end multimodal machine learning pipeline on a synthetic 80-patient cohort combining **12 clinical variables** and **900 simulated quantitative 3D MRI radiomic features** (mimicking PyRadiomics/QFIP feature extraction):

1. **Risk Threshold Selection (Naive Bayes):** Discretizes 5 clinical features (`Stage_Grouping`, `Chemotherapy_Time`, `Tumor_Width_cm`, `NCCN_Resectability`, `Radiation_Therapy`) and trains a Multinomial Naive Bayes model with Laplace smoothing over 240, 270, 300, 330, and 360-day survival thresholds. Thresholds 270, 300, and 330 days tie at 0.74 balanced accuracy. The 270-day threshold is selected deterministically via the explicit tie-breaking rule: lowest cross-validation standard deviation across folds (0.105 for 270d/300d vs. 0.142 for 330d), then smallest threshold (270d < 300d) as the earliest clinical risk boundary.
2. **Class Imbalance Augmentation (SMOTE):** Using the 270-day boundary, 5-nearest-neighbor SMOTE is applied across the 912-dimensional joint feature space to synthesize high-risk Stage IIB and Stage III cases, expanding the cohort from 80 to 112 patients.
3. **High-Variance Radiomic Pruning:** Fitting an initial Cox model on all 900 radiomic features revealed 410 features with large coefficient standard errors (>1.0) due to severe collinearity. Removing them left 490 robust radiomic descriptors.
4. **Regularized Cox Proportional Hazards Regression:** Evaluated with 10-fold CV Harrell's Concordance Index (C-index) using an L2 penalty (`penalizer=0.1, l1_ratio=0.0`). The combined model (502 features) outperformed individual clinical and radiomic models in both honest leak-free CV (0.80) and paper-style leaky CV (0.86).
5. **Kaplan-Meier & Risk Stratification:** Splitting patients by median partial hazard score produced statistically significant survival separation (Log-Rank statistic = 135.11, p < 0.001).

> [!NOTE]
> **Figure 2 Distinction:** In this repository, Figure 2 displays the Naive Bayes 10-fold cross-validation balanced accuracy bar chart across survival thresholds, documenting the 0.74 tie and tie-breaking rule. In Jamalian's original paper, Figure 2 illustrates the Naive Bayes graphical directed acyclic model.

---

## Repository Structure

```text
ML-Mini-Project/
├── README.md                           # Project documentation and instructions
├── requirements.txt                    # Pinned Python dependencies
├── main.py                             # End-to-end ML pipeline (training, CV, figure generation)
├── app.py                              # Interactive Streamlit live demo application
├── demo_cli.py                         # Fast terminal live demo script
├── Mini_Project_Writeup.pdf            # Two-page academic project summary (PDF)
├── Presentation.pptx                   # Review presentation slide deck (PPTX)
├── tools/
│   ├── make_writeup.py                 # Reproducible PDF write-up generator script
│   └── make_presentation.py            # Reproducible PowerPoint slide deck generator script
├── src/
│   ├── __init__.py
│   ├── data_generator.py               # Synthetic clinical & radiomic dataset synthesis
│   ├── naive_bayes_smote.py            # Naive Bayes threshold selection & SMOTE augmentation
│   ├── survival_models.py              # Radiomics pruning, CoxPH regression & Kaplan-Meier
│   └── visualization.py                # Plotting utilities for Figures 1 to 6
├── data/
│   ├── README.md                       # Documentation of synthetic generation methodology
│   ├── clinical_data.csv               # Synthetic 80-patient clinical features and survival records
│   └── radiomic_data.csv               # Synthetic 80x900 radiomic feature matrix (simulated)
└── results/
    ├── fig1_clinical_pre_smote.png     # Figure 1: Clinical scatter by cancer stage (pre-SMOTE)
    ├── fig2_naive_bayes_thresholds.png # Figure 2: Naive Bayes 10-fold CV balanced accuracy (tie illustrated)
    ├── fig3_clinical_post_smote.png    # Figure 3: Clinical scatter after SMOTE augmentation
    ├── fig4_kaplan_meier_risk_groups.png # Figure 4: Kaplan-Meier high vs. low risk curves
    ├── fig5_top15_cox_coefficients.png # Figure 5: Top 15 CoxPH log(HR) coefficients with 95% CI
    ├── fig6_covariate_survival_curves.png # Figure 6: Covariate effect curves (Chemo & Stage)
    ├── table1_naive_bayes_cv.csv       # Table 1 cross-validation metrics & selection status
    ├── table2_cox_c_index.csv          # Table 2 Honest leak-free CoxPH concordance index results
    ├── table2b_leakage_comparison.csv  # Table 2b Side-by-side leaky vs. leak-free CV comparison
    ├── top15_cox_features.csv          # Top 15 prognostic features summary
    └── metrics_summary.json            # Machine-readable evaluation summary
```

---

## Setup and How to Run

**Python Version:** Python 3.10+ (tested on Python 3.14.7).

### 1. Installation

Create a virtual environment and install dependencies:

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# Linux / macOS (bash / zsh)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Full Pipeline

Executes dataset generation, 10-fold cross-validation (both leak-free and paper-style leaky), feature pruning, and exports all tables and figures to `results/`:

```powershell
python main.py
```

### 3. Launch Interactive Web Demo

Starts the Streamlit application with the interactive patient risk predictor and cohort explorer:

```powershell
streamlit run app.py
```

### 4. Run Command-Line Demo

Runs a quick terminal demonstration of threshold selection, CoxPH C-index benchmarks (including Table 2b leakage comparison), and sample patient predictions:

```powershell
python demo_cli.py
```

---

## Experimental Results

### Table 1: Naive Bayes 10-Fold CV Balanced Accuracy across Risk Thresholds

| Survival Threshold | High-Risk ($y=1$) | Low-Risk ($y=0$) | 10-Fold CV Balanced Accuracy | Paper (real data, for context only) | Selection Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| 240 days | 18 | 62 | 0.64 ± 0.17 | 0.53 | Suboptimal |
| **270 days (Optimal)** | **24** | **56** | **0.74 ± 0.11** | **0.69** | **Selected Optimal (Tied at 0.74; lowest std 0.105, smallest cutoff)** |
| 300 days | 24 | 56 | 0.74 ± 0.11 | 0.61 | Tied at 0.74 (std=0.105; discarded in favor of smaller 270d cutoff) |
| 330 days | 25 | 55 | 0.74 ± 0.14 | 0.57 | Tied at 0.74 (std=0.142; discarded due to higher fold variance) |
| 360 days | 26 | 54 | 0.72 ± 0.17 | 0.61 | Suboptimal |

* **Threshold Selection Rule:** Thresholds 270, 300, and 330 days tie at 0.74 mean balanced accuracy. Tie-break rule 1 (lowest fold standard deviation across splits: 0.105 vs. 0.142) eliminates 330 days. Tie-break rule 2 (smallest threshold: 270d < 300d) selects 270 days as the earliest and most conservative high-risk cutoff.

### Table 2: Cox Proportional Hazards Honest Leak-Free 10-Fold CV Concordance Index (C-Index)

| Model Feature Set | Number of Features | 10-Fold CV C-Index | Paper (real data, for context only) |
| :--- | :---: | :---: | :---: |
| **Clinical Features** | 12 | **0.71 ± 0.09** | 0.67 |
| **Radiomic Features (Pruned)** | 490 | **0.77 ± 0.11** | 0.76 |
| **Clinical and Radiomic Features** | 502 | **0.80 ± 0.11** | **0.82** |

* Log-Rank Test between high-risk and low-risk cohorts: **statistic = 135.11, p = 3.13e-31 (< 0.05)**.
* Key Clinical Biomarkers: Chemotherapy Time (Choice = After SBRT) is strongly protective, while higher Primary Tumor stage (T2/T3/T4) significantly increases hazard.

### Table 2b: Cross-Validation Data Leakage Comparison

| Model Feature Set | Number of Features | Honest Leak-Free C-Index | Paper-Style Leaky C-Index | Leakage Inflation | Paper Context (Real Data) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Clinical Features** | 12 | **0.71 ± 0.09** | 0.74 ± 0.10 | +0.03 | 0.67 |
| **Radiomic Features** | 490 | **0.77 ± 0.11** | 0.83 ± 0.08 | +0.06 | 0.76 |
| **Clinical and Radiomic Features** | 502 | **0.80 ± 0.11** | 0.86 ± 0.07 | +0.06 | 0.82 |

> [!NOTE]
> **Why Leak-Free C-Indices are Lower:** In the paper-style leaky pipeline, SMOTE minority oversampling is executed on the full dataset before cross-validation splitting, and the 410-feature pruning is determined using all patient records. Synthetic samples (which interpolate between original patients) therefore land in both training and test folds, artificially inflating the C-index by +0.03 to +0.06. In our leak-free pipeline, SMOTE and radiomic pruning are strictly confined to each CV training split, and test folds contain exclusively original, unseen patient records. The leak-free figures (0.71, 0.77, 0.80) represent the honest, generalizable performance of the pipeline.

---

## Limitations

1. **Synthetic Data:** The dataset is synthetic (as the original Stanford cohort is protected under NDA). Findings demonstrate machine learning methodology and cannot be interpreted as clinical evidence or directly compared to the paper.
2. **Small Cohort Size ($n = 80$):** High-dimensional survival modeling on 80 patients has inherently high sampling variance, reflected in standard deviations of ±0.09 to ±0.11 across CV folds.
3. **SMOTE on Survival Data:** Applying standard Euclidean SMOTE to survival times and binary event indicators interpolates censored observations without accounting for underlying survival distribution hazard functions.
4. **Proportional Hazards Assumption:** The proportional hazards assumption (that hazard ratios remain constant over time) was not formally evaluated via Schoenfeld residual testing.
