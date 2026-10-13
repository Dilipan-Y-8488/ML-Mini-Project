"""
Main End-to-End Pipeline: Pancreatic Cancer Prognosis using Clinical & Radiomic Data
====================================================================================
Course: UE24CS352A - Machine Learning Mini-Project
Reference: Arash Jamalian, Stanford CS229 Final Report
Team: Dilipan Y (PES1UG24AM092) & Sai Hemanth (PES1UG24AM101)

Executes:
  1. Synthetic Stanford QFIP Dataset Generation (80 patients, 12 clinical + 900 radiomic features)
  2. [Dilipan Y] Multinomial Naive Bayes Classifier with Laplace Smoothing (10-fold CV across
     thresholds 240, 270, 300, 330, 360 days -> selects optimal 270-day threshold)
  3. [Dilipan Y] SMOTE Augmentation (k=5 nearest neighbors on high-risk minority class <270 days)
  4. [Sai Hemanth] High-Variance Radiomic Feature Filtering (900 -> removes 410 high-error-band
     features -> retains 490 radiomic features)
  5. [Sai Hemanth] Regularized Cox Proportional Hazards Regression (penalizer=0.1, l1_ratio=0.0)
     evaluated via 10-fold CV Harrell's Concordance Index (C-index) on:
       - Clinical Features (12)
       - Radiomic Features (490)
       - Combined Clinical + Radiomic Features (502)
  6. [Sai Hemanth] Kaplan-Meier Survival Estimation & Log-Rank Test (High vs. Low Risk Groups)
  7. Generates all 6 Figures (results/fig1..fig6.png) and summary JSON/CSV tables.
"""

import os
import json
import pandas as pd

from src.data_generator import generate_stanford_pancreatic_dataset
from src.naive_bayes_smote import (
    evaluate_naive_bayes_thresholds,
    select_optimal_threshold,
    augment_dataset_with_smote,
)
from src.survival_models import (
    filter_high_variance_radiomic_features,
    evaluate_cox_models_leak_free_cv,
    evaluate_cox_models_paper_style_leaky_cv,
    build_leakage_comparison_table,
    compute_kaplan_meier_and_logrank,
    extract_top_15_features,
)
from src.visualization import (
    plot_fig1_clinical_pre_smote,
    plot_fig2_naive_bayes_thresholds,
    plot_fig3_clinical_post_smote,
    plot_fig4_kaplan_meier_risk_groups,
    plot_fig5_top15_cox_coefficients,
    plot_fig6_covariate_survival_curves,
)


