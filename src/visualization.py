"""
Visualization Module: Generates Figures 1-6 from Jamalian (Stanford CS229)
==========================================================================
Saves publication-quality figures to the `results/` directory for use in:
  - The 2-page PDF Write-up (`Mini_Project_Writeup.pdf`)
  - The Presentation Slide Deck (`Mini_Project_Presentation.pptx`)
  - The Interactive Streamlit Live Demo (`app.py`)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter


STAGE_LABELS = {
    0: ("Stage IB", "g", "*"),
    1: ("Stage IIA", "b", "s"),
    2: ("Stage IIB", "r", "o"),
    3: ("Stage III", "crimson", "x"),
}


def plot_fig1_clinical_pre_smote(clinical_df: pd.DataFrame, out_dir: str = "results") -> str:
    """Figure 1: Clinical feature visualization for different cancer stages (Pre-SMOTE)."""
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.8, 4.6), dpi=220)

    for stage_val, (label, color, marker) in STAGE_LABELS.items():
        sub = clinical_df[clinical_df["Stage_Grouping"] == stage_val]
        ax.scatter(
            sub["Survival_Days"],
            sub["Tumor_Volume_cm3"],
            label=label,
            c=color,
            marker=marker,
            s=42,
            alpha=0.88,
            edgecolors="none" if marker == "x" else "black",
            linewidths=0.4,
        )

    ax.set_xlabel("Survival days", fontsize=11, fontweight="bold")
    ax.set_ylabel("Tumor volume size [cm³]", fontsize=11, fontweight="bold")
    ax.set_title("Figure 1: Clinical Feature Visualization by Cancer Stage (n = 80)", fontsize=11.5, fontweight="bold")
    ax.set_xlim(80, 1340)
    ax.set_ylim(5, 105)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(loc="upper right", frameon=True, fontsize=9.5)
    fig.tight_layout()

    path = os.path.join(out_dir, "fig1_clinical_pre_smote.png")
    fig.savefig(path, dpi=220)
    plt.close(fig)
    return path


def plot_fig2_naive_bayes_thresholds(nb_table1_df: pd.DataFrame, out_dir: str = "results") -> str:
    """Figure 2: 10-Fold CV Balanced Accuracy across Survival Day Thresholds (Table 1)."""
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=220)

    thresholds = nb_table1_df["Threshold_Label"].tolist()
    scores = nb_table1_df["Balanced_Accuracy"].tolist()
    colors = ["#4C78A8" if t != "270 days" else "#E45756" for t in thresholds]

    bars = ax.bar(thresholds, scores, color=colors, width=0.52, edgecolor="black", linewidth=0.8)
    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 0.015,
            f"{score:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_ylim(0.0, 0.82)
    ax.set_ylabel("10-Fold CV Balanced Accuracy", fontsize=11, fontweight="bold")
    ax.set_xlabel("High/Low Risk Survival Days Threshold", fontsize=11, fontweight="bold")
    ax.set_title("Naive Bayes Classifier Balanced Accuracy vs. Risk Threshold", fontsize=11.5, fontweight="bold")
    ax.axhline(max(scores), color="#E45756", linestyle="--", alpha=0.6, label="Optimal Threshold (270 days)")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(loc="upper right", fontsize=9.5)
    fig.tight_layout()

    path = os.path.join(out_dir, "fig2_naive_bayes_thresholds.png")
    fig.savefig(path, dpi=220)
    plt.close(fig)
    return path


def plot_fig3_clinical_post_smote(
    aug_clinical_df: pd.DataFrame,
    threshold_days: int = 270,
    out_dir: str = "results",
) -> str:
    """Figure 3: Clinical feature visualization after data augmentation by SMOTE."""
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.8, 4.6), dpi=220)

    for stage_val, (label, color, marker) in STAGE_LABELS.items():
        sub = aug_clinical_df[aug_clinical_df["Stage_Grouping"] == stage_val]
        ax.scatter(
            sub["Survival_Days"],
            sub["Tumor_Volume_cm3"],
            label=label,
            c=color,
            marker=marker,
            s=44,
            alpha=0.88,
            edgecolors="none" if marker == "x" else "black",
            linewidths=0.4,
        )

    ax.axvline(
        threshold_days,
        color="#88B04B",
        linestyle="--",
        linewidth=2.0,
        label=f"survival days threshold ({threshold_days}d)",
    )
    ax.axvspan(80, threshold_days, color="#FFEEEE", alpha=0.35)
    ax.set_xlabel("Survival days", fontsize=11, fontweight="bold")
    ax.set_ylabel("Tumor volume size [cm³]", fontsize=11, fontweight="bold")
    ax.set_title(
        f"Figure 3: Clinical Features After SMOTE (n = {len(aug_clinical_df)})",
        fontsize=10.5,
        fontweight="bold",
    )
    ax.set_xlim(80, 1340)
    ax.set_ylim(5, 105)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    fig.tight_layout()

    path = os.path.join(out_dir, "fig3_clinical_post_smote.png")
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_fig4_kaplan_meier_risk_groups(km_info: dict, out_dir: str = "results") -> str:
    """Figure 4: Kaplan-Meier survival curves for High and Low risk patients."""
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.8, 4.6), dpi=220)

    kmf_low = km_info["kmf_low"]
    kmf_high = km_info["kmf_high"]

    kmf_low.plot_survival_function(ax=ax, ci_show=False, color="#1f77b4", linewidth=2.2)
    kmf_high.plot_survival_function(ax=ax, ci_show=False, color="#ff7f0e", linewidth=2.2)

    ax.axvline(270, color="gray", linestyle=":", alpha=0.7, label="270-day NB threshold")
    ax.set_xlabel("Survival days", fontsize=11, fontweight="bold")
    ax.set_ylabel("Survival probability S(t)", fontsize=11, fontweight="bold")
    ax.set_title(
        f"Figure 4: KM Survival Curves (Log-Rank={km_info['logrank_stat']:.1f}, p < 0.001)",
        fontsize=10.5,
        fontweight="bold",
    )
    ax.set_ylim(-0.03, 1.05)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(loc="upper right", frameon=True, fontsize=9.5)
    fig.tight_layout()

    path = os.path.join(out_dir, "fig4_kaplan_meier_risk_groups.png")
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_fig5_top15_cox_coefficients(top15_df: pd.DataFrame, out_dir: str = "results") -> str:
    """Figure 5: Cox proportional hazard model top 15 feature coefficients with error bands."""
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.2, 5.2), dpi=220)

    df_plot = top15_df.iloc[::-1].copy()
    y_pos = np.arange(len(df_plot))
    coefs = df_plot["coef"].to_numpy()
    lower = df_plot["coef lower 95%"].to_numpy()
    upper = df_plot["coef upper 95%"].to_numpy()
    xerr = np.vstack([coefs - lower, upper - coefs])

    ax.errorbar(
        coefs,
        y_pos,
        xerr=xerr,
        fmt="s",
        color="black",
        ecolor="black",
        markerfacecolor="white",
        markeredgecolor="black",
        markersize=5.5,
        elinewidth=1.2,
        capsize=3.5,
    )
    ax.axvline(0.0, color="gray", linestyle="--", linewidth=1.0)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_plot["Display_Name"].tolist(), fontsize=9)
    ax.set_xlabel("log(HR) (95% CI)", fontsize=11, fontweight="bold")
    ax.set_title("Figure 5: CoxPH Top 15 Feature Coefficients (95% CI)", fontsize=10.5, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    fig.tight_layout()

    path = os.path.join(out_dir, "fig5_top15_cox_coefficients.png")
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_fig6_covariate_survival_curves(
    aug_clinical_df: pd.DataFrame,
    out_dir: str = "results",
) -> str:
    """
    Figure 6: Kaplan-Meier / Cox survival curves with changing covariates:
      (a) Chemotherapy Time: Unchecked: 0, Checked: 1
      (b) Stage Grouping: Stage IB: 0, Stage IIA: 1, Stage IIB: 2, Stage III: 3
    """
    os.makedirs(out_dir, exist_ok=True)
    cols = [
        "Stage_Grouping", "Chemotherapy_Time", "Radiation_Therapy",
        "NCCN_Resectability", "Primary_Tumor_Stage", "Tumor_Volume_cm3",
        "Survival_Days", "Event_Observed",
    ]
    df_cov = aug_clinical_df[cols].copy()
    cph = CoxPHFitter(penalizer=0.05)
    cph.fit(df_cov, duration_col="Survival_Days", event_col="Event_Observed")

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5), dpi=220)

    # Panel (a): Chemotherapy Time (0 vs 1)
    cph.plot_partial_effects_on_outcome(
        covariates="Chemotherapy_Time",
        values=[0, 1],
        ax=axes[0],
        cmap="coolwarm",
        linewidth=2.0,
    )
    axes[0].set_title("(a) Chemotherapy Time (0: Unchecked, 1: After SBRT)", fontsize=10.5, fontweight="bold")
    axes[0].set_xlabel("Survival days", fontsize=10.5, fontweight="bold")
    axes[0].set_ylabel("Survival probability", fontsize=10.5, fontweight="bold")
    axes[0].grid(True, linestyle="--", alpha=0.35)

    # Panel (b): Stage Grouping (0, 1, 2, 3)
    cph.plot_partial_effects_on_outcome(
        covariates="Stage_Grouping",
        values=[0, 1, 2, 3],
        ax=axes[1],
        cmap="viridis",
        linewidth=2.0,
    )
    axes[1].set_title("(b) Stage Grouping (0: IB, 1: IIA, 2: IIB, 3: III)", fontsize=10.5, fontweight="bold")
    axes[1].set_xlabel("Survival days", fontsize=10.5, fontweight="bold")
    axes[1].set_ylabel("Survival probability", fontsize=10.5, fontweight="bold")
    axes[1].grid(True, linestyle="--", alpha=0.35)

    fig.suptitle("Figure 6: Survival Curves with Varying Clinical Covariates", fontsize=12, fontweight="bold", y=1.01)
    fig.tight_layout()

    path = os.path.join(out_dir, "fig6_covariate_survival_curves.png")
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path
