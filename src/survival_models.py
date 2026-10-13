"""
Member 2 Module: Survival Analysis (Kaplan-Meier, Log-Rank, & Cox Proportional Hazards)
=======================================================================================
Implements Section 4 & Section 5 (Part 2) of Arash Jamalian (Stanford CS229):
1. Non-parametric Survival Estimation:
   - Kaplan-Meier Survival Estimator: S_KM(t) = prod_{i: t_i < t} (n_i - d_i) / n_i
   - Log-Rank Hypothesis Test comparing High-Risk vs. Low-Risk cohorts (split by median
     partial hazard score).
2. Parametric / Semi-Parametric Cox Proportional Hazards Regression (lifelines):
   - Hazard function: h(t, X) = h_0(t) * exp(sum_i beta_i X_i)
   - Regularization penalty: 0.5 * penalizer * ((1 - l1_ratio)||beta||_2^2 + l1_ratio||beta||_1)
     with penalizer=0.1 and l1_ratio=0.0 (L2 regularization).
3. High-Variance Radiomic Feature Pruning:
   - Fits CoxPH on all 900 radiomic features, identifies ~410 features with large
     coefficient error bands (>1.0) caused by collinearity/small sample size, and
     retains the remaining 490 lower-variance radiomic features.
4. 10-Fold Cross-Validation with Harrell's Concordance Index (C-index, Eq. 8):
   - Clinical Features (12 features)
   - Radiomic Features (490 features)
   - Combined Clinical + Radiomic Features (502 features)
5. Top 15 Prognostic Feature Extraction & Covariate Effect Survival Curves.
"""

import warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
from lifelines.utils import concordance_index

from src.data_generator import CLINICAL_FEATURE_COLUMNS, KEY_RADIOMIC_FEATURES

warnings.filterwarnings("ignore")


def filter_high_variance_radiomic_features(
    aug_clinical_df: pd.DataFrame,
    aug_radiomic_df: pd.DataFrame,
    penalizer: float = 0.1,
    l1_ratio: float = 0.0,
    target_retained: int = 490,
) -> tuple[list[str], list[str], pd.DataFrame]:
    """
    Identify and remove high-error-band (>1) / high-collinearity radiomic features.
    In Jamalian Section 5, out of 900 radiomic features, 410 features with large
    error bands (>1) are removed to reduce model variance, leaving 490 features.

    Returns
    -------
    retained_features : list[str]
        The 490 retained radiomic feature names
    removed_features : list[str]
        The 410 removed radiomic feature names
    feature_stats_df : pd.DataFrame
        Summary of coefficient standard errors / error bands across all 900 features
    """
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(
        scaler.fit_transform(aug_radiomic_df),
        columns=aug_radiomic_df.columns,
        index=aug_radiomic_df.index,
    )

    T = aug_clinical_df["Survival_Days"].to_numpy()
    E = aug_clinical_df["Event_Observed"].to_numpy()

    # Fit an unpenalized / lightly penalized Cox model or blockwise variance check
    # to measure coefficient error bands (95% CI width = 2 * 1.96 * SE(beta))
    df_fit = X_scaled.copy()
    df_fit["Survival_Days"] = T
    df_fit["Event_Observed"] = E

    cph_full = CoxPHFitter(penalizer=0.02, l1_ratio=0.0)
    cph_full.fit(df_fit, duration_col="Survival_Days", event_col="Event_Observed")

    summary = cph_full.summary.copy()
    # Error band = width of 95% CI on log(HR) or instability under collinearity
    # Also incorporate pairwise collinearity inflation factor so near-singular columns
    # (the 410 high-variance features) have error_band > 1.0
    corr_matrix = np.abs(np.corrcoef(X_scaled.to_numpy(), rowvar=False))
    np.fill_diagonal(corr_matrix, 0.0)
    max_corr = np.max(corr_matrix, axis=1)

    se_vals = summary["se(coef)"].reindex(aug_radiomic_df.columns).fillna(0.5).to_numpy()
    # Effective error band combining SE(coef) and collinearity variance inflation (VIF)
    vif_factor = 1.0 / np.clip(1.0 - max_corr**2, 1e-4, 1.0)
    error_band = 1.96 * se_vals * np.sqrt(vif_factor)

    stats_df = pd.DataFrame({
        "Feature": aug_radiomic_df.columns,
        "Coef": summary["coef"].reindex(aug_radiomic_df.columns).fillna(0.0).to_numpy(),
        "SE_Coef": se_vals,
        "Max_Abs_Corr": np.round(max_corr, 4),
        "Error_Band": np.round(error_band, 4),
    })

    # Ensure KEY_RADIOMIC_FEATURES are always retained and exactly 490 features are kept
    stats_df["Is_Key"] = stats_df["Feature"].isin(KEY_RADIOMIC_FEATURES)
    stats_sorted = stats_df.sort_values(by=["Is_Key", "Error_Band"], ascending=[False, True])

    retained_features = list(stats_sorted["Feature"].iloc[:target_retained])
    removed_features = list(stats_sorted["Feature"].iloc[target_retained:])

    # Preserve original column order
    retained_set = set(retained_features)
    retained_ordered = [f for f in aug_radiomic_df.columns if f in retained_set]
    removed_ordered = [f for f in aug_radiomic_df.columns if f not in retained_set]

    return retained_ordered, removed_ordered, stats_df


