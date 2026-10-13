"""
Synthetic Pancreatic Cancer Clinical & Radiomic Dataset Generator (UE24CS352A)
================================================================================
DISCLAIMER:
The original Stanford Cancer Center dataset studied in Arash Jamalian (CS229,
Stanford University, 2020) is protected under a Non-Disclosure Agreement (NDA)
and cannot be publicly distributed.

This module programmatically generates a SYNTHETIC dataset designed to mirror
the structural dimensionality and statistical properties of the reference study:
  - 80 synthetic patients (24 high-risk < 270d, 56 low-risk >= 270d)
  - 12 clinical variables (stage, treatments, performance status, tumor sizes)
  - 900 radiomic features (simulating PyRadiomics/QFIP extraction with 3D
    wavelets, Laplacian-of-Gaussian, GLCM, GLSZM, GLRLM textures)
  - Continuous survival days and right-censoring indicators (~17.5% censored).

Simulation Details:
  - Seed: Deterministic via numpy.random.default_rng(seed=42).
  - Survival time (T): High-risk simulated as Uniform(135, 266) days;
    Low-risk simulated as Gamma(shape=2.4, scale=145.0) + 272 days.
  - Latent hazard (eta): Standardized negative log-survival, driving
    clinical categorical distributions and radiomic feature matrices.
  - Collinearity / Pruning: 410 radiomic features are generated from 10 shared
    latent anchor variables with minimal noise (sigma=0.012), causing high
    standard errors (SE > 1.0) under Cox regression to simulate the collinear
    redundancy observed in the original study.
  - Disclaimer: These synthetic data are NOT real patient records. Metrics
    obtained on this dataset are for educational demonstration and cannot be
    directly compared to the published paper's results.
"""

import os
import numpy as np
import pandas as pd


CLINICAL_FEATURE_COLUMNS = [
    "Stage_Grouping",          # 0: Stage IB, 1: Stage IIA, 2: Stage IIB, 3: Stage III
    "Chemotherapy_Time",       # 0: Unchecked (No/Pre), 1: Checked (After SBRT)
    "Radiation_Therapy",       # 0: SBRT, 1: Conventional Fractionation
    "NCCN_Resectability",      # 0: Resectable, 1: Borderline Resectable, 2: Locally Advanced
    "Tumor_Location",          # 0: Head, 1: Body, 2: Tail
    "Primary_Tumor_Stage",     # 1: T1, 2: T2, 3: T3, 4: T4
    "KPS_Score",               # Karnofsky Performance Status (60 - 100)
    "Gender",                  # 0: Female, 1: Male
    "Tumor_Width_cm",          # Tumor width (cm)
    "Tumor_Height_cm",         # Tumor height (cm)
    "Tumor_Depth_cm",          # Tumor depth (cm)
    "Tumor_Volume_cm3",        # Tumor volume (cm^3)
]

NAIVE_BAYES_CLINICAL_FEATURES = [
    "Stage_Grouping",
    "Chemotherapy_Time",
    "Tumor_Width_cm",
    "NCCN_Resectability",
    "Radiation_Therapy",
]

KEY_RADIOMIC_FEATURES = [
    "wavelet-LLH_glrlm_LongRunEmphasis",
    "wavelet-LLH_firstorder_Skewness",
    "wavelet-LLH_firstorder_Mean",
    "wavelet-HHH_glrlm_LongRunLowGrayLevelEmphasis",
    "wavelet-HLH_glszm_ZoneEntropy",
    "wavelet-HLL_firstorder_Skewness",
    "log-sigma-5-mm-3D_glrlm_LongRunLowGrayLevelEmphasis",
    "log-sigma-5-mm-3D_glszm_SizeZoneNonUniformity",
]


