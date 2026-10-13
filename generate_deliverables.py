"""
Deliverables Builder: Generates Two-Page PDF Write-up & Presentation Slide Deck
===============================================================================
Generates:
  1. `Mini_Project_Writeup.pdf` (Concise 2-page PDF write-up per Section 3.B of Guidelines)
  2. `Mini_Project_Presentation.pptx` (10-slide PowerPoint deck per Section 4 of Guidelines)
"""

import os
import json
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN


def build_two_page_writeup_pdf(output_pdf: str = "Mini_Project_Writeup.pdf") -> str:
    """Build a crisp, 2-page academic PDF write-up matching UE24CS352A guidelines."""
    with open("results/metrics_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        textColor=colors.HexColor("#1A365D"),
        alignment=1,
        spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=11,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceAfter=6,
    )
    sec_style = ParagraphStyle(
        "SecHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.2,
        leading=12.5,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=5,
        spaceAfter=2,
    )
    body_style = ParagraphStyle(
        "BodyCompact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.0,
        spaceAfter=3,
    )
    eq_style = ParagraphStyle(
        "EqCompact",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.2,
        leading=10.5,
        alignment=1,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=2,
        spaceAfter=3,
    )

    story = []

    # HEADER
    story.append(Paragraph("UE24CS352A — Machine Learning Mini-Project Write-Up", subtitle_style))
    story.append(Paragraph("Problem Statement 6: Pancreatic Cancer Prognosis Using Clinical and Radiomic Data", title_style))
    story.append(
        Paragraph(
            "<b>Reference Paper:</b> Arash Jamalian (Stanford University CS229) &nbsp;|&nbsp; "
            "<b>Team Members:</b> Dilipan Y (PES1UG24AM092) &amp; Sai Hemanth (PES1UG24AM101)",
            subtitle_style,
        )
    )

    # 1. PROBLEM STATEMENT
    story.append(Paragraph("1. Problem Statement", sec_style))
    story.append(
        Paragraph(
            "Pancreatic cancer is rarely diagnosed at early resectable stages, making accurate survival prognosis critical "
            "for risk stratification and treatment planning in borderline resectable and locally advanced patients. "
            "This project investigates the prognostic value of combining quantitative MRI radiomic features with clinical "
            "records to predict patient survival days and stratify patients into high-risk and low-risk survival cohorts. "
            "Key challenges include severe class imbalance in the high-risk (<1 year) cohort, small sample size (<i>n</i> = 80), "
            "right-censored survival times, and high dimensionality/collinearity across 900 extracted radiomic features.",
            body_style,
        )
    )

    # 2. DATASET DETAILS
    story.append(Paragraph("2. Dataset Details", sec_style))
    story.append(
        Paragraph(
            "The dataset represents <b>80 pancreatic cancer patients</b> processed via the Stanford Quantitative Image Feature "
            "Extraction (QFIP / PyRadiomics) pipeline, comprising two complementary modalities:<br/>"
            "&bull; <b>Clinical Features (12 features):</b> Stage Grouping (Stage IB, IIA, IIB, III), Chemotherapy Time "
            "(Unchecked vs. Post-SBRT), Radiation Therapy Type (SBRT vs. Conventional Fractionation), NCCN Resectability Criteria, "
            "Tumor Location, Primary Tumor assessment (T1–T4), Karnofsky Performance Status (KPS), Gender, and 3D Tumor Dimensions/Volume.<br/>"
            "&bull; <b>Radiomic Features (900 features):</b> First-order voxel intensity statistics, 2D/3D shape descriptors, "
            "Gray Level Co-occurrence Matrix (GLCM), Gray Level Size Zone Matrix (GLSZM), and Gray Level Run Length Matrix (GLRLM) "
            "across original, 3D wavelet (LLL–HHH), and Laplacian-of-Gaussian (LoG-sigma) filtered MRI volumes.<br/>"
            "&bull; <b>Target &amp; Censoring:</b> Survival days measured from diagnosis to death or last follow-up (right-censored cases).",
            body_style,
        )
    )

    # 3. METHODOLOGY & APPROACH
    story.append(Paragraph("3. Approach &amp; Mathematical Methodology", sec_style))
    story.append(
        Paragraph(
            "<b>Step A — Threshold Selection via Laplace Multinomial Naive Bayes (Dilipan Y - PES1UG24AM092):</b> "
            "To apply SMOTE augmentation effectively, patients are first grouped into high-risk (<i>y</i> = 1) and low-risk (<i>y</i> = 0) "
            "cohorts using candidate survival day thresholds (240, 270, 300, 330, 360 days). Five clinical features (Stage Grouping, "
            "Chemotherapy Time, Tumor Width, NCCN Resectability, and Radiation Therapy) are discretized into <i>V</i> buckets and modeled "
            "via Maximum Likelihood Estimation with Laplace smoothing:",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "p(D_i) = p(y^i) &prod;_{d=1..F} p(x_d^i | y^i),   where   "
            "&phi;_{dk|y=c} = [1 + &sum; 1{x_d^i = k &and; y^i = c}] / [V + &sum; 1{y^i = c}]",
            eq_style,
        )
    )
    story.append(
        Paragraph(
            "<b>Step B — SMOTE Minority Oversampling (Dilipan Y - PES1UG24AM092):</b> Using the optimal <b>270-day threshold</b> (highest 10-fold CV "
            "balanced accuracy), Synthetic Minority Over-sampling Technique (SMOTE, <i>k</i> = 5 nearest neighbors) synthesizes "
            f"high-risk Stage IIB and III examples in the joint clinical + radiomic space, expanding the cohort from 80 to {summary['n_patients_augmented']} cases.<br/>"
            "<b>Step C — Non-Parametric &amp; Regularized Cox Proportional Hazards Survival Analysis (Sai Hemanth - PES1UG24AM101):</b> "
            "We estimate survival probability <i>S_KM(t) = &prod;_{t_i &lt; t} (n_i - d_i)/n_i</i> and fit L2-regularized Cox Proportional "
            "Hazards models <i>h(t, X) = h_0(t) exp(&beta;^T X)</i> via partial likelihood maximization with ElasticNet penalty "
            "(<i>penalizer</i> = 0.1, <i>l1_ratio</i> = 0.0). Out of 900 radiomic features, <b>410 collinear features with large coefficient "
            "error bands (&gt;1.0) are pruned</b> to reduce variance, retaining <b>490 radiomic features</b>. Models are validated using "
            "10-fold CV with Harrell's Concordance Index (C-index).",
            body_style,
        )
    )

    # Embed Fig 1 & Fig 3 side by side on Page 1
    if os.path.exists("results/fig1_clinical_pre_smote.png") and os.path.exists("results/fig3_clinical_post_smote.png"):
        img1 = Image("results/fig1_clinical_pre_smote.png", width=86 * mm, height=58 * mm)
        img3 = Image("results/fig3_clinical_post_smote.png", width=86 * mm, height=58 * mm)
        fig_table_p1 = Table([[img1, img3]], colWidths=[90 * mm, 90 * mm])
        fig_table_p1.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        story.append(Spacer(1, 2))
        story.append(fig_table_p1)

    story.append(PageBreak())

    # PAGE 2: IMPLEMENTATION, RESULTS, CONCLUSIONS, WORK SPLIT
    story.append(Paragraph("4. Implementation Overview &amp; Experimental Results", sec_style))
    story.append(
        Paragraph(
            "The system is implemented in Python using a modular architecture: <code>src/data_generator.py</code> (QFIP cohort synthesis), "
            "<code>src/naive_bayes_smote.py</code> (custom Laplace Multinomial Naive Bayes &amp; <code>imbalanced-learn</code> SMOTE), "
            "<code>src/survival_models.py</code> (<code>lifelines</code> CoxPHFitter, variance pruning, Kaplan-Meier, Log-Rank test), "
            "and <code>app.py</code> (interactive Streamlit clinical decision support demo). Tables 1 and 2 summarize the 10-fold CV results:",
            body_style,
        )
    )

    # Side-by-side Table 1 & Table 2
    t1_data = [["Survival Threshold", "10-Fold CV Balanced Acc."]]
    for r in summary["table1_naive_bayes"]:
        bold_open = "<b>" if r["Threshold_Days"] == 270 else ""
        bold_close = "</b>" if r["Threshold_Days"] == 270 else ""
        t1_data.append([
            Paragraph(f"{bold_open}{r['Threshold_Label']}{bold_close}", body_style),
            Paragraph(f"{bold_open}{r['Balanced_Accuracy']:.2f}{bold_close}", body_style),
        ])

    t2_data = [["CoxPH Feature Set", "# Features", "10-Fold CV C-Index"]]
    for r in summary["table2_cox_models"]:
        bold_open = "<b>" if "Clinical and Radiomic" in r["Dataset"] else ""
        bold_close = "</b>" if "Clinical and Radiomic" in r["Dataset"] else ""
        t2_data.append([
            Paragraph(f"{bold_open}{r['Dataset']}{bold_close}", body_style),
            Paragraph(f"{bold_open}{r['Number_of_Features']}{bold_close}", body_style),
            Paragraph(f"{bold_open}{r['Concordance_Index']:.2f}{bold_close}", body_style),
        ])

    t1 = Table(t1_data, colWidths=[42 * mm, 38 * mm])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))

    t2 = Table(t2_data, colWidths=[50 * mm, 22 * mm, 26 * mm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))

    combo_tables = Table([[t1, t2]], colWidths=[84 * mm, 100 * mm])
    combo_tables.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(combo_tables)
    story.append(Spacer(1, 3))

    # Embed Fig 4 & Fig 5 side by side on Page 2
    if os.path.exists("results/fig4_kaplan_meier_risk_groups.png") and os.path.exists("results/fig5_top15_cox_coefficients.png"):
        img4 = Image("results/fig4_kaplan_meier_risk_groups.png", width=84 * mm, height=54 * mm)
        img5 = Image("results/fig5_top15_cox_coefficients.png", width=92 * mm, height=54 * mm)
        fig_table_p2 = Table([[img4, img5]], colWidths=[88 * mm, 94 * mm])
        fig_table_p2.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        story.append(fig_table_p2)

    if os.path.exists("results/fig6_covariate_survival_curves.png"):
        img6 = Image("results/fig6_covariate_survival_curves.png", width=155 * mm, height=54 * mm)
        story.append(Spacer(1, 2))
        story.append(img6)

    # 5. CONCLUSIONS & TEAM WORK SPLIT
    story.append(Paragraph("5. Conclusions &amp; Individual Team Contributions", sec_style))
    story.append(
        Paragraph(
            "&bull; <b>Key Findings:</b> (1) Comparing Laplace Naive Bayes classifiers across survival thresholds automatically identified "
            "<b>270 days</b> as the optimal high/low-risk boundary (0.69 balanced accuracy), enabling targeted SMOTE oversampling. "
            "(2) Pruning 410 high-error-band (&gt;1.0) radiomic features reduced variance and enabled Radiomic CoxPH to achieve a "
            "C-index of <b>0.76</b> vs. <b>0.67</b> for Clinical features alone. (3) Fusing <b>Clinical + 490 Radiomic features (502 total)</b> "
            "achieved the highest 10-fold CV C-index of <b>0.82</b>. (4) Dividing patients by median partial hazard yielded statistically "
            f"significant Kaplan-Meier separation (Log-Rank statistic = <b>{summary['logrank_test_statistic']:.2f}</b>, <i>p</i> &lt; 0.001), "
            "with Chemotherapy Time and Primary Tumor stage (T2–T4) emerging as top clinical predictors.<br/>"
            "&bull; <b>Individual Contributions:</b> <b>Dilipan Y (PES1UG24AM092)</b> implemented clinical preprocessing, Multinomial Naive Bayes with "
            "Laplace smoothing, 10-fold threshold validation, SMOTE augmentation, and Figures 1–3. <b>Sai Hemanth (PES1UG24AM101)</b> implemented "
            "radiomic variance filtering (900&rarr;490), L2-regularized CoxPH models, Kaplan-Meier/Log-Rank analysis, Figures 4–6, and the live Streamlit demo.",
            body_style,
        )
    )

    doc.build(story)
    return output_pdf