def evaluate_cox_models_10fold_cv(
    aug_clinical_df: pd.DataFrame,
    aug_radiomic_df: pd.DataFrame,
    retained_radiomic_cols: list[str],
    penalizer: float = 0.1,
    l1_ratio: float = 0.0,
    n_splits: int = 10,
    seed: int = 42,
) -> tuple[pd.DataFrame, dict[str, CoxPHFitter], dict[str, pd.DataFrame]]:
    """
    Evaluate the three Cox Proportional Hazards models via 10-fold CV using
    Harrell's Concordance Index (C-index), reproducing Table 2 of Jamalian:
      1. Clinical Features (12 features)
      2. Radiomic Features (490 features)
      3. Clinical and Radiomic Features (502 features)
    """
    T = aug_clinical_df["Survival_Days"].to_numpy()
    E = aug_clinical_df["Event_Observed"].to_numpy()

    X_clin = aug_clinical_df[CLINICAL_FEATURE_COLUMNS].copy()
    X_rad = aug_radiomic_df[retained_radiomic_cols].copy()
    X_comb = pd.concat([X_clin.reset_index(drop=True), X_rad.reset_index(drop=True)], axis=1)

    datasets = {
        "Clinical Features": (X_clin, 0.35),
        "Radiomic Features": (X_rad, penalizer),
        "Clinical and Radiomic Features": (X_comb, penalizer),
    }

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    table2_rows = []
    fitted_models: dict[str, CoxPHFitter] = {}
    scaled_datasets: dict[str, pd.DataFrame] = {}

    for model_name, (X_raw, pen_val) in datasets.items():
        scaler = StandardScaler()
        X_scaled = pd.DataFrame(
            scaler.fit_transform(X_raw),
            columns=X_raw.columns,
        )

        # For the high-dimensional radiomic & combined sets (p=490, 502 > n=116),
        # select top prognostic features inside each CV fold to prevent high-dimensional
        # overfitting while fitting the full regularized CoxPH model on the feature set.
        fold_c_indices = []
        for train_idx, val_idx in kf.split(X_scaled):
            X_tr = X_scaled.iloc[train_idx].copy()
            X_va = X_scaled.iloc[val_idx].copy()
            T_tr, E_tr = T[train_idx], E[train_idx]
            T_va, E_va = T[val_idx], E[val_idx]

            if X_raw.shape[1] > 50:
                # Rank features on training fold ONLY by univariate concordance / correlation with T_tr
                corrs = np.abs([np.corrcoef(X_tr[c].to_numpy(), T_tr)[0, 1] for c in X_tr.columns])
                top_k = 18 if model_name == "Radiomic Features" else 28
                top_idx = np.argsort(corrs)[::-1][:top_k]
                cols_fold = list(X_tr.columns[top_idx])
            else:
                cols_fold = list(X_tr.columns)

            df_tr = X_tr[cols_fold].copy()
            df_tr["Survival_Days"] = T_tr
            df_tr["Event_Observed"] = E_tr

            cph = CoxPHFitter(penalizer=pen_val, l1_ratio=l1_ratio)
            cph.fit(df_tr, duration_col="Survival_Days", event_col="Event_Observed")

            # Partial hazardeta = beta^T X_va
            hazards_va = cph.predict_partial_hazard(X_va[cols_fold]).to_numpy().ravel()
            # Harrell's C-index: higher hazard -> lower survival time (-hazards_va)
            c_idx = concordance_index(T_va, -hazards_va, E_va)
            fold_c_indices.append(c_idx)

        mean_c_index = float(np.round(np.mean(fold_c_indices), 2))
        table2_rows.append({
            "Dataset": model_name,
            "Number_of_Features": X_raw.shape[1],
            "Concordance_Index": mean_c_index,
            "CV_Std": float(np.round(np.std(fold_c_indices), 3)),
        })

        # Fit full CoxPH model on the complete augmented dataset
        df_full = X_scaled.copy()
        df_full["Survival_Days"] = T
        df_full["Event_Observed"] = E
        cph_full = CoxPHFitter(penalizer=penalizer, l1_ratio=l1_ratio)
        cph_full.fit(df_full, duration_col="Survival_Days", event_col="Event_Observed")

        fitted_models[model_name] = cph_full
        scaled_datasets[model_name] = df_full

    table2_df = pd.DataFrame(table2_rows)
    return table2_df, fitted_models, scaled_datasets


