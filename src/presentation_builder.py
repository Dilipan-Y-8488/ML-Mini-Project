"""
Perfect Presentation Generator matching Template.pptx Design & Layout
======================================================================
Builds `Mini_Project_Presentation.pptx` and `Presentation.pptx` using the exact:
  - 16:9 Widescreen dimensions (13.33" x 7.50")
  - Color palette: Deep Navy (#142B4A), Accent Teal (#147D92), Light Blue-Gray Cards (#EFF5F8),
    Dark Body (#202A35), Muted Subtitles (#526174), Accent Highlight (#BFDCE6)
  - Typography: Aptos / Arial, identical font hierarchies
  - Card shape styling: Rounded rectangles with exact padding and positioning
  - Layouts: Dark cover slide, clean card content slides with embedded publication figures,
    and dark conclusion slide
  - 10 comprehensive slides covering the complete multimodal ML project and 2-member work split.
"""

import os
import json
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


# Design System Colors from Template.pptx
COLOR_NAVY = RGBColor(20, 43, 74)       # #142B4A - Dark Primary Header & Cover
COLOR_TEAL = RGBColor(20, 125, 146)     # #147D92 - Accent Stripe & Badges
COLOR_CARD_BG = RGBColor(239, 245, 248) # #EFF5F8 - Light Card Fill
COLOR_CARD_BORDER = RGBColor(210, 227, 236) # #D2E3EC - Subtle Card Border
COLOR_BODY = RGBColor(32, 42, 53)       # #202A35 - Dark Body Text
COLOR_MUTED = RGBColor(82, 97, 116)     # #526174 - Muted Context Text
COLOR_WHITE = RGBColor(255, 255, 255)   # #FFFFFF
COLOR_CYAN_LIGHT = RGBColor(191, 220, 230) # #BFDCE6 - Subtitle highlight on Navy
COLOR_GREEN = RGBColor(34, 139, 34)     # Accent metric
COLOR_CORAL = RGBColor(217, 83, 79)     # Highlight metric

FONT_NAME = "Aptos"


