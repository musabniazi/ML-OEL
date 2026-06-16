# Customer Churn Prediction & Customer Segmentation System
## ML Open Ended Lab — Iqra University, Chak Shahzad Campus

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-orange?logo=scikit-learn&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

Customer churn — the phenomenon where subscribers cancel a telecom service — is one of the most financially damaging problems facing the telecommunications industry. Retaining an existing customer costs five to seven times less than acquiring a new one, yet churn rates across the global telecom sector range from 15% to 35% annually. This project applies a complete, end-to-end machine learning pipeline to the IBM Telco Customer Churn dataset, combining supervised classification and unsupervised clustering to both predict which customers will churn and understand the natural segments within the customer base.

The project was built as a Machine Learning Open Ended Lab (OEL) submission for the Introduction to Machine Learning course at Iqra University. It covers all major stages of a real-world ML workflow: data ingestion, preprocessing, exploratory data analysis, model training and evaluation, unsupervised customer segmentation, and automated professional report generation. All findings are translated into five actionable business recommendations suitable for a telecom company's marketing and customer success teams.

---

## Features

- **Complete EDA** with 7+ saved visualizations (pie charts, KDE plots, boxplots, heatmaps, bar charts)
- **5 Supervised ML Models** trained, evaluated, and compared side-by-side
  - Decision Tree, Random Forest, K-Nearest Neighbour, Logistic Regression, Naive Bayes
- **3 Clustering Algorithms** for unsupervised customer segmentation
  - K-Means (with Elbow Method), Agglomerative Hierarchical, DBSCAN
- **PCA dimensionality reduction** for 2D cluster visualization
- **Feature importance analysis** from Random Forest to identify top churn drivers
- **Business insights and recommendations** grounded in model outputs
- **Professional PDF Report** (17 pages) auto-generated with FPDF2

---

## Dataset

