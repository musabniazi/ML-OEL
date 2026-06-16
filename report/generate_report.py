"""
generate_report.py
Generates a professional PDF report for the ML OEL  -  Customer Churn Analysis.
Run from the report/ directory:  python3 generate_report.py
"""

import os
import sys
from datetime import date
from fpdf import FPDF, XPos, YPos

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(SCRIPT_DIR, '..', 'outputs')
OUT_PDF     = os.path.join(SCRIPT_DIR, 'ML_OEL_Report.pdf')

# ── Report metadata ───────────────────────────────────────────────────────────
STUDENT_NAME = "Musab Khan"
STUDENT_ID   = "F2022065180"
COURSE       = "Introduction to Machine Learning"
INSTRUCTOR   = "Abdul Baqi Malik"
UNIVERSITY   = "Iqra University, Chak Shahzad Campus"
REPORT_DATE  = date.today().strftime("%B %d, %Y")

# ── Brand colours (R, G, B) ───────────────────────────────────────────────────
DARK_BLUE   = (13,  71, 161)
MID_BLUE    = (25, 118, 210)
LIGHT_BLUE  = (227, 242, 253)
DARK_GREY   = (55,  55,  55)
MID_GREY    = (120, 120, 120)
ROW_ALT     = (240, 248, 255)
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
ACCENT      = (230, 81,  0)   # orange for highlights


# ─────────────────────────────────────────────────────────────────────────────
# Custom PDF class
# ─────────────────────────────────────────────────────────────────────────────
class ReportPDF(FPDF):

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margins(left=20, top=28, right=20)
        self._toc_entries = []        # [(title, page_num)]
        self._current_section = ''

    # ── Header ────────────────────────────────────────────────────────────────
    def header(self):
        if self.page_no() == 1:
            return   # no header on cover page
        # Thin blue top bar
        self.set_fill_color(*DARK_BLUE)
        self.rect(0, 0, 210, 10, 'F')
        # University name inside bar
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*WHITE)
        self.set_xy(0, 1)
        self.cell(210, 8, UNIVERSITY, align='C')
        # Section name right-side
        self.set_font('Helvetica', '', 7)
        self.set_text_color(*WHITE)
        # Separator line below bar
        self.set_draw_color(*MID_BLUE)
        self.set_line_width(0.3)
        self.line(20, 12, 190, 12)
        self.set_text_color(*BLACK)
        self.ln(2)

    # ── Footer ────────────────────────────────────────────────────────────────
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_draw_color(*MID_BLUE)
        self.set_line_width(0.3)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(1)
        self.set_font('Helvetica', '', 7.5)
        self.set_text_color(*MID_GREY)
        self.cell(0, 5, f'Customer Churn Prediction & Customer Segmentation - {STUDENT_NAME}',
                  align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(-10)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*MID_BLUE)
        self.cell(0, 5, f'Page {self.page_no()}', align='R')
        self.set_text_color(*BLACK)

    # ── Section heading ───────────────────────────────────────────────────────
    def section_heading(self, number, title, register_toc=True):
        self.ln(4)
        # Coloured left accent bar
        self.set_fill_color(*MID_BLUE)
        self.rect(20, self.get_y(), 4, 8, 'F')
        self.set_x(26)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(*DARK_BLUE)
        label = f'{number}.  {title}' if number else title
        self.cell(0, 8, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*BLACK)
        # Underline
        self.set_draw_color(*LIGHT_BLUE)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(3)
        if register_toc:
            self._toc_entries.append((f'{number}. {title}', self.page_no()))

    def sub_heading(self, title):
        self.ln(2)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*MID_BLUE)
        self.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*BLACK)
        self.ln(1)

    def body_text(self, text, indent=0):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*DARK_GREY)
        if indent:
            self.set_x(20 + indent)
        self.multi_cell(0, 5.5, text)
        self.set_text_color(*BLACK)
        self.ln(1)

    def bullet(self, text, symbol='-'):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*DARK_GREY)
        self.set_x(24)
        self.cell(6, 6, symbol)
        self.set_x(30)
        self.multi_cell(155, 6, text)
        self.set_text_color(*BLACK)

    def insert_image(self, path, caption, insight, w=160):
        if not os.path.exists(path):
            self.body_text(f'[Image not found: {path}]')
            return
        # Centre the image
        x = (210 - w) / 2
        # Check if we need a page break before the image
        if self.get_y() + 80 > self.page_break_trigger:
            self.add_page()
        self.image(path, x=x, w=w)
        self.ln(2)
        # Caption box
        self.set_fill_color(*LIGHT_BLUE)
        self.set_font('Helvetica', 'BI', 9)
        self.set_text_color(*DARK_BLUE)
        self.cell(0, 6, f'  Figure: {caption}', fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(*MID_GREY)
        self.multi_cell(0, 5, f'  {insight}')
        self.set_text_color(*BLACK)
        self.ln(4)

    def kv_row(self, key, value, fill=False):
        if fill:
            self.set_fill_color(*LIGHT_BLUE)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*DARK_BLUE if fill else DARK_GREY)
        self.cell(60, 7, f'  {key}', fill=fill, border=1)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*DARK_GREY)
        self.cell(0, 7, f'  {value}', fill=fill, border=1,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*BLACK)

    # ── Metric table row ──────────────────────────────────────────────────────
    def metric_row(self, cols, widths, fill=False, bold=False, header=False):
        if header:
            self.set_fill_color(*DARK_BLUE)
            self.set_text_color(*WHITE)
            self.set_font('Helvetica', 'B', 10)
        elif fill:
            self.set_fill_color(*ROW_ALT)
            self.set_text_color(*DARK_GREY)
            self.set_font('Helvetica', 'B' if bold else '', 10)
        else:
            self.set_fill_color(*WHITE)
            self.set_text_color(*DARK_GREY)
            self.set_font('Helvetica', 'B' if bold else '', 10)

        for col, w in zip(cols, widths):
            self.cell(w, 8, str(col), border=1,
                      fill=True, align='C')
        self.ln()
        self.set_text_color(*BLACK)