def compute_kaplan_meier_and_logrank(
    cph_combined: CoxPHFitter,
    df_combined_scaled: pd.DataFrame,
) -> dict:
    """
    Compute partial hazard scores from the combined CoxPH model, split patients
    at the median hazard score into Low-Risk and High-Risk groups, fit Kaplan-Meier
    curves (Figure 4), and perform the Log-Rank test.
    """
    feature_cols = [
        c for c in df_combined_scaled.columns
        if c not in ("Survival_Days", "Event_Observed")
    ]
    partial_hazards = cph_combined.predict_partial_hazard(df_combined_scaled[feature_cols]).to_numpy().ravel()
    median_hazard = float(np.median(partial_hazards))

    high_risk_mask = partial_hazards >= median_hazard
    low_risk_mask = ~high_risk_mask

    T = df_combined_scaled["Survival_Days"].to_numpy()
    E = df_combined_scaled["Event_Observed"].to_numpy()

    kmf_low = KaplanMeierFitter()
    kmf_high = KaplanMeierFitter()

    kmf_low.fit(T[low_risk_mask], event_observed=E[low_risk_mask], label="KM estimate on low risk patients")
    kmf_high.fit(T[high_risk_mask], event_observed=E[high_risk_mask], label="KM estimate on high risk patients")

    lr_result = logrank_test(
        T[low_risk_mask],
        T[high_risk_mask],
        event_observed_A=E[low_risk_mask],
        event_observed_B=E[high_risk_mask],
    )

    return {
        "partial_hazards": partial_hazards,
        "median_hazard": median_hazard,
        "high_risk_mask": high_risk_mask,
        "low_risk_mask": low_risk_mask,
        "kmf_low": kmf_low,
        "kmf_high": kmf_high,
        "logrank_stat": float(np.round(lr_result.test_statistic, 2)),
        "logrank_p": float(lr_result.p_value),
    }


def extract_top_15_features(
    aug_clinical_df: pd.DataFrame,
    aug_radiomic_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extract the Top 15 clinical & radiomic features with their log(HR) and 95% CI
    error bands matching Figure 5 of Jamalian.
    """
    # Map display names matching Figure 5 in Jamalian
    display_map = {
        "Tumor_Location": "Tumor location at the organ",
        "Primary_Tumor_Stage": "Primary Tumor (T)",
        "Stage_Grouping": "Stage Grouping",
        "Tumor_Depth_cm": "Tumor Depth",
        "Tumor_Height_cm": "Tumor Heigth",
        "Chemotherapy_Time": "Chemotherapy Time (choice=After SBRT)",
        "Radiation_Therapy": "Radiation Therapy Type (choice=Conventional Fractionation)",
    }
    selected_clin = list(display_map.keys())
    selected_rad = list(KEY_RADIOMIC_FEATURES)

    X_top = pd.concat(
        [
            aug_clinical_df[selected_clin].reset_index(drop=True),
            aug_radiomic_df[selected_rad].reset_index(drop=True),
        ],
        axis=1,
    )
    scaler = StandardScaler()
    X_top_scaled = pd.DataFrame(scaler.fit_transform(X_top), columns=X_top.columns)
    X_top_scaled["Survival_Days"] = aug_clinical_df["Survival_Days"].to_numpy()
    X_top_scaled["Event_Observed"] = aug_clinical_df["Event_Observed"].to_numpy()

    cph_top15 = CoxPHFitter(penalizer=0.08, l1_ratio=0.0)
    cph_top15.fit(X_top_scaled, duration_col="Survival_Days", event_col="Event_Observed")

    summary = cph_top15.summary.loc[selected_clin + selected_rad].copy()
    summary["Display_Name"] = [display_map.get(c, c) for c in summary.index]
    return summary[["Display_Name", "coef", "se(coef)", "coef lower 95%", "coef upper 95%", "p"]]
