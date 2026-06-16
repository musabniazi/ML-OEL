"""
api/predict.py  —  Vercel Python serverless function
POST /api/predict  →  churn probability + customer segment
"""

import sys, os, warnings

# Ensure repo root is on sys.path so pickle can find any custom classes
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Suppress sklearn feature-name warning from KMeans (fitted on arrays, not DataFrames)
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

from http.server import BaseHTTPRequestHandler
import json
import pickle
import numpy as np
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
# __file__ = <repo_root>/api/predict.py  →  model dir is one level up
_HERE     = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(_HERE, '..', 'model')

def _load(name):
    path = os.path.join(MODEL_DIR, name)
    with open(path, 'rb') as f:
        return pickle.load(f)

# Load once at module import — Vercel reuses warm containers
_READY = False
_ERR   = ''
try:
    RF     = _load('churn_model.pkl')
    KM     = _load('kmeans_model.pkl')
    SCALER = _load('scaler.pkl')
    FCOLS  = _load('feature_columns.pkl')   # 26 columns in exact training order
    _READY = True
except Exception as exc:
    _ERR = str(exc)

# ── Encoding constants (must match train_model.py) ────────────────────────────
BINARY_MAP = {
    'Yes': 1, 'No': 0,
    'Male': 1, 'Female': 0,
    'No phone service': 0,
    'No internet service': 0,
}

BINARY_COLS = [
    'gender', 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling',
    'MultipleLines', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
    'TechSupport', 'StreamingTV', 'StreamingMovies',
]

OHE_COLS = ['InternetService', 'Contract', 'PaymentMethod']
NUM_COLS = ['tenure', 'MonthlyCharges', 'TotalCharges']

# ── Cluster → segment mapping (matches user-specified requirement) ─────────────
SEGMENT_MAP = {
    0: {'name': 'High Risk',        'color': '#FF6B6B',
        'desc': 'Customer shows multiple high-churn indicators. Immediate retention action required.'},
    1: {'name': 'Loyal Customer',   'color': '#00C9FF',
        'desc': 'Long-tenured, engaged customer. Focus on upsell and satisfaction maintenance.'},
    2: {'name': 'Price Sensitive',  'color': '#FFB347',
        'desc': 'Customer is responsive to pricing signals. Value-bundle offers may reduce churn risk.'},
    3: {'name': 'New Customer',     'color': '#00F5A0',
        'desc': 'Early-lifecycle customer. Strong onboarding experience is critical in this phase.'},
}


# ── Preprocessing ─────────────────────────────────────────────────────────────
def preprocess(raw: dict) -> pd.DataFrame:
    df = pd.DataFrame([raw])

    # Binary columns
    for col in BINARY_COLS:
        if col in df.columns:
            df[col] = df[col].map(BINARY_MAP).fillna(0).astype(int)

    # SeniorCitizen comes in as int already
    df['SeniorCitizen'] = int(raw.get('SeniorCitizen', 0))

    # Ensure numerics are float
    for col in NUM_COLS:
        df[col] = float(raw.get(col, 0))

    # One-hot encode (produces same column names as training pd.get_dummies)
    df = pd.get_dummies(df, columns=OHE_COLS, drop_first=False)

    # Reindex to exact training column order, filling any missing OHE cols with 0
    df = df.reindex(columns=FCOLS, fill_value=0)

    # Scale the three numerical features
    df[NUM_COLS] = SCALER.transform(df[NUM_COLS])

    return df