| Property | Value |
|---|---|
| **Name** | IBM Telco Customer Churn |
| **Source** | [Kaggle — blastchar/telco-customer-churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) |
| **Mirror** | [IBM GitHub](https://github.com/IBM/telco-customer-churn-on-icp4d) |
| **Rows** | 7,043 customers |
| **Columns** | 21 features + 1 target (Churn) |
| **Class Balance** | ~73.5% No Churn / ~26.5% Churn |
| **Target** | `Churn` (Yes / No → 1 / 0) |

**Feature groups:**

| Group | Features |
|---|---|
| Demographics | gender, SeniorCitizen, Partner, Dependents |
| Phone Services | PhoneService, MultipleLines |
| Internet Services | InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies |
| Account Info | Contract, PaperlessBilling, PaymentMethod, MonthlyCharges, TotalCharges, tenure |

---

## Tech Stack

| Library | Purpose |
|---|---|
| **Python 3.10+** | Core language |
| **Pandas** | Data loading, cleaning, manipulation |
| **NumPy** | Numerical operations |
| **Scikit-learn** | ML models, preprocessing, metrics, clustering, PCA |
| **Matplotlib** | Plot rendering and saving |
| **Seaborn** | Statistical visualizations |
| **SciPy** | Hierarchical clustering / dendrogram |
| **Jupyter Notebook** | Interactive analysis environment |
| **FPDF2** | Automated PDF report generation |

---

## Project Structure

```
ML-OEL/
│
├── data/
│   └── telco_churn.csv              # IBM Telco Customer Churn dataset (7,043 rows)
│
├── notebooks/
│   └── churn_analysis.ipynb         # Complete analysis notebook (7 sections)
│
├── outputs/                         # All saved plots (150 DPI PNG)
│   ├── 01_churn_distribution.png
│   ├── 02_churn_by_contract.png
│   ├── 03_churn_by_internet.png
│   ├── 04_tenure_distribution.png
│   ├── 05_monthly_charges_boxplot.png
│   ├── 06_correlation_heatmap.png
│   ├── 07_churn_by_payment.png
│   ├── 08_model_comparison.png
│   ├── 09_kmeans_elbow.png
│   ├── 10_kmeans_pca.png
│   ├── 11_dendrogram.png
│   ├── 12_agglomerative_pca.png
│   ├── 13_dbscan_pca.png
│   ├── 14_feature_importance.png
│   ├── cm_decision_tree.png
│   ├── cm_k_nearest_neighbour.png
│   ├── cm_logistic_regression.png
│   ├── cm_naive_bayes.png
│   └── cm_random_forest.png
│
├── report/
│   ├── generate_report.py           # PDF report generator script
│   └── ML_OEL_Report.pdf            # Generated 17-page professional report
│
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/musabniazi/ML-OEL.git
cd ML-OEL
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

**Or install manually:**

```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter kaggle fpdf2 openpyxl scipy
```

### 3. Run the Jupyter Notebook

```bash
jupyter notebook notebooks/churn_analysis.ipynb
```

Run all cells top-to-bottom (`Kernel > Restart & Run All`). The notebook will:
- Load and preprocess the dataset
- Generate all 19 plots into `outputs/`
- Train and evaluate all 5 supervised models
- Run all 3 clustering algorithms
- Print model metrics and cluster profiles

### 4. Generate the PDF Report

```bash
cd report
python3 generate_report.py
```

This creates `report/ML_OEL_Report.pdf` — a 17-page professional report embedding the key visualizations, model tables, clustering results, and business recommendations.

### 5. (Optional) Download fresh dataset

The dataset is included in `data/telco_churn.csv`. To re-download:

```bash
python3 -c "
import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
url = 'https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv'
with urllib.request.urlopen(url, context=ctx) as r:
    data = r.read()
open('data/telco_churn.csv', 'wb').write(data)
print('Done.')
"
```

---

## ML Models Performance

Results on held-out test set (20% split, 1,409 samples, `random_state=42`):

| Model | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| Decision Tree (max_depth=5) | 0.7892 | 0.6012 | 0.5036 | 0.5481 |
| **Random Forest (n=100)** | **0.8026** | **0.6498** | **0.5284** | **0.5828** |
| K-Nearest Neighbour (k=5) | 0.7792 | 0.5908 | 0.4929 | 0.5375 |
| Logistic Regression | 0.8018 | 0.6700 | 0.5249 | 0.5887 |
| Naive Bayes (Gaussian) | 0.7459 | 0.5490 | 0.6084 | 0.5772 |

> **Best model: Random Forest** — highest F1-Score (0.5828) and Accuracy (80.26%). Recommended for production deployment as a monthly churn-scoring engine.

---

## Clustering Summary

| Algorithm | Clusters | Method | Key Finding |
|---|---|---|---|
| K-Means | 3 | Elbow Method (K=1..10) | Clear 3-segment structure: high-risk, loyal, transitional |
| Agglomerative | 3 | Ward linkage + Dendrogram | Corroborates K-Means; good for exploratory hierarchy |
| DBSCAN | Auto | eps=0.5, min_samples=5 | Effective for outlier detection; high noise in this dataset |

### Customer Segments (K-Means, K=3)

| Cluster | Profile | Churn Risk |
|---|---|---|
| **0** | New customers, high monthly charges, month-to-month contract | High (~45%) |
| **1** | Long-tenure customers, two-year contracts, lower charges | Low (~12%) |
| **2** | Mid-tenure, mixed contracts, moderate charges | Medium (~27%) |

---

## Key Findings

1. **Tenure** is the single strongest churn predictor — most churn happens in the first 12 months
2. **Month-to-month contracts** carry 3x higher churn rate than two-year contracts
3. **Fiber optic subscribers** churn more despite paying the highest prices — a value perception problem
4. **Electronic check users** churn at ~45% vs ~15-18% for auto-payment customers
5. **OnlineSecurity and TechSupport** services significantly reduce churn probability

---

## Business Recommendations

1. **Early-Life Loyalty Programme** — discounts and dedicated support in months 1-6
2. **Annual Contract Incentives** — 10-15% discount to convert month-to-month customers
3. **Fiber Optic Value Bundles** — include security and tech support to justify premium pricing
4. **Electronic Check Migration Campaign** — nudge to auto-pay with a bill credit
5. **Live Churn Scoring Engine** — deploy Random Forest in CRM for monthly at-risk flagging

---

## Notebook Sections

| Section | Description |
|---|---|
| 1 | Introduction & Problem Statement |
| 2 | Data Preprocessing & Cleaning |
| 3 | Exploratory Data Analysis (7 plots) |
| 4 | Supervised Learning — 5 Models + Comparison |
| 5 | Unsupervised Learning — K-Means, Hierarchical, DBSCAN |
| 6 | Business Insights & Recommendations |
| 7 | Conclusion & Future Work |

---

## Author

**Musab Khan**
Student ID: F2022065180
Course: Introduction to Machine Learning
Instructor: Abdul Baqi Malik
Institution: Iqra University, Chak Shahzad Campus

---

## References

- BlastChar. (2018). *Telco Customer Churn* [Dataset]. Kaggle.
- IBM. (2018). *Telco Customer Churn on ICP4D*. GitHub.
- Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR*, 12, 2825-2830.
- Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5-32.
- Ester, M., et al. (1996). A Density-Based Algorithm for Discovering Clusters. *KDD-96*.

---

*Built as part of the ML Open Ended Lab — Iqra University, 2024*