def _build_radiomic_feature_names(n_features: int = 900) -> list[str]:
    """Generate 900 authentic PyRadiomics / Stanford QFIP feature names."""
    names = list(KEY_RADIOMIC_FEATURES)
    prefixes = [
        "original",
        "wavelet-LLL", "wavelet-LLH", "wavelet-LHL", "wavelet-LHH",
        "wavelet-HLL", "wavelet-HLH", "wavelet-HHL", "wavelet-HHH",
        "log-sigma-1-mm-3D", "log-sigma-3-mm-3D", "log-sigma-5-mm-3D",
    ]
    families = {
        "firstorder": [
            "Energy", "Entropy", "Kurtosis", "Maximum", "Mean",
            "Median", "Minimum", "Range", "RootMeanSquared", "Skewness",
            "StandardDeviation", "Uniformity", "Variance", "10Percentile", "90Percentile",
        ],
        "shape": [
            "Compactness1", "Compactness2", "Elongation", "Flatness",
            "LeastAxisLength", "MajorAxisLength", "Maximum2DDiameterColumn",
            "Maximum2DDiameterRow", "Maximum2DDiameterSlice", "Maximum3DDiameter",
            "MeshVolume", "MinorAxisLength", "Sphericity", "SurfaceArea",
            "SurfaceVolumeRatio", "VoxelVolume",
        ],
        "glcm": [
            "Autocorrelation", "ClusterProminence", "ClusterShade", "ClusterTendency",
            "Contrast", "Correlation", "DifferenceAverage", "DifferenceEntropy",
            "DifferenceVariance", "Id", "Idm", "Imc1", "Imc2", "InverseVariance",
            "JointAverage", "JointEnergy", "JointEntropy", "MaximumProbability",
            "SumAverage", "SumEntropy", "SumSquares",
        ],
        "glszm": [
            "GrayLevelNonUniformity", "GrayLevelNonUniformityNormalized",
            "GrayLevelVariance", "HighGrayLevelZoneEmphasis", "LargeAreaEmphasis",
            "LargeAreaHighGrayLevelEmphasis", "LargeAreaLowGrayLevelEmphasis",
            "LowGrayLevelZoneEmphasis", "SizeZoneNonUniformity",
            "SizeZoneNonUniformityNormalized", "SmallAreaEmphasis",
            "SmallAreaHighGrayLevelEmphasis", "SmallAreaLowGrayLevelEmphasis",
            "ZoneEntropy", "ZonePercentage", "ZoneVariance",
        ],
        "glrlm": [
            "GrayLevelNonUniformity", "GrayLevelNonUniformityNormalized",
            "GrayLevelVariance", "HighGrayLevelRunEmphasis", "LongRunEmphasis",
            "LongRunHighGrayLevelEmphasis", "LongRunLowGrayLevelEmphasis",
            "LowGrayLevelRunEmphasis", "RunEntropy", "RunLengthNonUniformity",
            "RunLengthNonUniformityNormalized", "RunPercentage", "RunVariance",
            "ShortRunEmphasis", "ShortRunHighGrayLevelEmphasis", "ShortRunLowGrayLevelEmphasis",
        ],
    }

    idx = 1
    while len(names) < n_features:
        for prefix in prefixes:
            for fam, metrics in families.items():
                if prefix != "original" and fam == "shape":
                    continue
                for m in metrics:
                    candidate = f"{prefix}_{fam}_{m}"
                    if candidate in names:
                        candidate = f"{candidate}_{idx}"
                    names.append(candidate)
                    if len(names) >= n_features:
                        return names[:n_features]
        idx += 1
    return names[:n_features]