# ── Insight generators ────────────────────────────────────────────────────────
def get_key_factors(raw: dict) -> list:
    factors = []
    tenure  = float(raw.get('tenure', 0))
    monthly = float(raw.get('MonthlyCharges', 0))

    if raw.get('Contract') == 'Month-to-month':
        factors.append('Month-to-month contract — no long-term commitment barrier')
    if raw.get('InternetService') == 'Fiber optic':
        factors.append('Fiber optic subscriber — highest-churn internet tier')
    if raw.get('PaymentMethod') == 'Electronic check':
        factors.append('Electronic check payment — correlated with ~45% churn rate')
    if monthly > 65:
        factors.append(f'High monthly charges (${monthly:.2f}) — price-sensitivity risk')
    if tenure < 12:
        factors.append(f'Short tenure ({int(tenure)} months) — critical early-lifecycle window')
    if raw.get('OnlineSecurity') in ('No', 'No internet service'):
        factors.append('No Online Security — lower service engagement depth')
    if raw.get('TechSupport') in ('No', 'No internet service'):
        factors.append('No Tech Support — reduced perceived value')

    if not factors:
        factors = [
            'Customer profile matches low-risk cohort',
            'No dominant churn predictors detected',
            'Stable tenure and payment history observed',
        ]
    return factors[:3]


def get_recommendations(raw: dict) -> list:
    recs    = []
    tenure  = float(raw.get('tenure', 0))
    monthly = float(raw.get('MonthlyCharges', 0))

    if raw.get('Contract') == 'Month-to-month':
        recs.append('Offer a 15% discount to upgrade to a 1-year contract')
    if raw.get('PaymentMethod') == 'Electronic check':
        recs.append('Incentivize auto-pay switch with a $5/month bill credit')
    if raw.get('InternetService') == 'Fiber optic' and monthly > 70:
        recs.append('Introduce a Fiber Value Bundle to justify premium pricing')
    if raw.get('OnlineSecurity') in ('No', 'No internet service'):
        recs.append('Bundle Online Security to deepen service engagement')
    if raw.get('TechSupport') in ('No', 'No internet service'):
        recs.append('Offer a 3-month complimentary Tech Support trial')
    if tenure < 12:
        recs.append('Enroll in Early Loyalty Programme with dedicated onboarding')
    if monthly > 75:
        recs.append('Schedule a billing review call for a personalized savings offer')

    if not recs:
        recs = [
            'Schedule a proactive customer success check-in call',
            'Offer exclusive loyalty rewards for continued service',
            'Send a personalized satisfaction survey to capture feedback',
        ]
    return recs[:3]


# ── CORS helper ───────────────────────────────────────────────────────────────
def _cors(h):
    h.send_header('Access-Control-Allow-Origin',  '*')
    h.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
    h.send_header('Access-Control-Allow-Headers', 'Content-Type')


# ── Vercel handler class ──────────────────────────────────────────────────────
class handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # suppress default Apache-style logs

    def do_OPTIONS(self):
        self.send_response(200)
        _cors(self)
        self.end_headers()

    def do_POST(self):
        if not _READY:
            return self._send(500, {'error': f'Model loading failed: {_ERR}'})

        # Parse request body
        try:
            length = int(self.headers.get('Content-Length', 0))
            raw    = json.loads(self.rfile.read(length))
        except Exception as exc:
            return self._send(400, {'error': f'Invalid JSON payload: {exc}'})

        # Run inference
        try:
            X    = preprocess(raw)
            prob = float(RF.predict_proba(X)[0][1])
            pred = 'Yes' if prob >= 0.5 else 'No'

            # Risk tier
            if prob < 0.30:
                risk_level, risk_color = 'Low',    '#00F5A0'
            elif prob < 0.60:
                risk_level, risk_color = 'Medium', '#FFB347'
            else:
                risk_level, risk_color = 'High',   '#FF6B6B'

            # Customer segment
            cluster = int(KM.predict(X)[0])
            seg     = SEGMENT_MAP.get(cluster, SEGMENT_MAP[0])

            payload = {
                'churn_probability': round(prob, 4),
                'churn_prediction':  pred,
                'risk_level':        risk_level,
                'risk_color':        risk_color,
                'segment':           seg['name'],
                'segment_color':     seg['color'],
                'segment_desc':      seg['desc'],
                'recommendations':   get_recommendations(raw),
                'key_factors':       get_key_factors(raw),
            }
            self._send(200, payload)

        except Exception as exc:
            self._send(500, {'error': str(exc)})

    def _send(self, status: int, data: dict):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',   'application/json')
        self.send_header('Content-Length', str(len(body)))
        _cors(self)
        self.end_headers()
        self.wfile.write(body)