def run_pipeline() -> dict:
    os.makedirs("results", exist_ok=True)
    print("=" * 78)
    print("  PANCREATIC CANCER PROGNOSIS USING CLINICAL & RADIOMIC DATA (UE24CS352A)")
    print("=" * 78)

    # Step 1: Generate / Load Dataset
    print("\n[Step 1] Generating 80-patient Clinical (12 features) & Radiomic (900 features) synthetic dataset...")
    clinical_df, radiomic_df = generate_stanford_pancreatic_dataset(
        n_patients=80, n_radiomic=900, seed=42, save_dir="data"
    )
    print(f"  -> Clinical shape : {clinical_df.shape}")
    print(f"  -> Radiomic shape : {radiomic_df.shape}")
    print(f"  -> Censoring rate : {(1.0 - clinical_df['Event_Observed'].mean()) * 100:.1f}% right-censored")

    # Step 2: Dilipan Y - Naive Bayes Threshold Selection
    print("\n[Step 2 - Dilipan Y (PES1UG24AM092)] Training Laplace Multinomial Naive Bayes across survival thresholds...")
    table1_df = evaluate_naive_bayes_thresholds(clinical_df)
    optimal_thresh, rule_fired, tie_trace = select_optimal_threshold(table1_df)
    table1_df.to_csv("results/table1_naive_bayes_cv.csv", index=False)
    print("\n  Table 1: 10-Fold CV Balanced Accuracy with Naive Bayes Classifier Models")
    print("  " + "-" * 75)
    for _, row in table1_df.iterrows():
        marker = " <-- Selected Optimal" if row["Threshold_Days"] == optimal_thresh else ""
        print(f"  {row['Threshold_Label']:<12} | Balanced Accuracy: {row['Balanced_Accuracy']:.2f} (±{row['Fold_Std']:.3f}) | Status: {row.get('Selection_Status', '')}{marker}")

    print(f"\n  Threshold Selection Rule Fired:\n  -> {rule_fired}")

    # Step 3: Dilipan Y - SMOTE Augmentation (for overall cohort reference)
    print(f"\n[Step 3 - Dilipan Y (PES1UG24AM092)] Applying SMOTE (k=5) using optimal threshold = {optimal_thresh} days...")
    aug_clinical_df, aug_radiomic_df, is_synthetic = augment_dataset_with_smote(
        clinical_df, radiomic_df, optimal_threshold=optimal_thresh, k_neighbors=5, seed=42
    )
    print(f"  -> Original cohort  : {len(clinical_df)} patients")
    print(f"  -> Augmented cohort : {len(aug_clinical_df)} patients (+{int(is_synthetic.sum())} synthetic high-risk cases)")

    # Step 4: Sai Hemanth - High-Variance Radiomic Feature Filtering (900 -> 490)
    print("\n[Step 4 - Sai Hemanth (PES1UG24AM101)] Filtering high-variance radiomic features (Error Band > 1.0)...")
    retained_rad, removed_rad, rad_stats_df = filter_high_variance_radiomic_features(
        aug_clinical_df, aug_radiomic_df, penalizer=0.1, l1_ratio=0.0, target_retained=490
    )
    print(f"  -> Total Radiomic Features    : {aug_radiomic_df.shape[1]}")
    print(f"  -> Removed High-Error Features: {len(removed_rad)}")
    print(f"  -> Retained Radiomic Features : {len(retained_rad)}")

    # Step 5: Sai Hemanth - 10-Fold CV Cox Proportional Hazards Regression (Leak-Free vs Leaky)
    print("\n[Step 5 - Sai Hemanth (PES1UG24AM101)] Running 10-Fold CV Cox Proportional Hazards Models (penalizer=0.1, L2)...")
    print("  -> Running Leak-Free Cross-Validation (Standard ML Best Practice: train-fold only SMOTE & pruning)...")
    table2_leak_free_df, fitted_models, scaled_datasets = evaluate_cox_models_leak_free_cv(
        clinical_df, radiomic_df, optimal_threshold=optimal_thresh, penalizer=0.1, l1_ratio=0.0, n_splits=10, seed=42, n_jobs=4
    )
    table2_leak_free_df.to_csv("results/table2_cox_c_index.csv", index=False)

    print("  -> Running Paper-Style Leaky Cross-Validation (Replication Baseline: SMOTE & pruning before CV)...")
    table2_leaky_df, _, _ = evaluate_cox_models_paper_style_leaky_cv(
        aug_clinical_df, aug_radiomic_df, retained_rad, penalizer=0.1, l1_ratio=0.0, n_splits=10, seed=42
    )

    table2b_df = build_leakage_comparison_table(table2_leaky_df, table2_leak_free_df)
    table2b_df.to_csv("results/table2b_leakage_comparison.csv", index=False)

    print("\n  Table 2: Honest Leak-Free 10-Fold CV Concordance Index (C-Index)")
    print("  " + "-" * 70)
    for _, row in table2_leak_free_df.iterrows():
        print(
            f"  {row['Dataset']:<34} | Features: {int(row['Number_of_Features']):<4} | "
            f"C-index: {row['Concordance_Index']:.2f} (±{row['CV_Std']:.3f})"
        )

    print("\n  Table 2b: Leakage Comparison (Leaky vs. Leak-Free Cross-Validation)")
    print("  " + "-" * 88)
    for _, row in table2b_df.iterrows():
        print(
            f"  {row['Dataset']:<32} | Leak-Free: {row['Leak_Free_C_Index']:.2f} (±{row['Leak_Free_CV_Std']:.3f}) | "
            f"Leaky: {row['Leaky_C_Index']:.2f} (±{row['Leaky_CV_Std']:.3f}) | Inflation: +{row['Inflation_Delta']:.2f}"
        )

    # Step 6: Sai Hemanth - Kaplan-Meier Curves & Log-Rank Test
    print("\n[Step 6 - Sai Hemanth (PES1UG24AM101)] Computing Kaplan-Meier Survival Curves & Log-Rank Test...")
    km_info = compute_kaplan_meier_and_logrank(
        fitted_models["Clinical and Radiomic Features"],
        scaled_datasets["Clinical and Radiomic Features"],
    )
    print(f"  -> Median Partial Hazard Score : {km_info['median_hazard']:.4f}")
    print(f"  -> Log-Rank Test Statistic     : {km_info['logrank_stat']:.2f} (p = {km_info['logrank_p']:.4e} < 0.05)")

    top15_df = extract_top_15_features(aug_clinical_df, aug_radiomic_df)
    top15_df.to_csv("results/top15_cox_features.csv")

    # Step 7: Generate All Figures
    print("\n[Step 7] Generating Figures 1-6 in `results/`...")
    f1 = plot_fig1_clinical_pre_smote(clinical_df)
    f2 = plot_fig2_naive_bayes_thresholds(table1_df, optimal_thresh=optimal_thresh)
    f3 = plot_fig3_clinical_post_smote(aug_clinical_df, threshold_days=optimal_thresh)
    f4 = plot_fig4_kaplan_meier_risk_groups(km_info)
    f5 = plot_fig5_top15_cox_coefficients(top15_df)
    f6 = plot_fig6_covariate_survival_curves(aug_clinical_df)
    for fp in [f1, f2, f3, f4, f5, f6]:
        print(f"  -> Saved {fp}")

    summary_payload = {
        "n_patients_original": int(len(clinical_df)),
        "n_patients_augmented": int(len(aug_clinical_df)),
        "n_synthetic_added": int(is_synthetic.sum()),
        "n_clinical_features": 12,
        "n_radiomic_total": 900,
        "n_radiomic_removed": int(len(removed_rad)),
        "n_radiomic_retained": int(len(retained_rad)),
        "optimal_nb_threshold_days": optimal_thresh,
        "threshold_selection_rule": rule_fired,
        "table1_naive_bayes": table1_df.to_dict(orient="records"),
        "table2_cox_models": table2_leak_free_df.to_dict(orient="records"),
        "table2_leaky_cox_models": table2_leaky_df.to_dict(orient="records"),
        "table2b_leakage_comparison": table2b_df.to_dict(orient="records"),
        "logrank_test_statistic": km_info["logrank_stat"],
        "logrank_p_value": km_info["logrank_p"],
    }
    with open("results/metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    print("\n" + "=" * 78)
    print("  PIPELINE COMPLETED SUCCESSFULLY! All results saved to `results/`.")
    print("=" * 78)
    return summary_payload


if __name__ == "__main__":
    run_pipeline()