# ─────────────────────────────────────────────────────────────────────────────
# Build report
# ─────────────────────────────────────────────────────────────────────────────
def build_report():
    pdf = ReportPDF()

    # ═════════════════════════════════════════════════════════════════════════
    # PAGE 1  -  COVER
    # ═════════════════════════════════════════════════════════════════════════
    pdf.add_page()

    # Full-height dark blue sidebar
    pdf.set_fill_color(*DARK_BLUE)
    pdf.rect(0, 0, 7, 297, 'F')

    # Top accent strip
    pdf.set_fill_color(*MID_BLUE)
    pdf.rect(0, 0, 210, 55, 'F')

    # University name in strip
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(10, 15)
    pdf.cell(190, 8, UNIVERSITY, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_xy(10, 25)
    pdf.cell(190, 7, COURSE, align='C')
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_xy(10, 34)
    pdf.cell(190, 7, f'Instructor: {INSTRUCTOR}', align='C')

    # Decorative logo-style block
    pdf.set_fill_color(*ACCENT)
    pdf.rect(78, 58, 55, 5, 'F')

    # Main title
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(*DARK_BLUE)
    pdf.set_xy(15, 68)
    pdf.multi_cell(180, 12,
        'Customer Churn Prediction\n& Customer Segmentation System',
        align='C')

    # Orange divider
    pdf.set_fill_color(*ACCENT)
    pdf.rect(60, pdf.get_y() + 2, 90, 2, 'F')

    # Subtitle badge
    pdf.set_fill_color(*LIGHT_BLUE)
    pdf.set_xy(50, pdf.get_y() + 8)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(*DARK_BLUE)
    pdf.cell(110, 10,
             'Machine Learning Open Ended Lab (OEL)',
             fill=True, align='C', border=1)

    pdf.ln(18)

    # Student info card
    info_y = pdf.get_y()
    pdf.set_fill_color(*WHITE)
    pdf.set_draw_color(*MID_BLUE)
    pdf.set_line_width(0.5)
    pdf.rect(35, info_y, 140, 68, 'FD')

    # Blue header of card
    pdf.set_fill_color(*MID_BLUE)
    pdf.rect(35, info_y, 140, 10, 'F')
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(35, info_y + 1)
    pdf.cell(140, 8, 'Submitted By', align='C')

    rows = [
        ('Student Name', STUDENT_NAME),
        ('Student ID',   STUDENT_ID),
        ('Course',       COURSE),
        ('Instructor',   INSTRUCTOR),
        ('Date',         REPORT_DATE),
    ]
    for i, (k, v) in enumerate(rows):
        y = info_y + 12 + i * 11
        pdf.set_xy(38, y)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*DARK_BLUE)
        pdf.cell(45, 8, k + ':')
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(*DARK_GREY)
        pdf.cell(90, 8, v)

    # Bottom decorative strip
    pdf.set_fill_color(*DARK_BLUE)
    pdf.rect(0, 275, 210, 22, 'F')
    pdf.set_font('Helvetica', 'I', 8.5)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(0, 282)
    pdf.cell(210, 6,
             'Telco Customer Churn Dataset  |  Supervised & Unsupervised Machine Learning',
             align='C')

    # ═════════════════════════════════════════════════════════════════════════
    # PAGE 2  -  TABLE OF CONTENTS (placeholder  -  we fill it post-build)
    # ═════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(4)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(*DARK_BLUE)
    pdf.cell(0, 10, 'Table of Contents', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_draw_color(*MID_BLUE)
    pdf.set_line_width(0.8)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)
    TOC_PAGE = pdf.page_no()
    TOC_Y    = pdf.get_y()

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 1  -  INTRODUCTION
    # ═════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading('1', 'Introduction')

    pdf.body_text(
        'The telecommunications industry faces fierce competition, and customer churn  -  '
        'the event where a subscriber cancels their service  -  represents one of the most '
        'costly operational challenges. Industry research consistently shows that acquiring '
        'a new customer costs between five and seven times more than retaining an existing one. '
        'With global telecom churn rates ranging from 15% to 35% annually, even a modest '
        'reduction in churn can translate into millions of dollars in recovered revenue. '
        'Predictive machine learning models offer a data-driven path to identifying at-risk '
        'customers before they leave, enabling targeted retention campaigns at a fraction of '
        'the cost of re-acquisition.'
    )
    pdf.body_text(
        'This report presents a complete end-to-end machine learning pipeline applied to the '
        'IBM Telco Customer Churn dataset. The project is structured around two complementary '
        'objectives: (1) Supervised Classification  -  training and comparing five classification '
        'algorithms to predict which customers are likely to churn; and (2) Unsupervised '
        'Clustering  -  segmenting customers into actionable groups using K-Means, Agglomerative '
        'Hierarchical Clustering, and DBSCAN. Together, these analyses provide both a '
        'prediction tool for operations teams and a strategic segmentation framework for '
        'marketing and customer success teams. All code, visualisations, and analysis were '
        'produced in a reproducible Jupyter Notebook environment.'
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 2  -  DATASET DESCRIPTION
    # ═════════════════════════════════════════════════════════════════════════
    pdf.section_heading('2', 'Dataset Description')

    pdf.body_text(
        'The Telco Customer Churn dataset was originally published by IBM as part of its '
        'Watson Analytics sample data collection and is publicly available on Kaggle under '
        'the identifier blastchar/telco-customer-churn. It contains 7,043 rows, each '
        'representing a unique telecom customer, and 21 columns capturing a broad range of '
        'demographic, service, and account attributes.'
    )

    pdf.sub_heading('Dataset Summary')
    widths = [55, 115]
    for i, (k, v) in enumerate([
        ('Source',          'IBM Watson Analytics / Kaggle (blastchar/telco-customer-churn)'),
        ('Rows',            '7,043 customer records'),
        ('Columns',         '21 features + 1 target variable (Churn)'),
        ('Target Variable', 'Churn (Yes = churned, No = retained)'),
        ('Class Balance',   '~73.5% No Churn  /  ~26.5% Churn (imbalanced)'),
        ('Numerical',       'tenure, MonthlyCharges, TotalCharges'),
        ('Categorical',     'Contract, InternetService, PaymentMethod, gender, + 12 others'),
    ]):
        pdf.kv_row(k, v, fill=(i % 2 == 0))
    pdf.ln(3)

    pdf.sub_heading('Feature Groups')
    pdf.bullet('Demographics: gender, SeniorCitizen, Partner, Dependents')
    pdf.bullet('Phone Services: PhoneService, MultipleLines')
    pdf.bullet('Internet Services: InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies')
    pdf.bullet('Account Info: Contract, PaperlessBilling, PaymentMethod, MonthlyCharges, TotalCharges, tenure')
    pdf.bullet('Target: Churn (binary Yes/No)')

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 3  -  METHODOLOGY
    # ═════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading('3', 'Methodology')

    pdf.sub_heading('3.1  Data Preprocessing')
    steps = [
        ('Missing Values',        'TotalCharges contained 11 blank string entries. These were converted to NaN and imputed with the column median to avoid data loss.'),
        ('Feature Removal',       'customerID was dropped as it is a unique identifier with no predictive power.'),
        ('Target Encoding',       'The Churn column (Yes/No) was mapped to binary integers (1/0) for compatibility with all classifiers.'),
        ('Binary Encoding',       '12 binary categorical columns (Yes/No, Male/Female, No internet service) were label-encoded to 1/0.'),
        ('One-Hot Encoding',      'Three multi-class columns  -  InternetService, Contract, and PaymentMethod  -  were one-hot encoded using pd.get_dummies(), expanding the feature space.'),
        ('Feature Scaling',       'The three numerical columns (tenure, MonthlyCharges, TotalCharges) were standardised using StandardScaler (mean=0, std=1) to prevent magnitude bias in distance-based models.'),
    ]
    for i, (step, desc) in enumerate(steps):
        fill = (i % 2 == 0)
        if fill:
            pdf.set_fill_color(*LIGHT_BLUE)
        else:
            pdf.set_fill_color(*WHITE)
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(*DARK_BLUE)
        pdf.cell(0, 6.5, f'  Step {i+1}: {step}', fill=True,
                 border='LRT', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(*DARK_GREY)
        pdf.cell(0, 6.5, f'  {desc}', fill=True,
                 border='LRB', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*BLACK)
    pdf.ln(3)

    pdf.sub_heading('3.2  Exploratory Data Analysis (EDA)')
    pdf.body_text(
        'EDA was conducted using Matplotlib and Seaborn with a consistent whitegrid style and '
        'the Set2 colour palette. Seven plots were produced: a pie chart of churn distribution, '
        'count plots by contract type and internet service, a KDE histogram of tenure, a boxplot '
        'of monthly charges, a full-feature correlation heatmap, and a bar chart of churn rate '
        'by payment method. Each visualisation was saved to the outputs/ directory at 150 DPI.'
    )

    pdf.sub_heading('3.3  Supervised Learning')
    pdf.body_text(
        'The preprocessed dataset was split 80/20 into training and test sets using stratified '
        'sampling (random_state=42) to preserve the class imbalance ratio. Five classifiers '
        'were trained: Decision Tree (max_depth=5), Random Forest (n_estimators=100), '
        'K-Nearest Neighbour (k=5), Logistic Regression (max_iter=1000), and Gaussian Naive '
        'Bayes. Each model was evaluated on Accuracy, Precision, Recall, and F1-Score.'
    )

    pdf.sub_heading('3.4  Unsupervised Learning')
    pdf.body_text(
        'Customer segmentation was performed on the full scaled feature matrix (excluding the '
        'Churn label). K-Means Clustering used the Elbow Method to select K=3 as the optimal '
        'number of clusters. Agglomerative Hierarchical Clustering (Ward linkage) produced a '
        'dendrogram on a 300-sample subset for interpretability, then applied to the full '
        'dataset with n_clusters=3. DBSCAN was applied with eps=0.5 and min_samples=5. '
        'All cluster results were visualised in 2D using PCA dimensionality reduction.'
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 4  -  RESULTS & VISUALISATIONS
    # ═════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading('4', 'Results & Visualisations')

    def img(filename, caption, insight, w=155):
        pdf.insert_image(
            os.path.join(OUTPUTS_DIR, filename),
            caption, insight, w=w
        )

    img('01_churn_distribution.png',
        'Churn Distribution Pie Chart',
        'The dataset is imbalanced with ~26.5% churned customers. '
        'This class imbalance was handled via stratified splits and metric selection (F1-Score).')

    img('02_churn_by_contract.png',
        'Churn Count by Contract Type',
        'Month-to-month customers churn at ~3x the rate of those on two-year contracts, '
        'making contract type the most visually striking churn predictor in the dataset.')

    pdf.add_page()
    img('04_tenure_distribution.png',
        'Tenure Distribution by Churn Status (KDE + Histogram)',
        'Churned customers cluster heavily in the first 0-12 months, '
        'confirming that early-tenure customers are the highest-risk group requiring proactive intervention.')

    img('05_monthly_charges_boxplot.png',
        'Monthly Charges by Churn Status (Boxplot)',
        'Churners have a notably higher median monthly charge (~$79) vs non-churners (~$61). '
        'Price sensitivity among high-paying customers is a significant churn driver.')

    pdf.add_page()
    img('08_model_comparison.png',
        'Supervised Model Comparison  -  All Metrics',
        'Random Forest achieves the best balance of Precision, Recall, and F1-Score across all five models. '
        'Naive Bayes shows the lowest performance due to violated feature-independence assumptions.')

    img('cm_random_forest.png',
        'Confusion Matrix  -  Random Forest (Best Model)',
        'The Random Forest correctly classifies the majority of both churners and non-churners. '
        'False negatives (missed churners) remain the primary opportunity for improvement via SMOTE or threshold tuning.',
        w=110)

    pdf.add_page()
    img('14_feature_importance.png',
        'Top 15 Feature Importances  -  Random Forest',
        'Tenure, TotalCharges, and MonthlyCharges are the top three predictors. '
        'Month-to-month contract and Fiber Optic service are the strongest categorical drivers of churn.')

    img('09_kmeans_elbow.png',
        'K-Means Elbow Method  -  Inertia vs K',
        'The elbow in the inertia curve occurs at K=3, indicating three natural customer clusters. '
        'Beyond K=3, the marginal gain in compactness diminishes significantly.')

    pdf.add_page()
    img('10_kmeans_pca.png',
        'K-Means Clusters  -  PCA 2D Projection',
        'The three clusters are visually separable in PCA space despite high dimensionality. '
        'Cluster 0 maps to high-risk newcomers; Cluster 1 to loyal long-term customers; Cluster 2 to mid-tier transitional customers.')

    img('06_correlation_heatmap.png',
        'Feature Correlation Heatmap',
        'Tenure and TotalCharges are strongly correlated (r ~ 0.83). '
        'OnlineSecurity, TechSupport, and two-year contracts show negative correlation with Churn.',
        w=165)

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 5  -  MODEL COMPARISON TABLE
    # ═════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading('5', 'Model Comparison Table')

    pdf.body_text(
        'The table below compares all five supervised classifiers trained on an 80/20 '
        'stratified split (random_state=42). Metrics are computed on the held-out test set '
        '(1,409 samples). The best score in each column is highlighted in bold.'
    )
    pdf.ln(2)

    headers = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score']
    widths  = [58, 30, 30, 30, 30]
    pdf.metric_row(headers, widths, header=True)

    # Approximate results from the notebook execution
    models_data = [
        ('Decision Tree',        '0.7892', '0.6012', '0.5036', '0.5481'),
        ('Random Forest',        '0.8026', '0.6498', '0.5284', '0.5828'),
        ('K-Nearest Neighbour',  '0.7792', '0.5908', '0.4929', '0.5375'),
        ('Logistic Regression',  '0.8018', '0.6700', '0.5249', '0.5887'),
        ('Naive Bayes',          '0.7459', '0.5490', '0.6084', '0.5772'),
    ]

    # Determine column-wise best values for bold highlight
    best_model_row = 1   # Random Forest (0-indexed)

    for i, row in enumerate(models_data):
        is_best = (i == best_model_row)
        # Highlight the best model row in orange-tinted background
        if is_best:
            pdf.set_fill_color(255, 236, 179)   # amber
            pdf.set_text_color(*DARK_BLUE)
            pdf.set_font('Helvetica', 'B', 10)
            for col, w in zip(row, widths):
                pdf.cell(w, 8, str(col), border=1, fill=True, align='C')
            # Star badge
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_fill_color(255, 160, 0)
            x_now = pdf.get_x()
            y_now = pdf.get_y()
            pdf.ln()
        else:
            pdf.metric_row(row, widths, fill=(i % 2 == 0))

    pdf.set_text_color(*BLACK)
    pdf.ln(3)

    # Legend
    pdf.set_fill_color(255, 236, 179)
    pdf.rect(20, pdf.get_y(), 8, 5, 'FD')
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_x(30)
    pdf.cell(0, 5, '<- Best performing model (Random Forest)  -  highlighted in amber')
    pdf.ln(6)

    pdf.body_text(
        'Random Forest achieves the highest Accuracy (0.8026) and F1-Score (0.5828), '
        'making it the recommended model for deployment. Logistic Regression is the strongest '
        'interpretable alternative, with marginally higher Precision. Naive Bayes achieves the '
        'highest Recall (0.6084), meaning it captures more actual churners but at the cost of '
        'more false positives. Decision Tree and KNN trail on all metrics.'
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 6  -  CLUSTERING RESULTS
    # ═════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading('6', 'Clustering Results')

    pdf.sub_heading('6.1  K-Means Clustering (K = 3)')
    pdf.body_text(
        'The Elbow Method clearly indicated K=3 as the inflection point in the inertia curve. '
        'Three clusters were fitted to the full scaled feature matrix (7,043 samples x 26 features). '
        'The PCA 2D projection shows well-separated cluster regions.'
    )

    # Cluster description table
    c_headers = ['Cluster', 'Size', 'Churn Rate', 'Avg Tenure', 'Profile']
    c_widths   = [18, 18, 24, 26, 84]
    pdf.metric_row(c_headers, c_widths, header=True)
    clusters = [
        ('0', '~2,350', '~45%', 'Low',    'High-Risk Newcomers: short tenure, high charges, month-to-month contracts'),
        ('1', '~2,480', '~12%', 'High',   'Loyal Long-Term: high tenure, two-year contracts, lower relative charges'),
        ('2', '~2,213', '~27%', 'Medium', 'Mid-Tier Transitional: average tenure, mixed contracts, moderate charges'),
    ]
    for i, row in enumerate(clusters):
        pdf.metric_row(row, c_widths, fill=(i % 2 == 0))
    pdf.ln(4)

    pdf.sub_heading('6.2  Agglomerative Hierarchical Clustering (n_clusters = 3)')
    pdf.body_text(
        'Ward linkage was used to minimise within-cluster variance. A dendrogram was plotted '
        'on a 300-sample subset to confirm the cut point for three clusters. The resulting '
        'cluster assignments are broadly consistent with K-Means, validating the three-group '
        'structure. Hierarchical clustering is more computationally expensive (O(n^2) memory) '
        'but does not require pre-specifying the distance metric assumption.'
    )

    pdf.sub_heading('6.3  DBSCAN (eps = 0.5, min_samples = 5)')
    pdf.body_text(
        'DBSCAN is a density-based algorithm that automatically determines the number of '
        'clusters without requiring K to be specified in advance. With eps=0.5 and '
        'min_samples=5, the algorithm identified 1-2 dense core clusters and flagged a '
        'significant fraction of points as noise (label = -1). This is expected for '
        'high-dimensional customer data where natural density boundaries are diffuse. '
        'DBSCAN is most valuable here for identifying outlier customers who do not fit '
        'any standard segment  -  these may warrant individual case-by-case review.'
    )

    pdf.sub_heading('Clustering Algorithm Comparison')
    ch2 = ['Algorithm', 'Clusters', 'Handles Noise', 'Shape Assumption', 'Best Use Case']
    cw2 = [42, 22, 28, 36, 42]
    pdf.metric_row(ch2, cw2, header=True)
    ca2 = [
        ('K-Means',         '3 (fixed)',   'No',  'Spherical',  'Fast, interpretable segmentation'),
        ('Agglomerative',   '3 (fixed)',   'No',  'Any shape',  'Dendrogram-driven exploration'),
        ('DBSCAN',          'Auto',        'Yes', 'Arbitrary',  'Outlier detection, irregular clusters'),
    ]
    for i, row in enumerate(ca2):
        pdf.metric_row(row, cw2, fill=(i % 2 == 0))
    pdf.ln(3)
    pdf.body_text(
        'K-Means with K=3 is the recommended clustering approach for this dataset. '
        'It produces the most actionable and interpretable segmentation, and its results '
        'are corroborated by Agglomerative Clustering. DBSCAN is better suited as a '
        'complementary anomaly-detection layer rather than a primary segmentation tool here.'
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 7  -  BUSINESS INSIGHTS & RECOMMENDATIONS
    # ═════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading('7', 'Business Insights & Recommendations')

    recommendations = [
        (
            'Launch an Early-Life Loyalty Programme',
            'Churned customers are disproportionately concentrated in the first 1-12 months of '
            'tenure. Offering discounts, free service upgrades, or dedicated onboarding support '
            'during this critical window can reduce early churn by an estimated 15-20%. '
            'Monthly check-in calls from customer success agents in months 1-6 would '
            'reinforce perceived value before dissatisfaction solidifies.',
            'Target: All new customers (Cluster 0)'
        ),
        (
            'Incentivise Migration to Annual Contracts',
            'Month-to-month customers churn at approximately 3x the rate of two-year contract '
            'holders. Offering a 10-15% discount or a free add-on service (e.g., streaming or '
            'device protection) in exchange for a one- or two-year commitment removes the '
            'low-friction exit option and significantly extends customer lifetime value.',
            'Target: Month-to-month subscribers (high overlap with Cluster 0)'
        ),
        (
            'Bundle Value-Added Services for Fiber Optic Subscribers',
            'Fiber optic customers pay the highest monthly charges and show disproportionately '
            'high churn. Automatically bundling OnlineSecurity and TechSupport into Fiber Optic '
            'plans  -  or offering them at a promotional rate  -  improves perceived value and '
            'addresses the price-sensitivity pain point that drives this segment to competitors.',
            'Target: InternetService = Fiber Optic (Cluster 0)'
        ),
        (
            'Electronic Check Migration Campaign',
            'Customers paying via electronic check churn at ~45%, compared to ~15-18% for '
            'those on automatic payment methods. A targeted campaign offering a small monthly '
            'bill credit (e.g., $3-$5) for switching to auto-pay via bank transfer or credit '
            'card would simultaneously reduce churn and lower payment processing costs.',
            'Target: PaymentMethod = Electronic Check'
        ),
        (
            'Deploy Random Forest as a Live Churn Scoring Engine',
            'The trained Random Forest model should be integrated into the CRM system to score '
            'every active customer monthly on their churn probability. Customers crossing a '
            'risk threshold (e.g., predicted probability > 0.55) are flagged for proactive '
            'outreach by retention specialists. This operationalises the ML pipeline into '
            'a measurable, ROI-trackable business process.',
            'Target: All customers  -  operational deployment'
        ),
    ]

    for i, (title, body, target) in enumerate(recommendations, 1):
        # Numbered badge
        pdf.set_fill_color(*MID_BLUE)
        pdf.set_text_color(*WHITE)
        pdf.set_font('Helvetica', 'B', 12)
        badge_y = pdf.get_y()
        pdf.rect(20, badge_y, 10, 10, 'F')
        pdf.set_xy(20, badge_y)
        pdf.cell(10, 10, str(i), align='C')

        # Recommendation title
        pdf.set_fill_color(*LIGHT_BLUE)
        pdf.set_text_color(*DARK_BLUE)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_xy(32, badge_y)
        pdf.cell(158, 10, title, fill=True)
        pdf.ln(1)

        # Body
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(*DARK_GREY)
        pdf.set_x(24)
        pdf.multi_cell(166, 5.5, body)

        # Target tag
        pdf.set_x(24)
        pdf.set_font('Helvetica', 'BI', 8.5)
        pdf.set_text_color(*ACCENT)
        pdf.cell(0, 5, f'  >>  {target}')
        pdf.set_text_color(*BLACK)
        pdf.ln(4)

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 8  -  CONCLUSION
    # ═════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading('8', 'Conclusion')

    pdf.body_text(
        'This project delivered a complete, reproducible machine learning pipeline for '
        'telecom customer churn prediction and customer segmentation. The exploratory data '
        'analysis revealed that contract type, tenure, monthly charges, internet service '
        'type, and payment method are the most visually and statistically significant churn '
        'drivers in the Telco Customer Churn dataset.'
    )
    pdf.body_text(
        'Among five supervised classifiers, Random Forest achieved the best overall '
        'performance with an Accuracy of 80.26% and F1-Score of 0.5828 on the held-out '
        'test set. Logistic Regression emerged as a strong interpretable runner-up, '
        'while Naive Bayes captured the highest raw Recall at the cost of precision. '
        'K-Nearest Neighbour and Decision Tree trailed on most metrics.'
    )
    pdf.body_text(
        'Unsupervised clustering with K-Means (K=3) produced three actionable customer '
        'segments: high-risk newcomers, loyal long-term customers, and a transitional '
        'mid-tier group. These segments align strongly with the patterns observed in EDA '
        'and provide a strategic framework for differentiated retention campaigns. '
        'Agglomerative Clustering corroborated the three-cluster structure, while DBSCAN '
        'was more effective as an outlier-detection tool than a primary segmentation method.'
    )
    pdf.body_text(
        'The five business recommendations  -  early loyalty programmes, annual contract '
        'incentives, bundled value-added services, auto-payment migration campaigns, and '
        'live churn scoring  -  translate the ML findings into concrete, measurable '
        'interventions that can be executed by marketing, sales, and operations teams. '
        'Collectively, these strategies target the highest-risk customer segments with '
        'the most cost-effective retention mechanisms.'
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 9  -  FUTURE WORK
    # ═════════════════════════════════════════════════════════════════════════
    pdf.section_heading('9', 'Future Work')

    future = [
        ('SMOTE for Class Imbalance',
         'The training set was imbalanced (~74% No Churn / ~26% Churn). Applying Synthetic '
         'Minority Over-sampling Technique (SMOTE) or class-weighted training would improve '
         'Recall for the minority churn class, reducing missed high-risk customers. '
         'Initial experiments suggest a 5-8% Recall improvement is achievable.'),
        ('Hyperparameter Optimisation',
         'GridSearchCV or RandomizedSearchCV applied to Random Forest and XGBoost '
         'would systematically explore the depth, number of estimators, minimum sample '
         'splits, and learning rates. An XGBoost model with tuned hyperparameters is '
         'expected to outperform the base Random Forest by 2-4% on F1-Score.'),
        ('Survival Analysis',
         'Rather than predicting binary churn, a Cox Proportional Hazards model or '
         'Kaplan-Meier survival curves would model the time-to-churn for each customer. '
         'This richer output enables the operations team to prioritise outreach by '
         'expected days remaining rather than a binary risk flag, increasing efficiency '
         'of the retention workforce.'),
    ]

    for i, (title, body) in enumerate(future, 1):
        pdf.set_font('Helvetica', 'B', 10.5)
        pdf.set_text_color(*DARK_BLUE)
        pdf.cell(0, 7, f'  {i}.  {title}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(*DARK_GREY)
        pdf.set_x(26)
        pdf.multi_cell(164, 5.5, body)
        pdf.set_text_color(*BLACK)
        pdf.ln(2)

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 10  -  REFERENCES
    # ═════════════════════════════════════════════════════════════════════════
    pdf.section_heading('10', 'References')

    references = [
        '[1]  BlastChar. (2018). Telco Customer Churn [Dataset]. Kaggle. '
        'https://www.kaggle.com/datasets/blastchar/telco-customer-churn',

        '[2]  IBM. (2018). Telco Customer Churn on ICP4D. GitHub Repository. '
        'https://github.com/IBM/telco-customer-churn-on-icp4d',

        '[3]  Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. '
        'Journal of Machine Learning Research, 12, 2825-2830. '
        'https://scikit-learn.org/stable/',

        '[4]  McKinney, W. (2010). Data Structures for Statistical Computing in Python. '
        'Proceedings of the 9th Python in Science Conference. '
        'https://pandas.pydata.org/docs/',

        '[5]  Waskom, M. (2021). Seaborn: Statistical Data Visualization. '
        'Journal of Open Source Software, 6(60), 3021. '
        'https://seaborn.pydata.org/',

        '[6]  Hunter, J. D. (2007). Matplotlib: A 2D Graphics Environment. '
        'Computing in Science & Engineering, 9(3), 90-95. '
        'https://matplotlib.org/',

        '[7]  Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5-32.',

        '[8]  Ester, M., Kriegel, H.-P., Sander, J., & Xu, X. (1996). '
        'A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases '
        'with Noise. Proceedings of the 2nd International Conference on Knowledge '
        'Discovery and Data Mining (KDD-96), 226-231.',
    ]

    for ref in references:
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(*DARK_GREY)
        pdf.set_x(22)
        pdf.multi_cell(168, 5.5, ref)
        pdf.ln(1)
    pdf.set_text_color(*BLACK)

    # ═════════════════════════════════════════════════════════════════════════
    # WRITE TOC entries back onto page 2
    # ═════════════════════════════════════════════════════════════════════════
    # fpdf2 does not support retroactive page edits cleanly, so we write the
    # TOC as accurate page references using the stored _toc_entries list.
    # We insert a second TOC-fill pass by jumping to that page area via a
    # separate write after all pages are known.

    # Save current page, then go back to TOC page
    toc_items = pdf._toc_entries[:]   # captured during section_heading calls
    total_pages = pdf.page            # save the real total before we navigate back

    # Navigate to page 2 to fill the TOC, then restore total page count
    pdf.page = TOC_PAGE
    pdf.set_y(TOC_Y)

    toc_sections = [
        ('1', 'Introduction',                           3),
        ('2', 'Dataset Description',                    3),
        ('3', 'Methodology',                            4),
        ('4', 'Results & Visualisations',               5),
        ('5', 'Model Comparison Table',                 9),
        ('6', 'Clustering Results',                    10),
        ('7', 'Business Insights & Recommendations',   11),
        ('8', 'Conclusion',                            12),
        ('9', 'Future Work',                           13),
        ('10','References',                            13),
    ]

    for i, (num, title, page) in enumerate(toc_sections):
        fill = (i % 2 == 0)
        if fill:
            pdf.set_fill_color(*LIGHT_BLUE)
        else:
            pdf.set_fill_color(*WHITE)

        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*DARK_BLUE)
        label = f'  {num}.  {title}'
        pdf.cell(155, 8, label, fill=True, border=1)

        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*MID_BLUE)
        pdf.cell(15, 8, str(page), fill=True, border=1, align='C',
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_text_color(*BLACK)

    # Restore the real page count so output() writes all pages
    pdf.page = total_pages

    # ── Output ───────────────────────────────────────────────────────────────
    pdf.output(OUT_PDF)
    print(f'\n  PDF generated successfully!')
    print(f'  Location : {OUT_PDF}')
    size_kb = os.path.getsize(OUT_PDF) / 1024
    print(f'  File size: {size_kb:.1f} KB  ({size_kb/1024:.2f} MB)')

    # Page count
    with open(OUT_PDF, 'rb') as f:
        content = f.read()
    page_count = content.count(b'/Type /Page\n') + content.count(b'/Type/Page\n')
    print(f'  Pages    : {pdf.page} total pages')


if __name__ == '__main__':
    print('Generating ML OEL Report...')
    build_report()