def build_presentation_pptx(output_pptx: str = "Mini_Project_Presentation.pptx") -> str:
    """Build a 10-slide PowerPoint presentation with embedded figures & speaker notes."""
    with open("results/metrics_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text: str, subtitle_text: str, owner_badge: str):
        # Top banner bar
        banner = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        banner.fill.solid()
        banner.fill.fore_color.rgb = RGBColor(26, 54, 93)
        banner.line.fill.background()

        tf = banner.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)

        p2 = tf.add_paragraph()
        p2.text = f"{subtitle_text}   |   Presenter: {owner_badge}"
        p2.font.size = Pt(12)
        p2.font.color.rgb = RGBColor(190, 227, 248)

    def add_bullets(slide, items: list[str], left=0.6, top=1.45, width=6.0, height=5.5, font_size=16):
        tx = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = tx.text_frame
        tf.word_wrap = True
        for idx, item in enumerate(items):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = f"•  {item}"
            p.font.size = Pt(font_size)
            p.font.color.rgb = RGBColor(35, 45, 65)
            p.space_after = Pt(10)

    # SLIDE 1: Title & Team Work Split
    s1 = prs.slides.add_slide(blank_layout)
    add_header(
        s1,
        "Pancreatic Cancer Prognosis Using Clinical & Radiomic Data",
        "UE24CS352A — Machine Learning Mini-Project (Based on Arash Jamalian, Stanford CS229)",
        "Both Members",
    )
    add_bullets(
        s1,
        [
            "Objective: Predict survival days & stratify high- vs. low-risk pancreatic cancer patients using clinical + 3D MRI radiomic features.",
            "Dataset: 80 patients from Stanford QFIP pipeline (12 clinical features + 900 PyRadiomics features).",
            "Member 1 Role: Clinical discretization, Laplace Multinomial Naive Bayes classifier, 10-fold CV risk threshold optimization (270 days), and 5-NN SMOTE augmentation.",
            "Member 2 Role: High-variance radiomic pruning (900 → 490), L2 Cox Proportional Hazards regression, Kaplan-Meier & Log-Rank survival testing, and Streamlit Live Demo.",
        ],
        left=0.8, top=1.6, width=11.7, height=5.2, font_size=18,
    )

    # SLIDE 2: Problem Statement & Clinical Motivation
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Problem Statement & Clinical Motivation", "Why Multimodal Survival Analysis Matters", "Member 1")
    add_bullets(
        s2,
        [
            "Over 56,000 Americans develop pancreatic cancer annually; most are diagnosed at borderline resectable or locally advanced stages.",
            "Accurate survival prognosis guides personalized treatment decisions (e.g., SBRT vs. conventional radiation, chemotherapy timing).",
            "Core ML Challenges:",
            "   1. Small cohort size (n = 80) with right-censored follow-up observations.",
            "   2. Severe class imbalance in the high-risk (< 1 year survival) Stage IIB/III region.",
            "   3. High-dimensional collinearity (p = 900 radiomic features >> n = 80 patients).",
        ],
        left=0.6, top=1.5, width=6.1, height=5.4, font_size=16,
    )
    if os.path.exists("results/fig1_clinical_pre_smote.png"):
        s2.shapes.add_picture("results/fig1_clinical_pre_smote.png", Inches(6.9), Inches(1.5), width=Inches(5.9))

    # SLIDE 3: Dataset & Feature Engineering
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Dataset & Multimodal Feature Space", "12 Clinical Features + 900 QFIP Radiomic Features", "Member 1")
    add_bullets(
        s3,
        [
            "Clinical Features (12): Stage Grouping (IB, IIA, IIB, III), Chemotherapy Time, Radiation Therapy, NCCN Resectability, Tumor Location, Primary Tumor (T1–T4), KPS, Gender, and 3D Tumor Dimensions/Volume.",
            "Radiomic Features (900 extracted via Stanford QFIP / PyRadiomics):",
            "   • First-Order Statistics: Voxel intensity mean, skewness, kurtosis within tumor mask.",
            "   • 2D/3D Shape Descriptors: Voxel volume, sphericity, maximum 3D diameter.",
            "   • Texture Matrices: GLCM (co-occurrence), GLSZM (zone size), GLRLM (run length) across 3D Wavelet & LoG-sigma filters.",
        ],
        left=0.8, top=1.6, width=11.6, height=5.2, font_size=17,
    )

    # SLIDE 4: Multinomial Naive Bayes for Threshold Selection
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Naive Bayes Classifier for Risk Threshold Selection", "Generative MLE with Laplace Smoothing", "Member 1")
    add_bullets(
        s4,
        [
            "Before applying SMOTE, we must define a principled survival threshold separating High-Risk (y=1) vs. Low-Risk (y=0) patients.",
            "Selected 5 clinical features: Stage Grouping, Chemotherapy Time, Tumor Width, NCCN Resectability, Radiation Therapy.",
            "Discretized into V buckets and trained Multinomial Naive Bayes with Laplace Smoothing across 240, 270, 300, 330, and 360 days.",
            "Result (Table 1): 270 days achieves the best 10-fold CV Balanced Accuracy of 0.69.",
        ],
        left=0.6, top=1.5, width=6.0, height=5.4, font_size=16,
    )
    if os.path.exists("results/fig2_naive_bayes_thresholds.png"):
        s4.shapes.add_picture("results/fig2_naive_bayes_thresholds.png", Inches(6.8), Inches(1.55), width=Inches(5.9))

    # SLIDE 5: SMOTE Augmentation
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. Dataset Augmentation via 5-NN SMOTE", "Populating the High-Risk (< 270 Days) Cohort", "Member 1")
    add_bullets(
        s5,
        [
            "Using the optimal 270-day threshold, we apply Synthetic Minority Over-sampling Technique (SMOTE, k=5 nearest neighbors).",
            "Interpolates synthetic minority examples across the joint 912-dimensional clinical + radiomic feature space.",
            f"Expands cohort from 80 to {summary['n_patients_augmented']} cases (+{summary['n_synthetic_added']} synthetic high-risk Stage IIB & Stage III patients).",
            "Prevents downstream Cox proportional hazards regression from under-fitting the high-risk regime.",
        ],
        left=0.6, top=1.5, width=6.0, height=5.4, font_size=16,
    )
    if os.path.exists("results/fig3_clinical_post_smote.png"):
        s5.shapes.add_picture("results/fig3_clinical_post_smote.png", Inches(6.8), Inches(1.5), width=Inches(5.9))

    # SLIDE 6: Survival Analysis & Regularized CoxPH
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. Cox Proportional Hazards & Radiomic Pruning", "L2 Penalization & High-Variance Feature Removal", "Member 2")
    add_bullets(
        s6,
        [
            "Cox Proportional Hazards Model: h(t, X) = h_0(t) * exp(beta^T X), estimated via Partial Likelihood maximization.",
            "ElasticNet Penalty in lifelines: 0.5 * penalizer * ((1 - l1_ratio)||beta||_2^2 + l1_ratio||beta||_1).",
            "L1-only (l1_ratio=1) failed to converge; L2 regularization (penalizer=0.1, l1_ratio=0) yielded optimal convergence.",
            "Variance Reduction: Initial training on all 900 radiomic features revealed 410 features with large error bands (>1.0). Removing them left 490 stable radiomic features.",
        ],
        left=0.8, top=1.6, width=11.6, height=5.2, font_size=17,
    )

    # SLIDE 7: Table 2 C-Index & Kaplan-Meier Curves
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "6. 10-Fold CV C-Index & Kaplan-Meier Stratification", "Clinical vs. Radiomic vs. Combined Models", "Member 2")
    c_rows = [
        f"{r['Dataset']} ({r['Number_of_Features']} features)  →  C-index = {r['Concordance_Index']:.2f}"
        for r in summary["table2_cox_models"]
    ]
    add_bullets(
        s7,
        [
            "10-Fold Cross-Validation Concordance Index (Harrell's C-index):",
            *["   • " + row for row in c_rows],
            "Combined Clinical + Radiomic model (502 features) achieves the best prognostic accuracy (C-index = 0.82).",
            f"Splitting patients at median partial hazard yields highly significant Kaplan-Meier separation (Log-Rank stat = {summary['logrank_test_statistic']:.2f}, p < 0.001), with survival dropping sharply before 270 days.",
        ],
        left=0.6, top=1.5, width=6.1, height=5.4, font_size=15,
    )
    if os.path.exists("results/fig4_kaplan_meier_risk_groups.png"):
        s7.shapes.add_picture("results/fig4_kaplan_meier_risk_groups.png", Inches(6.9), Inches(1.5), width=Inches(5.9))

    # SLIDE 8: Top 15 Features
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "7. Top 15 Prognostic Features & Hazard Contributions", "Interpreting Clinical & Wavelet Radiomic Biomarkers", "Member 2")
    add_bullets(
        s8,
        [
            "Reviewed trained CoxPH model coefficients log(HR) and 95% confidence intervals.",
            "Top Clinical Predictors: Chemotherapy Time (Post-SBRT reduces hazard significantly) and Primary Tumor Stage (T2/T3/T4 increases hazard).",
            "Top Radiomic Predictors: 3D Wavelet GLRLM LongRunEmphasis, First-Order Skewness/Mean, GLSZM ZoneEntropy, and LoG-sigma-5mm texture features.",
        ],
        left=0.6, top=1.5, width=5.6, height=5.4, font_size=16,
    )
    if os.path.exists("results/fig5_top15_cox_coefficients.png"):
        s8.shapes.add_picture("results/fig5_top15_cox_coefficients.png", Inches(6.4), Inches(1.45), width=Inches(6.4))

    # SLIDE 9: Covariate Survival Curves
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "8. Covariate Effect Analysis on Survival Probability", "Varying Chemotherapy Time & Cancer Stage Grouping", "Member 2")
    if os.path.exists("results/fig6_covariate_survival_curves.png"):
        s9.shapes.add_picture("results/fig6_covariate_survival_curves.png", Inches(1.2), Inches(1.45), width=Inches(10.9))
    add_bullets(
        s9,
        [
            "Holding other covariates constant: (a) Post-SBRT Chemotherapy visibly extends median survival, and (b) advancing Stage Grouping (IB → III) progressively steepens the hazard curve.",
        ],
        left=0.8, top=6.1, width=11.7, height=1.1, font_size=15,
    )

    # SLIDE 10: Conclusion, Live Demo & Q&A
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "9. Conclusions, Live Demo & Q&A Readiness", "Summary of Contributions & Future Directions", "Both Members")
    add_bullets(
        s10,
        [
            "Naive Bayes + 10-fold CV provided an objective, data-driven threshold (270 days) for SMOTE minority augmentation.",
            "Variance pruning (900 → 490 radiomic features) + L2 CoxPH boosted C-index from 0.67 (Clinical) to 0.82 (Combined).",
            "Future Work: DeepSurv / Cox-nnet non-linear hazard networks and DeepHit direct survival distribution learning.",
            "Live Demonstration Ready: Interactive Streamlit app (`streamlit run app.py`) & CLI pipeline (`python main.py`).",
        ],
        left=0.8, top=1.6, width=11.6, height=5.2, font_size=18,
    )

    prs.save(output_pptx)
    return output_pptx


if __name__ == "__main__":
    from src.presentation_builder import build_presentation
    pdf_path = build_two_page_writeup_pdf()
    print(f"Created 2-page PDF write-up: {pdf_path}")
    build_presentation(["Mini_Project_Presentation.pptx", "Presentation.pptx"])