def generate_stanford_pancreatic_dataset(
    n_patients: int = 80,
    n_radiomic: int = 900,
    seed: int = 42,
    save_dir: str = "data",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate or load the 80-patient clinical and 900-feature radiomic dataset.

    Returns
    -------
    clinical_df : pd.DataFrame
        Shape (80, 15) -> Patient_ID, 12 clinical features, Survival_Days, Event_Observed
    radiomic_df : pd.DataFrame
        Shape (80, 900) -> 900 standardized radiomic features indexed by patient
    """
    os.makedirs(save_dir, exist_ok=True)
    clinical_path = os.path.join(save_dir, "clinical_data.csv")
    radiomic_path = os.path.join(save_dir, "radiomic_data.csv")

    rng = np.random.default_rng(seed)

    # 1. Latent risk factor for each of the 80 patients
    # Mirrors the cohort in Jamalian Fig. 1: fewer high-risk (<270d) examples (~22/80)
    # and majority surviving >270 days (~58/80).
    n_high_risk = 24
    n_low_risk = n_patients - n_high_risk
    high_risk_flags = np.array([1] * n_high_risk + [0] * n_low_risk)
    rng.shuffle(high_risk_flags)

    # Survival days: high-risk in [135, 268], low-risk in [272, 1280]
    survival_days = np.zeros(n_patients, dtype=int)
    for i in range(n_patients):
        if high_risk_flags[i] == 1:
            survival_days[i] = int(rng.uniform(135, 266))
        else:
            # Skewed toward 300-650 days with long-term survivors up to 1280 days
            base = rng.gamma(shape=2.4, scale=145.0) + 272
            survival_days[i] = int(np.clip(base, 273, 1285))

    # Normalize continuous latent hazard eta in [-1.5, 1.5] negatively correlated with survival_days
    log_surv = np.log(survival_days)
    latent_hazard = -(log_surv - np.mean(log_surv)) / (np.std(log_surv) + 1e-8)

    # 2. Construct the 12 Clinical Features
    # Make the 5 Naive Bayes clinical features correlate cleanly with the 270-day threshold
    # while having moderate correlation with continuous survival time (so clinical C-index ~ 0.67)
    stage_grouping = np.zeros(n_patients, dtype=int)
    chemo_time = np.zeros(n_patients, dtype=int)
    radiation_therapy = np.zeros(n_patients, dtype=int)
    nccn_resect = np.zeros(n_patients, dtype=int)
    tumor_width = np.zeros(n_patients, dtype=float)

    for i in range(n_patients):
        is_hr = high_risk_flags[i] == 1
        if is_hr:
            stage_grouping[i] = rng.choice([0, 1, 2, 3], p=[0.05, 0.17, 0.36, 0.42])
            chemo_time[i] = rng.choice([0, 1], p=[0.74, 0.26])
            radiation_therapy[i] = rng.choice([0, 1], p=[0.30, 0.70])
            nccn_resect[i] = rng.choice([0, 1, 2], p=[0.12, 0.33, 0.55])
            tumor_width[i] = np.clip(rng.normal(3.9, 0.65), 2.1, 5.8)
        else:
            stage_grouping[i] = rng.choice([0, 1, 2, 3], p=[0.18, 0.34, 0.30, 0.18])
            chemo_time[i] = rng.choice([0, 1], p=[0.32, 0.68])
            radiation_therapy[i] = rng.choice([0, 1], p=[0.64, 0.36])
            nccn_resect[i] = rng.choice([0, 1, 2], p=[0.42, 0.38, 0.20])
            tumor_width[i] = np.clip(rng.normal(3.0, 0.70), 1.4, 5.2)

    # Remaining 7 clinical features
    tumor_location = rng.choice([0, 1, 2], size=n_patients, p=[0.62, 0.23, 0.15])
    primary_tumor_stage = np.clip(
        np.round(2.2 + 0.45 * latent_hazard + rng.normal(0, 0.65, n_patients)), 1, 4
    ).astype(int)
    kps_score = np.clip(
        np.round((82 - 5.5 * latent_hazard + rng.normal(0, 8, n_patients)) / 10.0) * 10,
        60, 100
    ).astype(int)
    gender = rng.choice([0, 1], size=n_patients, p=[0.48, 0.52])

    tumor_height = np.clip(tumor_width * rng.uniform(0.78, 1.22, n_patients), 1.3, 5.9)
    tumor_depth = np.clip(tumor_width * rng.uniform(0.75, 1.25, n_patients), 1.2, 5.8)
    # Volume roughly ellipsoid + scatter matching Fig 1 [10, 100] cm^3
    tumor_volume = np.clip(
        0.85 * tumor_width * tumor_height * tumor_depth + rng.normal(12.0, 9.0, n_patients),
        10.5, 99.5
    )

    # Right censoring: ~82% observed events, ~18% right-censored
    event_observed = np.ones(n_patients, dtype=int)
    censored_idx = rng.choice(
        np.where(survival_days > 310)[0],
        size=min(14, len(np.where(survival_days > 310)[0])),
        replace=False,
    )
    event_observed[censored_idx] = 0

    clinical_df = pd.DataFrame({
        "Patient_ID": [f"STAN-PC-{i+1:03d}" for i in range(n_patients)],
        "Stage_Grouping": stage_grouping,
        "Chemotherapy_Time": chemo_time,
        "Radiation_Therapy": radiation_therapy,
        "NCCN_Resectability": nccn_resect,
        "Tumor_Location": tumor_location,
        "Primary_Tumor_Stage": primary_tumor_stage,
        "KPS_Score": kps_score,
        "Gender": gender,
        "Tumor_Width_cm": np.round(tumor_width, 2),
        "Tumor_Height_cm": np.round(tumor_height, 2),
        "Tumor_Depth_cm": np.round(tumor_depth, 2),
        "Tumor_Volume_cm3": np.round(tumor_volume, 2),
        "Survival_Days": survival_days,
        "Event_Observed": event_observed,
    })

    # 3. Construct the 900 Radiomic Features
    # Section 5 of Jamalian:
    # - 900 radiomic features total, many highly correlated.
    # - 410 features have large coefficient error bands (>1) due to collinearity/variance
    #   and are removed, leaving 490 radiomic features.
    # - The 8 key radiomic features in Fig. 5 have clear prognostic signal.
    feature_names = _build_radiomic_feature_names(n_radiomic)
    radiomic_matrix = np.zeros((n_patients, n_radiomic), dtype=float)

    # First 8 features = KEY_RADIOMIC_FEATURES from Figure 5
    key_weights = np.array([-0.42, -0.36, -0.33, -0.48, -0.35, -0.31, -0.38, -0.29])
    for j in range(8):
        radiomic_matrix[:, j] = (
            key_weights[j] * latent_hazard
            + rng.normal(0, 0.82, size=n_patients)
        )

    # Next 482 features (total 490 retained features):
    # Moderate prognostic signal + structured block correlation
    n_retained = 490
    latent_blocks = rng.normal(0, 1.0, size=(n_patients, 18))
    for j in range(8, n_retained):
        block_id = j % 18
        signal_strength = rng.uniform(-0.26, 0.26) if j < 65 else rng.uniform(-0.08, 0.08)
        radiomic_matrix[:, j] = (
            signal_strength * latent_hazard
            + 0.55 * latent_blocks[:, block_id]
            + rng.normal(0, 0.85, size=n_patients)
        )

    # Last 410 features (indices 490..899):
    # Highly collinear / near-singular combinations that induce large standard errors (>1.0)
    # in unpruned Cox regression (mirroring the 410 removed features in Jamalian Section 5).
    anchor_cols = rng.normal(0, 1.0, size=(n_patients, 10))
    for j in range(n_retained, n_radiomic):
        a_idx = j % 10
        # Near-collinear with very small variance delta -> inflates SE(beta) > 1
        radiomic_matrix[:, j] = (
            anchor_cols[:, a_idx]
            + rng.normal(0, 0.012, size=n_patients)
        )

    radiomic_df = pd.DataFrame(
        np.round(radiomic_matrix, 5),
        columns=feature_names,
    )

    clinical_df.to_csv(clinical_path, index=False)
    radiomic_df.to_csv(radiomic_path, index=False)
    return clinical_df, radiomic_df


if __name__ == "__main__":
    clin, rad = generate_stanford_pancreatic_dataset()
    print(f"Generated clinical dataset: {clin.shape}")
    print(f"Generated radiomic dataset: {rad.shape}")
