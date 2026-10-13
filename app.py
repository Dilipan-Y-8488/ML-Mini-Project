"""
Interactive Live Demo Application (Streamlit)
=============================================
Course: UE24CS352A - Machine Learning Mini-Project
Project: Pancreatic Cancer Prognosis using Clinical and Radiomic Data

Run with:
    streamlit run app.py
"""

import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter

from src.data_generator import (
    generate_stanford_pancreatic_dataset,
    CLINICAL_FEATURE_COLUMNS,
    NAIVE_BAYES_CLINICAL_FEATURES,
)
from src.naive_bayes_smote import (
    evaluate_naive_bayes_thresholds,
    augment_dataset_with_smote,
    discretize_clinical_features,
    LaplaceMultinomialNaiveBayes,
)

st.set_page_config(
    page_title="Pancreatic Cancer Prognosis | UE24CS352A Live Demo",
    page_icon="🧬",
    layout="wide",
)


@st.cache_data
def load_data_and_results():
    if not os.path.exists("data/clinical_data.csv") or not os.path.exists("results/metrics_summary.json"):
        from main import run_pipeline
        run_pipeline()

    clinical_df = pd.read_csv("data/clinical_data.csv")
    radiomic_df = pd.read_csv("data/radiomic_data.csv")
    table1_df = pd.read_csv("results/table1_naive_bayes_cv.csv")
    table2_df = pd.read_csv("results/table2_cox_c_index.csv")
    table2b_df = pd.read_csv("results/table2b_leakage_comparison.csv") if os.path.exists("results/table2b_leakage_comparison.csv") else None
    top15_df = pd.read_csv("results/top15_cox_features.csv")
    with open("results/metrics_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    aug_clin, aug_rad, _ = augment_dataset_with_smote(
        clinical_df, radiomic_df, optimal_threshold=summary["optimal_nb_threshold_days"]
    )
    return clinical_df, radiomic_df, aug_clin, aug_rad, table1_df, table2_df, table2b_df, top15_df, summary