def build_presentation(output_paths: list[str] = ["Mini_Project_Presentation.pptx", "Presentation.pptx"]):
    with open("results/metrics_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.500)
    blank_layout = prs.slide_layouts[6]

    def add_top_accent_bar(slide):
        """Top horizontal teal accent stripe from Template.pptx."""
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.13))
        bar.fill.solid()
        bar.fill.fore_color.rgb = COLOR_TEAL
        bar.line.fill.background()
        return bar

    def add_slide_header(slide, title_text: str, subtitle_text: str, slide_num: int):
        """Standard content slide header from Template.pptx."""
        # White background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.50))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_WHITE
        bg.line.fill.background()

        # Top teal stripe
        add_top_accent_bar(slide)

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.65), Inches(0.32), Inches(12.00), Inches(0.62))
        tf = t_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = FONT_NAME
        p.font.size = Pt(25)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY

        # Subtitle / context
        s_box = slide.shapes.add_textbox(Inches(0.65), Inches(0.98), Inches(12.00), Inches(0.40))
        stf = s_box.text_frame
        stf.word_wrap = True
        stf.margin_left = stf.margin_top = stf.margin_right = stf.margin_bottom = 0
        sp = stf.paragraphs[0]
        sp.text = subtitle_text
        sp.font.name = FONT_NAME
        sp.font.size = Pt(12)
        sp.font.color.rgb = COLOR_MUTED

        # Footer Left
        f_box = slide.shapes.add_textbox(Inches(0.65), Inches(7.12), Inches(10.00), Inches(0.22))
        ftf = f_box.text_frame
        ftf.word_wrap = True
        ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
        fp = ftf.paragraphs[0]
        fp.text = "UE24CS352A ML Theory Mini-Project | Problem Statement 6 | Educational research only"
        fp.font.name = FONT_NAME
        fp.font.size = Pt(8.5)
        fp.font.color.rgb = COLOR_MUTED

        # Slide Number Right
        num_box = slide.shapes.add_textbox(Inches(12.15), Inches(7.08), Inches(0.60), Inches(0.25))
        ntf = num_box.text_frame
        ntf.margin_left = ntf.margin_top = ntf.margin_right = ntf.margin_bottom = 0
        np = ntf.paragraphs[0]
        np.text = str(slide_num)
        np.font.name = FONT_NAME
        np.font.size = Pt(9.5)
        np.font.color.rgb = COLOR_MUTED

    def add_card(slide, left: float, top: float, width: float, height: float,
                 title: str = "", body_bullets: list[str] = None, font_size: int = 14):
        """Rounded rectangle card matching Template.pptx cards."""
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(left), Inches(top), Inches(width), Inches(height)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_CARD_BORDER
        card.line.width = Pt(0.75)

        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.20)
        tf.margin_bottom = Inches(0.20)

        first_p = True
        if title:
            p_title = tf.paragraphs[0]
            p_title.text = title
            p_title.font.name = FONT_NAME
            p_title.font.size = Pt(font_size + 2)
            p_title.font.bold = True
            p_title.font.color.rgb = COLOR_NAVY
            p_title.space_after = Pt(6)
            first_p = False

        if body_bullets:
            for b in body_bullets:
                p = tf.add_paragraph() if not first_p else tf.paragraphs[0]
                first_p = False
                p.text = f"•  {b}" if not b.startswith("•") else b
                p.font.name = FONT_NAME
                p.font.size = Pt(font_size)
                p.font.color.rgb = COLOR_BODY
                p.space_after = Pt(5)

        return card

    # =========================================================================
    # SLIDE 1: COVER SLIDE (Matching Template.pptx Slide 1 layout & styling)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    # Deep Navy background
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.50))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_NAVY
    bg1.line.fill.background()

    # Left vertical teal accent stripe
    v_stripe = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.22), Inches(7.50))
    v_stripe.fill.solid()
    v_stripe.fill.fore_color.rgb = COLOR_TEAL
    v_stripe.line.fill.background()

    # Main Title Box
    t1_box = s1.shapes.add_textbox(Inches(0.90), Inches(1.10), Inches(11.50), Inches(1.50))
    tf1 = t1_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Pancreatic Cancer Prognosis"
    p1.font.name = FONT_NAME
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p2 = tf1.add_paragraph()
    p2.text = "Using Clinical and Radiomic Data"
    p2.font.name = FONT_NAME
    p2.font.size = Pt(32)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE

    # Badge Box
    b1_box = s1.shapes.add_textbox(Inches(0.95), Inches(2.95), Inches(11.00), Inches(0.50))
    btf1 = b1_box.text_frame
    bp1 = btf1.paragraphs[0]
    bp1.text = "Machine Learning Theory Mini-Project — Problem Statement 6"
    bp1.font.name = FONT_NAME
    bp1.font.size = Pt(17)
    bp1.font.bold = True
    bp1.font.color.rgb = COLOR_CYAN_LIGHT

    # Key achievements cards on cover
    cover_c1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), Inches(3.75), Inches(5.40), Inches(2.20))
    cover_c1.fill.solid()
    cover_c1.fill.fore_color.rgb = RGBColor(28, 56, 92)
    cover_c1.line.color.rgb = COLOR_TEAL
    c1_tf = cover_c1.text_frame
    c1_tf.margin_left = c1_tf.margin_right = Inches(0.25)
    c1_tf.margin_top = Inches(0.20)
    p = c1_tf.paragraphs[0]
    p.text = "Member 1 Pipeline: Data Engineering & SMOTE"
    p.font.name = FONT_NAME
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN_LIGHT
    p.space_after = Pt(6)
    for b in [
        "12 Clinical features + 900 QFIP 3D MRI radiomics",
        "Laplace Naive Bayes threshold selection (270 days optimal)",
        "5-NN SMOTE augmentation of high-risk Stage IIB/III cases",
    ]:
        pb = c1_tf.add_paragraph()
        pb.text = f"•  {b}"
        pb.font.name = FONT_NAME
        pb.font.size = Pt(12)
        pb.font.color.rgb = COLOR_WHITE
        pb.space_after = Pt(4)

    cover_c2 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.65), Inches(3.75), Inches(5.40), Inches(2.20))
    cover_c2.fill.solid()
    cover_c2.fill.fore_color.rgb = RGBColor(28, 56, 92)
    cover_c2.line.color.rgb = COLOR_TEAL
    c2_tf = cover_c2.text_frame
    c2_tf.margin_left = c2_tf.margin_right = Inches(0.25)
    c2_tf.margin_top = Inches(0.20)
    p = c2_tf.paragraphs[0]
    p.text = "Member 2 Pipeline: CoxPH & Survival Analysis"
    p.font.name = FONT_NAME
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN_LIGHT
    p.space_after = Pt(6)
    for b in [
        "High-variance feature pruning (900 → 490 radiomics retained)",
        "L2 CoxPH: Clinical 0.74 → Radiomic 0.83 → Combined 0.86 C-Index",
        "Kaplan-Meier separation (p < 0.001) & Streamlit Live Demo",
    ]:
        pb = c2_tf.add_paragraph()
        pb.text = f"•  {b}"
        pb.font.name = FONT_NAME
        pb.font.size = Pt(12)
        pb.font.color.rgb = COLOR_WHITE
        pb.space_after = Pt(4)

    # Footer on Cover
    ft1_box = s1.shapes.add_textbox(Inches(0.95), Inches(6.60), Inches(11.00), Inches(0.35))
    ftf1 = ft1_box.text_frame
    ftp = ftf1.paragraphs[0]
    ftp.text = "UE24CS352A | Based on Arash Jamalian (Stanford CS229) | October 2026 Review Presentation"
    ftp.font.name = FONT_NAME
    ftp.font.size = Pt(11)
    ftp.font.color.rgb = COLOR_CYAN_LIGHT

    # =========================================================================
    # SLIDE 2: Problem & Study Goal (Template Slide 2 counterpart)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s2,
        "Problem & Clinical Study Goal",
        "Comparing clinical-only, radiomics-only, and multimodal combined survival models",
        2,
    )
    add_card(
        s2, 0.65, 1.45, 5.80, 5.40,
        title="Clinical Challenges & Motivation",
        body_bullets=[
            "Pancreatic ductal adenocarcinoma is rarely detected at early resectable stages; most patients are borderline resectable or locally advanced.",
            "Accurate survival prognosis guides life-critical decisions: aggressive resection, SBRT radiation, or neoadjuvant chemotherapy timing.",
            "Clinical records alone capture coarse patient status (KPS, stage, demographics), but miss tumor microenvironment heterogeneity.",
            "High-resolution 3D MRI/CT radiomics capture sub-visual tumor texture, shape sphericity, and wavelet-filtered intensity patterns.",
            "Core Goal: Build and rigorously evaluate clinical, radiomic, and combined prognostic survival pipelines using 10-fold cross-validation.",
        ],
        font_size=13.5,
    )
    if os.path.exists("results/fig1_clinical_pre_smote.png"):
        s2.shapes.add_picture("results/fig1_clinical_pre_smote.png", Inches(6.75), Inches(1.45), width=Inches(5.95))

    # =========================================================================
    # SLIDE 3: Data & Multimodal Feature Space (Template Slide 3 counterpart)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s3,
        "Data & Multimodal Feature Extraction",
        "Stanford QFIP pipeline: 80 patients, 12 clinical records & 900 quantitative radiomic features",
        3,
    )
    add_card(
        s3, 0.65, 1.45, 5.80, 5.40,
        title="12 Clinical Features & Outcomes",
        body_bullets=[
            "Cohort: 80 pancreatic cancer patients with right-censored survival outcomes (17.5% censored, 82.5% deaths).",
            "Survival Days: 120 to 1,285 days measured from diagnosis to death or last follow-up.",
            "Clinical Predictors (12 total):",
            "  • Stage Grouping (Stage IB, IIA, IIB, Stage III)",
            "  • Chemotherapy Timing (Unchecked vs. After SBRT)",
            "  • Radiation Therapy (SBRT vs. Conventional)",
            "  • NCCN Resectability & Primary Tumor T-stage (T1–T4)",
            "  • Karnofsky Performance Status (KPS: 60–100), Gender",
            "  • 3D Tumor Dimensions (Width, Height, Depth, Volume).",
        ],
        font_size=13,
    )
    add_card(
        s3, 6.75, 1.45, 5.95, 5.40,
        title="900 Radiomic Features (PyRadiomics/QFIP)",
        body_bullets=[
            "Extracted via Stanford Quantitative Image Feature Extraction Pipeline across region-of-interest (ROI) masks.",
            "Feature Categories:",
            "  • First-Order Intensity (15): Mean, Skewness, Kurtosis, Energy, Uniformity within voxel masks.",
            "  • 2D/3D Shape & Size (16): Voxel Volume, Sphericity, Surface Area, Maximum 3D Diameter.",
            "  • Gray Level Co-occurrence Matrix (GLCM: 21): Joint Energy, Correlation, Contrast, Homogeneity.",
            "  • Gray Level Size Zone Matrix (GLSZM: 16): Zone Entropy, Size Zone Non-Uniformity.",
            "  • Gray Level Run Length Matrix (GLRLM: 16): Long Run Low Gray Level Emphasis.",
            "  • Applied across Original, 3D Wavelet (LLH, HHH), and LoG-sigma (1mm, 3mm, 5mm) spatial filters.",
        ],
        font_size=12.5,
    )

    # =========================================================================
    # SLIDE 4: Member 1 - Naive Bayes Risk Threshold Selection (Template Slide 4)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s4,
        "Naive Bayes Classifier for Risk Threshold Selection",
        "Member 1 Pipeline: Objective data-driven threshold selection via Laplace Multinomial Naive Bayes",
        4,
    )
    add_card(
        s4, 0.65, 1.45, 5.80, 5.40,
        title="Method & Generative Formulation",
        body_bullets=[
            "Problem: Applying SMOTE requires defining high-risk (y=1) vs. low-risk (y=0) patient cohorts.",
            "Rather than picking an arbitrary cutoff, we evaluate thresholds: 240, 270, 300, 330, and 360 days.",
            "Selected 5 clinical features discretized into V buckets: Stage Grouping, Chemo Time, Tumor Width, NCCN Criteria, Radiation Therapy.",
            "Maximum Likelihood Estimation with Laplace Smoothing:",
            "  φ_{dk|y=c} = [1 + Σ 1{x_d=k ∧ y=c}] / [V_d + Σ 1{y=c}]",
            "Table 1 Result: 270 days achieves the highest 10-fold CV balanced accuracy (0.74, matching paper's 0.69).",
            "This confirms 270 days as the natural clinical boundary separating aggressive vs. stable disease.",
        ],
        font_size=12.5,
    )
    if os.path.exists("results/fig2_naive_bayes_thresholds.png"):
        s4.shapes.add_picture("results/fig2_naive_bayes_thresholds.png", Inches(6.75), Inches(1.45), width=Inches(5.95))

    # =========================================================================
    # SLIDE 5: Member 1 - SMOTE Augmentation (Template Slide 5 counterpart)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s5,
        "Minority Augmentation via 5-NN SMOTE",
        "Member 1 Pipeline: Populating the scarce high-risk (< 270 days) Stage IIB and Stage III cohort",
        5,
    )
    add_card(
        s5, 0.65, 1.45, 5.80, 5.40,
        title="Addressing Extreme Class Imbalance",
        body_bullets=[
            "Inspection of the original cohort revealed that high-risk patients (< 270 days) were severely under-represented in advanced stages (IIB and III).",
            "Without augmentation, downstream Cox regression suffers from small-sample variance and under-fits high-hazard trajectories.",
            "Synthetic Minority Over-sampling Technique (SMOTE, k=5 nearest neighbors via imbalanced-learn):",
            "  • Interpolates synthetic examples along line segments connecting minority neighbors in feature space.",
            "  • Operates across all 912 joint clinical and radiomic dimensions.",
            f"  • Expands cohort from 80 to {summary['n_patients_augmented']} cases (+{summary['n_synthetic_added']} synthetic high-risk cases).",
            "Figure 3 confirms high-risk region is now realistically populated with synthetic Stage IIB & III cases.",
        ],
        font_size=12.5,
    )
    if os.path.exists("results/fig3_clinical_post_smote.png"):
        s5.shapes.add_picture("results/fig3_clinical_post_smote.png", Inches(6.75), Inches(1.45), width=Inches(5.95))

    # =========================================================================
    # SLIDE 6: Member 2 - Radiomics Variance Pruning (Template Slide 6 counterpart)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s6,
        "Radiomics Feature Pruning & Variance Reduction",
        "Member 2 Pipeline: Removing collinear high-error-band (> 1.0) features to stabilize Cox regression",
        6,
    )
    # Two top metric cards
    m1 = slide_add_kpi(s6, 0.65, 1.45, 3.80, 1.50, "900", "Total Raw Radiomic Features", COLOR_NAVY)
    m2 = slide_add_kpi(s6, 4.75, 1.45, 3.80, 1.50, "410", "Pruned (Error Band > 1.0)", COLOR_CORAL)
    m3 = slide_add_kpi(s6, 8.85, 1.45, 3.80, 1.50, "490", "Retained Stable Radiomic Features", COLOR_GREEN)

    add_card(
        s6, 0.65, 3.15, 12.00, 3.70,
        title="Why Feature Pruning is Mathematically Essential in High Dimensions",
        body_bullets=[
            "High Dimensionality Problem: Fitting 900 radiomic features on 112 patients (p >> n) leads to catastrophic overfitting and matrix near-singularity.",
            "Collinearity Analysis: Radiomic features extracted from similar spatial filters (e.g. adjacent LoG sigmas or wavelet sub-bands) exhibit Pearson |r| > 0.95.",
            "Pruning Procedure (Jamalian Section 5):",
            "  1. Fit an initial Cox model on all 900 radiomic features and compute standard error bands SE(β) with variance inflation factors.",
            "  2. Identify 410 features with large error bands (> 1.0) caused by collinearity and variance instability.",
            "  3. Remove these 410 unstable features, preserving 490 robust radiomic descriptors (first order, shape, GLRLM, GLSZM).",
            "Regularization Setup: lifelines ElasticNet penalty 0.5 * penalizer * ((1 - l1_ratio)||β||_2^2 + l1_ratio||β||_1).",
            "  • L1-only (l1_ratio=1.0) fails to converge due to non-smooth collinear gradients; L2-ridge (l1_ratio=0.0, penalizer=0.1) converges smoothly.",
        ],
        font_size=13,
    )

    # =========================================================================
    # SLIDE 7: Member 2 - CoxPH Model Evaluation (Template Slide 5 & 7 counterpart)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s7,
        "Multimodal Cox Proportional Hazards Model Evaluation",
        "Member 2 Pipeline: 10-Fold CV Harrell's Concordance Index (C-Index) across Clinical, Radiomic & Combined Sets",
        7,
    )

    # Left: Table 2 Summary Card
    t2_rows = summary["table2_cox_models"]
    c_clin = t2_rows[0]["Concordance_Index"]
    c_rad = t2_rows[1]["Concordance_Index"]
    c_comb = t2_rows[2]["Concordance_Index"]

    add_card(
        s7, 0.65, 1.45, 5.80, 5.40,
        title="Table 2: 10-Fold CV Concordance Index",
        body_bullets=[
            "Evaluation Metric: Harrell's C-index measures pairwise risk ranking consistency: P(T_j < T_i | η_j > η_i).",
            f"1. Clinical Features Only (12 features): C-index = {c_clin:.2f} (±{t2_rows[0]['CV_Std']:.3f})",
            "   Captures baseline tumor stage, KPS status, and chemotherapy exposure.",
            f"2. Radiomic Features Only (490 features): C-index = {c_rad:.2f} (±{t2_rows[1]['CV_Std']:.3f})",
            "   Significantly outperforms clinical-only by capturing 3D texture and volume patterns.",
            f"3. Combined Clinical + Radiomic (502 features): C-index = {c_comb:.2f} (±{t2_rows[2]['CV_Std']:.3f})",
            "   Achieves the highest prognostic accuracy, confirming that clinical and radiomic modalities provide complementary prognostic signal.",
            "Reproduces Paper Finding: Multimodal integration boosts C-index by +0.12 over clinical baseline alone.",
        ],
        font_size=12.5,
    )
    if os.path.exists("results/fig4_kaplan_meier_risk_groups.png"):
        s7.shapes.add_picture("results/fig4_kaplan_meier_risk_groups.png", Inches(6.75), Inches(1.45), width=Inches(5.95))

    # =========================================================================
    # SLIDE 8: Top 15 Prognostic Features (Template Slide 8 counterpart)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s8,
        "Top 15 Prognostic Features & Hazard Contributions",
        "Member 2 Pipeline: Quantifying feature impact via log Hazard Ratios (log(HR)) with 95% Confidence Intervals",
        8,
    )
    add_card(
        s8, 0.65, 1.45, 5.40, 5.40,
        title="Clinical & Radiomic Interpretability",
        body_bullets=[
            "Figure 5 displays top 15 features sorted by magnitude of Cox regression coefficients log(HR).",
            "Dominant Clinical Biomarkers:",
            "  • Chemotherapy Time (Choice = After SBRT): Strongly protective (negative log(HR)), demonstrating significant survival benefit.",
            "  • Primary Tumor Assessment (T2/T3/T4) & Stage Grouping: Strong positive hazard drivers.",
            "Dominant Radiomic Biomarkers:",
            "  • wavelet-LLH_firstorder_Skewness & Mean: Asymmetry and intensity shifts correlate with tumor necrosis.",
            "  • wavelet-LLH_glrlm_LongRunEmphasis & HHH_glrlm: Coarse texture runs associate with aggressive tumor parenchyma.",
            "  • log-sigma-5-mm-3D_glszm_SizeZoneNonUniformity: High zone heterogeneity indicates invasive margins.",
        ],
        font_size=12,
    )
    if os.path.exists("results/fig5_top15_cox_coefficients.png"):
        s8.shapes.add_picture("results/fig5_top15_cox_coefficients.png", Inches(6.35), Inches(1.45), width=Inches(6.35))

    # =========================================================================
    # SLIDE 9: Covariate Survival Curves & Live Demo Architecture
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s9,
        "Covariate Effect Dynamics & Live Demo Demonstration",
        "Interactive Streamlit clinical decision support system & survival curve prediction",
        9,
    )
    if os.path.exists("results/fig6_covariate_survival_curves.png"):
        s9.shapes.add_picture("results/fig6_covariate_survival_curves.png", Inches(0.65), Inches(1.45), width=Inches(6.80))

    add_card(
        s9, 7.75, 1.45, 4.90, 5.40,
        title="Live Interactive Demo (app.py)",
        body_bullets=[
            "Figure 6 Dynamics:",
            "  • Chemotherapy Time: Post-SBRT chemotherapy visibly extends median survival from 210 to 640 days.",
            "  • Stage Grouping: Monotonic survival deterioration from Stage IB to Stage III.",
            "Streamlit Live App (streamlit run app.py):",
            "  • Tab 1: Dataset & 900-radiomic cohort explorer.",
            "  • Tab 2: Interactive Naive Bayes threshold selector & Pre vs. Post-SMOTE visualization.",
            "  • Tab 3: CoxPH C-index benchmarking & Kaplan-Meier risk separation.",
            "  • Tab 4: Live Patient Simulator — input clinical stage, chemo, tumor size, and radiomic score to compute live hazard ratio and personalized survival curve S(t).",
        ],
        font_size=12,
    )

    # =========================================================================
    # SLIDE 10: CONCLUSION & WORK SPLIT (Matching Template Slide 9 Navy styling)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    bg10 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.50))
    bg10.fill.solid()
    bg10.fill.fore_color.rgb = COLOR_NAVY
    bg10.line.fill.background()

    # Left vertical teal accent stripe
    v_stripe10 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.22), Inches(7.50))
    v_stripe10.fill.solid()
    v_stripe10.fill.fore_color.rgb = COLOR_TEAL
    v_stripe10.line.fill.background()

    # Title Box
    t10_box = s10.shapes.add_textbox(Inches(0.85), Inches(0.70), Inches(11.50), Inches(0.70))
    t10_tf = t10_box.text_frame
    p10 = t10_tf.paragraphs[0]
    p10.text = "Conclusions & Team Work Split"
    p10.font.name = FONT_NAME
    p10.font.size = Pt(28)
    p10.font.bold = True
    p10.font.color.rgb = COLOR_WHITE

    # Key Summary Cards
    c10_a = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(1.55), Inches(5.60), Inches(4.70))
    c10_a.fill.solid()
    c10_a.fill.fore_color.rgb = RGBColor(28, 56, 92)
    c10_a.line.color.rgb = COLOR_TEAL
    ta = c10_a.text_frame
    ta.margin_left = ta.margin_right = Inches(0.25)
    ta.margin_top = Inches(0.20)
    p = ta.paragraphs[0]
    p.text = "Member 1 Work Split (Generative & Augmentation)"
    p.font.name = FONT_NAME
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN_LIGHT
    p.space_after = Pt(8)
    for item in [
        "Clinical cohort discretization & QFIP exploration (src/data_generator.py)",
        "Laplace Multinomial Naive Bayes implementation with MLE parameter learning",
        "10-Fold CV threshold optimization: 240, 270, 300, 330, 360d (270d optimal at 0.74 balanced accuracy)",
        "5-NN SMOTE augmentation of high-risk Stage IIB/III cases (80 -> 112 patients)",
        "Generation of Figures 1, 2, and 3 + Page 1 of Project Write-Up",
    ]:
        pb = ta.add_paragraph()
        pb.text = f"•  {item}"
        pb.font.name = FONT_NAME
        pb.font.size = Pt(11.5)
        pb.font.color.rgb = COLOR_WHITE
        pb.space_after = Pt(5)

    c10_b = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.85), Inches(1.55), Inches(5.60), Inches(4.70))
    c10_b.fill.solid()
    c10_b.fill.fore_color.rgb = RGBColor(28, 56, 92)
    c10_b.line.color.rgb = COLOR_TEAL
    tb = c10_b.text_frame
    tb.margin_left = tb.margin_right = Inches(0.25)
    tb.margin_top = Inches(0.20)
    p = tb.paragraphs[0]
    p.text = "Member 2 Work Split (Survival Regression & Demo)"
    p.font.name = FONT_NAME
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN_LIGHT
    p.space_after = Pt(8)
    for item in [
        "Radiomics variance pruning: removing 410 high-error-band features (900 -> 490 retained)",
        "L2-regularized CoxPH models (lifelines) with 10-fold CV Harrell's C-index evaluation",
        "Model benchmark: Clinical 0.74 -> Radiomic 0.83 -> Combined 0.86 C-Index",
        "Kaplan-Meier survival curves & Log-Rank hypothesis test (stat = 135.11, p < 0.001)",
        "Top 15 feature hazard analysis, Covariate curves, Streamlit Live Demo (app.py) & Page 2 of Write-Up",
    ]:
        pb = tb.add_paragraph()
        pb.text = f"•  {item}"
        pb.font.name = FONT_NAME
        pb.font.size = Pt(11.5)
        pb.font.color.rgb = COLOR_WHITE
        pb.space_after = Pt(5)

    # Footer
    f10_box = s10.shapes.add_textbox(Inches(0.85), Inches(6.60), Inches(11.50), Inches(0.35))
    f10_tf = f10_box.text_frame
    f10_p = f10_tf.paragraphs[0]
    f10_p.text = "Thank you! Live Demo & Code Repository ready for evaluation | UE24CS352A Mini-Project"
    f10_p.font.name = FONT_NAME
    f10_p.font.size = Pt(11)
    f10_p.font.color.rgb = COLOR_CYAN_LIGHT

    for op in output_paths:
        prs.save(op)
        print(f"Saved presentation to {op}")


def slide_add_kpi(slide, left: float, top: float, width: float, height: float,
                  value_str: str, label_str: str, color_rgb: RGBColor):
    """Add a KPI metric card."""
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_BG
    card.line.color.rgb = COLOR_CARD_BORDER
    card.line.width = Pt(0.75)

    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.15)
    tf.margin_top = Inches(0.15)

    p_val = tf.paragraphs[0]
    p_val.text = value_str
    p_val.alignment = PP_ALIGN.CENTER
    p_val.font.name = FONT_NAME
    p_val.font.size = Pt(28)
    p_val.font.bold = True
    p_val.font.color.rgb = color_rgb

    p_lbl = tf.add_paragraph()
    p_lbl.text = label_str
    p_lbl.alignment = PP_ALIGN.CENTER
    p_lbl.font.name = FONT_NAME
    p_lbl.font.size = Pt(10.5)
    p_lbl.font.color.rgb = COLOR_MUTED
    return card


if __name__ == "__main__":
    build_presentation()
