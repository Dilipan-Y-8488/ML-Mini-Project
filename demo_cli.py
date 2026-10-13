"""
Interactive CLI Live Demo Script
================================
Course: UE24CS352A - Machine Learning Mini-Project
Project: Pancreatic Cancer Prognosis using Clinical & Radiomic Data

Provides an instant terminal-based demonstration of:
  1. Cohort summary & Member 1 Naive Bayes 10-Fold CV Threshold Table
  2. Member 1 SMOTE Minority Augmentation summary
  3. Member 2 High-Variance Radiomic Pruning (900 -> 490) & 10-Fold CV CoxPH C-Index Table
  4. Live interactive patient risk & survival curve prediction for sample patients!
"""

import json
import pandas as pd
from lifelines import CoxPHFitter

from src.data_generator import generate_stanford_pancreatic_dataset
from src.naive_bayes_smote import (
    discretize_clinical_features,
    LaplaceMultinomialNaiveBayes,
    augment_dataset_with_smote,
)


def run_cli_demo():
    clinical_df, radiomic_df = generate_stanford_pancreatic_dataset()
    with open("results/metrics_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    print("\n" + "#" * 80)
    print("  LIVE DEMO: PANCREATIC CANCER PROGNOSIS (CLINICAL + RADIOMIC DATA)")
    print("  Course: UE24CS352A Machine Learning Mini-Project")
    print("#" * 80)

    print("\n--- [PART 1: MEMBER 1 — LAPLACE MULTINOMIAL NAIVE BAYES & SMOTE] ---")
    t1 = pd.DataFrame(summary["table1_naive_bayes"])
    print(t1[["Threshold_Label", "High_Risk_Count", "Low_Risk_Count", "Balanced_Accuracy", "Fold_Std"]].to_string(index=False))
    print(f"\n  => Selected Optimal Threshold : {summary['optimal_nb_threshold_days']} days")
    print(f"  => SMOTE Cohort Expansion     : {summary['n_patients_original']} -> {summary['n_patients_augmented']} patients (+{summary['n_synthetic_added']} synthetic high-risk cases)")

    print("\n--- [PART 2: MEMBER 2 — VARIANCE PRUNING, COXPH C-INDEX & KAPLAN-MEIER] ---")
    print(f"  => Radiomic Features Pruned   : {summary['n_radiomic_total']} -> {summary['n_radiomic_retained']} retained ({summary['n_radiomic_removed']} high-error-band >1 removed)")
    t2 = pd.DataFrame(summary["table2_cox_models"])
    print("\n" + t2.to_string(index=False))
    print(f"\n  => Kaplan-Meier Log-Rank Test : Statistic = {summary['logrank_test_statistic']:.2f}, p = {summary['logrank_p_value']:.4e} (< 0.05)")

    print("\n--- [PART 3: LIVE PATIENT PROGNOSIS SIMULATOR] ---")
    X_disc, bins = discretize_clinical_features(clinical_df)
    y_270 = (clinical_df["Survival_Days"].to_numpy() < 270).astype(int)
    nb_model = LaplaceMultinomialNaiveBayes({
        "Stage_Grouping": 4, "Chemotherapy_Time": 2, "Tumor_Width_cm": 4,
        "NCCN_Resectability": 3, "Radiation_Therapy": 2,
    })
    nb_model.fit(X_disc, y_270)

    aug_clin, aug_rad, _ = augment_dataset_with_smote(clinical_df, radiomic_df, optimal_threshold=270)
    live_cols = [
        "Stage_Grouping", "Chemotherapy_Time", "Radiation_Therapy",
        "NCCN_Resectability", "Primary_Tumor_Stage", "KPS_Score",
        "Tumor_Width_cm", "Tumor_Volume_cm3",
    ]
    df_cox = aug_clin[live_cols + ["Survival_Days", "Event_Observed"]].copy()
    df_cox["Radiomic_Composite"] = aug_rad.iloc[:, :8].mean(axis=1).to_numpy()
    cph = CoxPHFitter(penalizer=0.05)
    cph.fit(df_cox, duration_col="Survival_Days", event_col="Event_Observed")

    demo_patients = [
        {
            "Name": "Patient A (Stage III, Locally Advanced, No Post-SBRT Chemo, High Tumor Volume)",
            "Stage_Grouping": 3, "Chemotherapy_Time": 0, "Radiation_Therapy": 1,
            "NCCN_Resectability": 2, "Primary_Tumor_Stage": 4, "KPS_Score": 70,
            "Tumor_Width_cm": 4.5, "Tumor_Volume_cm3": 74.0, "Radiomic_Composite": -0.65,
        },
        {
            "Name": "Patient B (Stage IB, Resectable, Received Post-SBRT Chemo, Small Tumor Volume)",
            "Stage_Grouping": 0, "Chemotherapy_Time": 1, "Radiation_Therapy": 0,
            "NCCN_Resectability": 0, "Primary_Tumor_Stage": 1, "KPS_Score": 90,
            "Tumor_Width_cm": 2.2, "Tumor_Volume_cm3": 21.0, "Radiomic_Composite": 0.55,
        },
    ]

    for p in demo_patients:
        p_df = pd.DataFrame([p])
        p_disc, _ = discretize_clinical_features(p_df, width_bins=bins)
        prob_hr = float(nb_model.predict_proba(p_disc)[0, 1])
        hazard_ratio = float(cph.predict_partial_hazard(p_df[live_cols + ["Radiomic_Composite"]]).iloc[0])
        median_days = float(cph.predict_median(p_df[live_cols + ["Radiomic_Composite"]]))
        cohort_str = "HIGH RISK (< 270d)" if prob_hr >= 0.5 else "LOW RISK (>= 270d)"
        print(f"\n  * {p['Name']}")
        print(f"    -> Naive Bayes High-Risk Prob : {prob_hr*100:.1f}%  [{cohort_str}]")
        print(f"    -> CoxPH Partial Hazard Ratio : {hazard_ratio:.2f}x baseline")
        print(f"    -> Predicted Median Survival  : ~{median_days:.0f} days")

    print("\n" + "#" * 80)
    print("  To launch the interactive web UI live demo, run: streamlit run app.py")
    print("#" * 80 + "\n")


if __name__ == "__main__":
    run_cli_demo()