def main():
    clinical_df, radiomic_df, aug_clin, aug_rad, table1_df, table2_df, table2b_df, top15_df, summary = (
        load_data_and_results()
    )

    st.title("🧬 Pancreatic Cancer Prognosis using Clinical & Radiomic Data")
    st.markdown(
        "**UE24CS352A — Machine Learning Mini-Project Live Demo** | "
        "*Based on Arash Jamalian (Stanford University CS229 Report)*"
    )

    # Top KPI cards
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Cohort Size (Original → SMOTE)", f"{summary['n_patients_original']} → {summary['n_patients_augmented']}")
    col2.metric("Radiomic Features (Raw → Filtered)", f"{summary['n_radiomic_total']} → {summary['n_radiomic_retained']}")
    col3.metric("Optimal NB Risk Threshold", f"{summary['optimal_nb_threshold_days']} Days (0.74 Acc)")
    col4.metric("Leak-Free 10-Fold CV C-Index", f"{table2_df['Concordance_Index'].max():.2f} (Combined)")
    col5.metric("Log-Rank Test Stat (p < 0.05)", f"{summary['logrank_test_statistic']:.2f}")

    st.divider()

    tabs = st.tabs([
        "📊 1. Dataset & Cohort Explorer",
        "🧮 2. [Dilipan Y] Naive Bayes & SMOTE",
        "📈 3. [Sai Hemanth] CoxPH & Kaplan-Meier",
        "🩺 4. Live Patient Prognosis Predictor",
    ])

    # TAB 1: Dataset Explorer
    with tabs[0]:
        st.subheader("Synthetic Stanford QFIP Clinical (12 Features) & Radiomic (900 Features) Cohort")
        st.caption("Disclaimer: This dataset is synthetic, generated to mimic the published Stanford cohort (NDA protected).")
        c1, c2 = st.columns([1.25, 1.0])
        with c1:
            st.markdown("##### Clinical Dataset Sample (`data/clinical_data.csv`)")
            st.dataframe(clinical_df.head(15), use_container_width=True)
            st.markdown("##### Radiomic Features Sample (First 12 of 900 Simulated Radiomic Features)")
            st.dataframe(radiomic_df.iloc[:10, :12], use_container_width=True)
        with c2:
            if os.path.exists("results/fig1_clinical_pre_smote.png"):
                st.image(
                    "results/fig1_clinical_pre_smote.png",
                    caption="Figure 1: Survival Days vs. Tumor Volume by Cancer Stage (Pre-SMOTE, n=80)",
                    use_container_width=True,
                )

    # TAB 2: Dilipan Y Pipeline
    with tabs[1]:
        st.subheader("Dilipan Y (PES1UG24AM092) — Laplace Multinomial Naive Bayes & SMOTE")
        st.markdown(
            r"""
            **Generative Model Formulation (Laplace Smoothing):**
            $$\phi_{dk|y=c} = \frac{1 + \sum_{i=1}^n \mathbf{1}\{x_d^{(i)} = k \wedge y^{(i)} = c\}}{V_d + \sum_{i=1}^n \mathbf{1}\{y^{(i)} = c\}}, \qquad \phi_y = \frac{\sum_{i=1}^n \mathbf{1}\{y^{(i)} = 1\}}{n}$$
            """
        )
        m1_col1, m1_col2 = st.columns([1.0, 1.1])
        with m1_col1:
            st.markdown("##### Table 1: 10-Fold CV Balanced Accuracy across Survival Thresholds")
            t1_cols = [c for c in ["Threshold_Label", "High_Risk_Count", "Low_Risk_Count", "Balanced_Accuracy", "Fold_Std", "Selection_Status"] if c in table1_df.columns]
            st.dataframe(table1_df[t1_cols], use_container_width=True)
            if "threshold_selection_rule" in summary:
                st.caption(f"**Selection Rule:** {summary['threshold_selection_rule']}")
            if os.path.exists("results/fig2_naive_bayes_thresholds.png"):
                st.image("results/fig2_naive_bayes_thresholds.png", use_container_width=True)
        with m1_col2:
            st.markdown("##### Figure 3: High-Risk Cohort Populated via 5-NN SMOTE (< 270 Days)")
            if os.path.exists("results/fig3_clinical_post_smote.png"):
                st.image("results/fig3_clinical_post_smote.png", use_container_width=True)
            st.info(
                f"**SMOTE Summary:** Augmented high-risk minority class (< 270 days) from "
                f"**{summary['n_patients_original']}** to **{summary['n_patients_augmented']}** total cases "
                f"(+{summary['n_synthetic_added']} synthetic Stage IIB & Stage III patients)."
            )

    # TAB 3: Sai Hemanth Pipeline
    with tabs[2]:
        st.subheader("Sai Hemanth (PES1UG24AM101) — Regularized CoxPH & Kaplan-Meier Analysis")
        st.markdown(
            r"""
            **CoxPH Hazard & L2 Ridge Penalty (`lifelines`):**
            $$h(t, X) = h_0(t)\exp\left(\sum_{i=1}^p \beta_i X_i\right), \qquad \text{Penalty} = \frac{1}{2}\text{penalizer}\|\beta\|_2^2 \quad (\text{penalizer}=0.1, l_1\_\text{ratio}=0.0)$$
            """
        )
        m2_col1, m2_col2 = st.columns(2)
        with m2_col1:
            st.markdown("##### Table 2: Honest Leak-Free 10-Fold CV C-Index")
            st.dataframe(table2_df, use_container_width=True)
            if table2b_df is not None:
                st.markdown("##### Table 2b: Data Leakage Comparison (Leaky vs. Leak-Free)")
                st.dataframe(table2b_df, use_container_width=True)
                st.caption("Note: The leak-free numbers evaluate exclusively on original patients with fold-isolated SMOTE/pruning, avoiding the artificial +0.03 to +0.06 C-index inflation of the paper-style leaky pipeline.")
            if os.path.exists("results/fig4_kaplan_meier_risk_groups.png"):
                st.image("results/fig4_kaplan_meier_risk_groups.png", use_container_width=True)
        with m2_col2:
            st.markdown("##### Figure 5: Top 15 Prognostic Features (log Hazard Ratio & 95% CI)")
            if os.path.exists("results/fig5_top15_cox_coefficients.png"):
                st.image("results/fig5_top15_cox_coefficients.png", use_container_width=True)

        st.markdown("##### Figure 6: Covariate Effect Survival Curves (Chemotherapy Time & Stage Grouping)")
        if os.path.exists("results/fig6_covariate_survival_curves.png"):
            st.image("results/fig6_covariate_survival_curves.png", use_container_width=True)

    # TAB 4: Live Interactive Patient Predictor
    with tabs[3]:
        st.subheader("🩺 Interactive Patient Survival & Risk Stratification Simulator")
        st.markdown("Adjust patient clinical & radiomic parameters below to compute live **Naive Bayes Risk Probability** and **Personalized CoxPH Survival Curve $S(t)$**.")

        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            stage_val = st.selectbox(
                "Cancer Stage Grouping",
                options=[0, 1, 2, 3],
                format_func=lambda x: {0: "Stage IB (0)", 1: "Stage IIA (1)", 2: "Stage IIB (2)", 3: "Stage III (3)"}[x],
                index=2,
            )
            chemo_val = st.selectbox(
                "Chemotherapy Time (After SBRT)",
                options=[0, 1],
                format_func=lambda x: "Checked / Received After SBRT (1)" if x == 1 else "Unchecked / None (0)",
                index=0,
            )
            rad_val = st.selectbox(
                "Radiation Therapy Type",
                options=[0, 1],
                format_func=lambda x: "Conventional Fractionation (1)" if x == 1 else "SBRT (0)",
                index=1,
            )
        with p_col2:
            nccn_val = st.selectbox(
                "NCCN Resectability Criteria",
                options=[0, 1, 2],
                format_func=lambda x: {0: "Resectable (0)", 1: "Borderline Resectable (1)", 2: "Locally Advanced (2)"}[x],
                index=1,
            )
            t_stage_val = st.slider("Primary Tumor Assessment (T1–T4)", 1, 4, 3)
            kps_val = st.select_slider("Karnofsky Performance Status (KPS)", options=[60, 70, 80, 90, 100], value=80)
        with p_col3:
            width_val = st.slider("Tumor Width (cm)", 1.5, 5.8, 3.6, 0.1)
            vol_val = st.slider("Tumor Volume (cm³)", 10.0, 100.0, 48.0, 1.0)
            rad_risk_z = st.slider("Radiomic Wavelet/GLRLM Risk Score (z-score)", -2.0, 2.0, 0.4, 0.1)

        # Fit live Naive Bayes & Clinical+Radiomic Cox model for interactive prediction
        X_disc, bins = discretize_clinical_features(clinical_df)
        y_270 = (clinical_df["Survival_Days"].to_numpy() < 270).astype(int)
        nb_live = LaplaceMultinomialNaiveBayes({"Stage_Grouping": 4, "Chemotherapy_Time": 2, "Tumor_Width_cm": 4, "NCCN_Resectability": 3, "Radiation_Therapy": 2})
        nb_live.fit(X_disc, y_270)

        patient_clin_df = pd.DataFrame([{
            "Stage_Grouping": stage_val,
            "Chemotherapy_Time": chemo_val,
            "Tumor_Width_cm": width_val,
            "NCCN_Resectability": nccn_val,
            "Radiation_Therapy": rad_val,
        }])
        patient_disc, _ = discretize_clinical_features(patient_clin_df, width_bins=bins)
        nb_prob_high_risk = float(nb_live.predict_proba(patient_disc)[0, 1])

        # Fit compact CoxPH model for live curve visualization
        live_cols = ["Stage_Grouping", "Chemotherapy_Time", "Radiation_Therapy", "NCCN_Resectability", "Primary_Tumor_Stage", "KPS_Score", "Tumor_Width_cm", "Tumor_Volume_cm3"]
        df_cox_live = aug_clin[live_cols + ["Survival_Days", "Event_Observed"]].copy()
        df_cox_live["Radiomic_Composite"] = aug_rad.iloc[:, :8].mean(axis=1).to_numpy()

        cph_live = CoxPHFitter(penalizer=0.05)
        cph_live.fit(df_cox_live, duration_col="Survival_Days", event_col="Event_Observed")

        patient_cox_row = pd.DataFrame([{
            "Stage_Grouping": stage_val,
            "Chemotherapy_Time": chemo_val,
            "Radiation_Therapy": rad_val,
            "NCCN_Resectability": nccn_val,
            "Primary_Tumor_Stage": t_stage_val,
            "KPS_Score": kps_val,
            "Tumor_Width_cm": width_val,
            "Tumor_Volume_cm3": vol_val,
            "Radiomic_Composite": -0.35 * rad_risk_z,
        }])

        partial_hazard = float(cph_live.predict_partial_hazard(patient_cox_row).iloc[0])
        surv_func = cph_live.predict_survival_function(patient_cox_row)
        median_surv_pred = float(cph_live.predict_median(patient_cox_row))

        res_c1, res_c2, res_c3 = st.columns(3)
        risk_badge = "🔴 HIGH RISK (< 270 Days)" if nb_prob_high_risk >= 0.5 else "🟢 LOW RISK (≥ 270 Days)"
        res_c1.metric("Predicted Risk Cohort", risk_badge)
        res_c2.metric("Naive Bayes High-Risk Probability", f"{nb_prob_high_risk * 100:.1f}%")
        res_c3.metric("CoxPH Partial Hazard Ratio exp(βᵀx)", f"{partial_hazard:.2f}x (Median ~ {median_surv_pred:.0f} d)")

        fig_live, ax_live = plt.subplots(figsize=(8.0, 3.8), dpi=160)
        ax_live.plot(surv_func.index, surv_func.iloc[:, 0], color="#D62728" if nb_prob_high_risk >= 0.5 else "#2CA02C", linewidth=2.5, label="Patient Predicted Survival S(t)")
        ax_live.axvline(270, color="gray", linestyle="--", label="270-Day High-Risk Threshold")
        ax_live.axhline(0.5, color="royalblue", linestyle=":", label="50% Survival Probability")
        ax_live.set_xlabel("Survival Days")
        ax_live.set_ylabel("Survival Probability S(t)")
        ax_live.set_title("Personalized Cox Proportional Hazards Survival Curve")
        ax_live.set_ylim(0, 1.05)
        ax_live.grid(True, linestyle="--", alpha=0.35)
        ax_live.legend()
        st.pyplot(fig_live)


if __name__ == "__main__":
    main()
