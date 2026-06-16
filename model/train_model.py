"""
train_model.py
Trains and saves the Random Forest churn classifier and KMeans segmentation
model using the same preprocessing pipeline as the analysis notebook.

Usage:
    python3 model/train_model.py
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, 'data', 'telco_churn.csv')
MODEL_DIR  = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

RANDOM_STATE = 42

print("=" * 60)
print("  ML-OEL — Churn Model Training Pipeline")
print("=" * 60)

# ── 1. Load ───────────────────────────────────────────────────────────────────
print("\n[1/6]  Loading dataset ...")
df = pd.read_csv(DATA_PATH)
print(f"       Loaded {df.shape[0]:,} rows x {df.shape[1]} columns")

# ── 2. Preprocess ─────────────────────────────────────────────────────────────
print("\n[2/6]  Preprocessing ...")

# TotalCharges: blank strings → NaN → float → fill with median
df['TotalCharges'] = df['TotalCharges'].replace(' ', np.nan).astype(float)
tc_median = df['TotalCharges'].median()
df['TotalCharges'].fillna(tc_median, inplace=True)
print(f"       TotalCharges: {df['TotalCharges'].isna().sum()} NaNs remaining "
      f"(filled {(df['TotalCharges'] == tc_median).sum()} with median={tc_median:.2f})")

# Drop customerID
df.drop(columns=['customerID'], inplace=True)

# Encode target
df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})

# Binary categorical columns → 1/0
# Covers Yes/No, Male/Female, and service-not-subscribed variants
BINARY_COLS = [
    'gender',
    'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling',
    'MultipleLines', 'OnlineSecurity', 'OnlineBackup',
    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
]
BINARY_MAP = {
    'Yes': 1, 'No': 0,
    'Male': 1, 'Female': 0,
    'No phone service': 0,
    'No internet service': 0,
}

# Store the mapping so the API layer can apply the same encoding at inference
label_encoders = {col: BINARY_MAP for col in BINARY_COLS}

for col in BINARY_COLS:
    df[col] = df[col].map(BINARY_MAP).fillna(df[col])

# One-hot encode multi-class columns
OHE_COLS = ['InternetService', 'Contract', 'PaymentMethod']
df = pd.get_dummies(df, columns=OHE_COLS, drop_first=False)

# Scale numerical features
NUM_COLS = ['tenure', 'MonthlyCharges', 'TotalCharges']
scaler = StandardScaler()
df[NUM_COLS] = scaler.fit_transform(df[NUM_COLS])

print(f"       Final shape after encoding: {df.shape}")
print(f"       Churn rate: {df['Churn'].mean()*100:.1f}%")

# ── 3. Train / test split ─────────────────────────────────────────────────────
print("\n[3/6]  Splitting 80 / 20 (stratified, random_state=42) ...")
X = df.drop(columns=['Churn'])
y = df['Churn']

feature_columns = X.columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)
print(f"       Train: {X_train.shape[0]:,}  |  Test: {X_test.shape[0]:,}  |  Features: {X_train.shape[1]}")

# ── 4. Train Random Forest ────────────────────────────────────────────────────
print("\n[4/6]  Training Random Forest (n_estimators=100) ...")
rf = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec  = recall_score(y_test, y_pred, zero_division=0)
f1   = f1_score(y_test, y_pred, zero_division=0)

print(f"       Accuracy  : {acc:.4f}  ({acc*100:.2f}%)")
print(f"       Precision : {prec:.4f}")
print(f"       Recall    : {rec:.4f}")
print(f"       F1-Score  : {f1:.4f}")

# Feature importances (top 5)
fi = pd.Series(rf.feature_importances_, index=feature_columns).nlargest(5)
print("\n       Top 5 feature importances:")
for feat, imp in fi.items():
    bar = '█' * int(imp * 200)
    print(f"         {feat:<45s} {imp:.4f}  {bar}")

# ── 5. Train KMeans ──────────────────────────────────────────────────────────
print("\n[5/6]  Training KMeans (n_clusters=4, random_state=42) ...")
# Use the full feature matrix (no label) for unsupervised segmentation
X_all = df.drop(columns=['Churn']).values
kmeans = KMeans(n_clusters=4, random_state=RANDOM_STATE, n_init=10)
kmeans.fit(X_all)

cluster_labels = kmeans.labels_
cluster_counts = pd.Series(cluster_labels).value_counts().sort_index()
print("       Cluster sizes:")
for c, n in cluster_counts.items():
    pct = n / len(cluster_labels) * 100
    # Churn rate per cluster
    churn_rate = df['Churn'].values[cluster_labels == c].mean() * 100
    print(f"         Cluster {c}: {n:>4} customers ({pct:.1f}%)  |  Churn rate: {churn_rate:.1f}%")

print(f"       Inertia: {kmeans.inertia_:.1f}")

# ── 6. Save artefacts ─────────────────────────────────────────────────────────
print("\n[6/6]  Saving model artefacts ...")

def save_pkl(obj, filename):
    path = os.path.join(MODEL_DIR, filename)
    with open(path, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    size_kb = os.path.getsize(path) / 1024
    print(f"       Saved  {filename:<30s}  ({size_kb:.1f} KB)")

save_pkl(rf,              'churn_model.pkl')
save_pkl(kmeans,          'kmeans_model.pkl')
save_pkl(scaler,          'scaler.pkl')
save_pkl(feature_columns, 'feature_columns.pkl')
save_pkl(label_encoders,  'label_encoders.pkl')

# ── Summary ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  Training complete.")
print(f"  Model accuracy on test set : {acc*100:.2f}%")
print(f"  F1-Score                   : {f1:.4f}")
print(f"  Artefacts saved to         : {MODEL_DIR}/")
print("=" * 60)
