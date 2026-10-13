"""
Member 1 Module: Clinical Discretization, Multinomial Naive Bayes & SMOTE Augmentation
======================================================================================
Implements Section 4 & Section 5 (Part 1) of Arash Jamalian (Stanford CS229):
1. Discretizes the 5 selected clinical features into V buckets:
   - Stage Grouping, Chemotherapy Time, Tumor Width, NCCN Resectability Criteria,
     and Radiation Therapy.
2. Trains a Generative Multinomial Naive Bayes Classifier with Maximum Likelihood
   Estimation (MLE) and Laplace Smoothing:
       phi_{d,k | y=c} = (1 + sum_i 1{x_d^{(i)} = k and y^{(i)} = c}) /
                         (V_d + sum_i 1{y^{(i)} = c})
       phi_y = (sum_i 1{y^{(i)} = 1}) / n
3. Evaluates 10-fold Cross-Validation Balanced Accuracy across survival thresholds:
   240, 270, 300, 330, and 360 days (reproducing Table 1 where 270 days is optimal).
4. Applies SMOTE (5-nearest neighbors via imbalanced-learn) on the joint clinical +
   radiomic feature space using the optimal 270-day threshold to populate the
   high-risk region (<270 days) with synthetic Stage IIB and Stage III cases.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score
from imblearn.over_sampling import SMOTE

from src.data_generator import (
    CLINICAL_FEATURE_COLUMNS,
    NAIVE_BAYES_CLINICAL_FEATURES,
)


SURVIVAL_THRESHOLDS = [240, 270, 300, 330, 360]


class LaplaceMultinomialNaiveBayes:
    """
    Generative Multinomial Naive Bayes Classifier with Laplace Smoothing
    matching the exact mathematical formulation in Jamalian Section 4:
        p(D_i) = p(y^i) * prod_{d=1}^F p(x_d^i | y^i)
    """

    def __init__(self, num_buckets_per_feature: dict[str, int] | None = None):
        self.num_buckets_per_feature = num_buckets_per_feature or {}
        self.phi_y1: float = 0.5
        self.phi_y0: float = 0.5
        self.cond_probs_y1: dict[str, dict[int, float]] = {}
        self.cond_probs_y0: dict[str, dict[int, float]] = {}
        self.feature_names: list[str] = []

    def fit(self, X_disc: pd.DataFrame, y: np.ndarray) -> "LaplaceMultinomialNaiveBayes":
        """Fit MLE parameters with Laplace (+1 / +V) smoothing."""
        self.feature_names = list(X_disc.columns)
        n = len(y)
        n_y1 = int(np.sum(y == 1))
        n_y0 = int(np.sum(y == 0))

        self.phi_y1 = n_y1 / max(n, 1)
        self.phi_y0 = 1.0 - self.phi_y1

        self.cond_probs_y1 = {}
        self.cond_probs_y0 = {}

        for col in self.feature_names:
            vals = X_disc[col].to_numpy()
            unique_buckets = sorted(list(set(vals) | set(range(self.num_buckets_per_feature.get(col, 4)))))
            V = len(unique_buckets)

            self.cond_probs_y1[col] = {}
            self.cond_probs_y0[col] = {}

            for k in unique_buckets:
                count_k_y1 = int(np.sum((vals == k) & (y == 1)))
                count_k_y0 = int(np.sum((vals == k) & (y == 0)))
                self.cond_probs_y1[col][k] = (1.0 + count_k_y1) / (V + n_y1)
                self.cond_probs_y0[col][k] = (1.0 + count_k_y0) / (V + n_y0)

        return self

    def predict_proba(self, X_disc: pd.DataFrame) -> np.ndarray:
        """Compute posterior probabilities P(y=1 | x) and P(y=0 | x)."""
        n = len(X_disc)
        log_p1 = np.full(n, np.log(max(self.phi_y1, 1e-12)))
        log_p0 = np.full(n, np.log(max(self.phi_y0, 1e-12)))

        for col in self.feature_names:
            vals = X_disc[col].to_numpy()
            default_p1 = 1.0 / (len(self.cond_probs_y1[col]) + 1.0)
            default_p0 = 1.0 / (len(self.cond_probs_y0[col]) + 1.0)
            p1_col = np.array([self.cond_probs_y1[col].get(int(v), default_p1) for v in vals])
            p0_col = np.array([self.cond_probs_y0[col].get(int(v), default_p0) for v in vals])
            log_p1 += np.log(np.clip(p1_col, 1e-12, 1.0))
            log_p0 += np.log(np.clip(p0_col, 1e-12, 1.0))

        max_log = np.maximum(log_p0, log_p1)
        exp_0 = np.exp(log_p0 - max_log)
        exp_1 = np.exp(log_p1 - max_log)
        denom = exp_0 + exp_1
        return np.column_stack([exp_0 / denom, exp_1 / denom])

    def predict(self, X_disc: pd.DataFrame) -> np.ndarray:
        """Predict binary risk label y in {0, 1}."""
        probs = self.predict_proba(X_disc)
        return (probs[:, 1] >= 0.5).astype(int)


def discretize_clinical_features(
    clinical_df: pd.DataFrame,
    width_bins: np.ndarray | None = None,
) -> tuple[pd.DataFrame, np.ndarray]:
    """
    Discretize the 5 Naive Bayes clinical features into multinomial buckets {0, ..., V-1}.
    Features: Stage_Grouping, Chemotherapy_Time, Tumor_Width_cm, NCCN_Resectability, Radiation_Therapy.
    """
    df_sub = clinical_df[NAIVE_BAYES_CLINICAL_FEATURES].copy()
    if width_bins is None:
        # 4 quantile/fixed buckets for Tumor_Width_cm
        width_bins = np.array([0.0, 2.6, 3.3, 4.0, 10.0])

    df_disc = pd.DataFrame(index=clinical_df.index)
    df_disc["Stage_Grouping"] = df_sub["Stage_Grouping"].astype(int)
    df_disc["Chemotherapy_Time"] = df_sub["Chemotherapy_Time"].astype(int)
    df_disc["Tumor_Width_cm"] = np.digitize(df_sub["Tumor_Width_cm"].to_numpy(), width_bins[1:-1]).astype(int)
    df_disc["NCCN_Resectability"] = df_sub["NCCN_Resectability"].astype(int)
    df_disc["Radiation_Therapy"] = df_sub["Radiation_Therapy"].astype(int)

    return df_disc, width_bins


def evaluate_naive_bayes_thresholds(
    clinical_df: pd.DataFrame,
    thresholds: list[int] = SURVIVAL_THRESHOLDS,
    n_splits: int = 10,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Run 10-fold Stratified Cross-Validation across survival day thresholds
    [240, 270, 300, 330, 360] and compute Balanced Accuracy (Table 1 in Jamalian).
    """
    X_disc, _ = discretize_clinical_features(clinical_df)
    bucket_sizes = {
        "Stage_Grouping": 4,
        "Chemotherapy_Time": 2,
        "Tumor_Width_cm": 4,
        "NCCN_Resectability": 3,
        "Radiation_Therapy": 2,
    }

    records = []
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    for thresh in thresholds:
        # High risk (y = 1) if Survival_Days < thresh else Low risk (y = 0)
        y = (clinical_df["Survival_Days"].to_numpy() < thresh).astype(int)
        fold_scores = []

        for train_idx, val_idx in skf.split(X_disc, y):
            X_train, X_val = X_disc.iloc[train_idx], X_disc.iloc[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            model = LaplaceMultinomialNaiveBayes(bucket_sizes)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
            fold_scores.append(balanced_accuracy_score(y_val, y_pred))

        mean_bal_acc = float(np.round(np.mean(fold_scores), 2))
        records.append({
            "Threshold_Days": thresh,
            "Threshold_Label": f"{thresh} days",
            "High_Risk_Count": int(np.sum(y == 1)),
            "Low_Risk_Count": int(np.sum(y == 0)),
            "Balanced_Accuracy": mean_bal_acc,
            "Fold_Std": float(np.round(np.std(fold_scores), 3)),
        })

    results_df = pd.DataFrame(records)
    return results_df


def augment_dataset_with_smote(
    clinical_df: pd.DataFrame,
    radiomic_df: pd.DataFrame,
    optimal_threshold: int = 270,
    k_neighbors: int = 5,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """
    Apply SMOTE (Synthetic Minority Oversampling Technique) with k=5 nearest neighbors
    on the joint clinical + radiomic feature space using the optimal 270-day threshold.

    Returns
    -------
    aug_clinical_df : pd.DataFrame
        Augmented clinical dataframe (including synthetic high-risk patients)
    aug_radiomic_df : pd.DataFrame
        Augmented 900-feature radiomic dataframe
    is_synthetic : np.ndarray
        Boolean mask indicating which rows were generated by SMOTE
    """
    y_risk = (clinical_df["Survival_Days"].to_numpy() < optimal_threshold).astype(int)

    # Combine numeric clinical features + survival targets + 900 radiomic features for SMOTE
    clin_numeric_cols = CLINICAL_FEATURE_COLUMNS + ["Survival_Days", "Event_Observed"]
    joint_df = pd.concat(
        [clinical_df[clin_numeric_cols].reset_index(drop=True), radiomic_df.reset_index(drop=True)],
        axis=1,
    )

    smote = SMOTE(k_neighbors=k_neighbors, random_state=seed)
    joint_resampled, y_resampled = smote.fit_resample(joint_df, y_risk)

    n_orig = len(clinical_df)
    n_total = len(joint_resampled)
    is_synthetic = np.zeros(n_total, dtype=bool)
    is_synthetic[n_orig:] = True

    # Reconstruct clinical dataframe with discrete integer types rounded appropriately
    aug_clinical = joint_resampled[clin_numeric_cols].copy()
    int_cols = [
        "Stage_Grouping", "Chemotherapy_Time", "Radiation_Therapy",
        "NCCN_Resectability", "Tumor_Location", "Primary_Tumor_Stage",
        "Gender", "Survival_Days", "Event_Observed",
    ]
    for col in int_cols:
        aug_clinical[col] = np.round(aug_clinical[col]).astype(int)

    aug_clinical["KPS_Score"] = (np.round(aug_clinical["KPS_Score"] / 10.0) * 10).astype(int)

    # For synthetic minority examples, ensure they reflect high-risk Stage IIB/III cases (<optimal_threshold)
    syn_indices = np.where(is_synthetic)[0]
    rng = np.random.default_rng(seed)
    for idx in syn_indices:
        aug_clinical.loc[idx, "Survival_Days"] = int(
            np.clip(aug_clinical.loc[idx, "Survival_Days"], 140, optimal_threshold - 5)
        )
        if aug_clinical.loc[idx, "Stage_Grouping"] < 2:
            aug_clinical.loc[idx, "Stage_Grouping"] = int(rng.choice([2, 3], p=[0.48, 0.52]))
        aug_clinical.loc[idx, "Event_Observed"] = 1

    patient_ids = list(clinical_df["Patient_ID"]) + [
        f"SMOTE-PC-{i+1:03d}" for i in range(n_total - n_orig)
    ]
    aug_clinical.insert(0, "Patient_ID", patient_ids)
    aug_clinical["High_Risk_Cohort"] = y_resampled
    aug_clinical["Is_Synthetic"] = is_synthetic

    aug_radiomic = joint_resampled[radiomic_df.columns].copy()
    return aug_clinical, aug_radiomic, is_synthetic
