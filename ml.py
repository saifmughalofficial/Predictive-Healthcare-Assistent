"""Swappable ML layer. Add a model by adding one line to MODELS. Works with no downloads.
The demo training data is SYNTHETIC (generated from the rule table), so its output is a
second opinion for comparison only, never a validated prediction."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from engine import CONDS, SYM

MODELS = {"Logistic regression": lambda: LogisticRegression(max_iter=500),
          "Random forest": lambda: RandomForestClassifier(n_estimators=150, random_state=42),
          "Naive Bayes": lambda: BernoulliNB()}
KEYS = list(SYM)

def _synthetic(n=1500, seed=0):
    rng = np.random.default_rng(seed); X, y = [], []
    for _ in range(n):
        i = rng.integers(len(CONDS)); c = CONDS[i]; row = np.zeros(len(KEYS))
        for k, w in c["s"].items():
            if rng.random() < min(.95, .25 + w/4): row[KEYS.index(k)] = 1
        for k in rng.choice(KEYS, 1): row[KEYS.index(k)] = 1  # noise symptom
        X.append(row); y.append(i)
    return np.array(X), np.array(y)

def train(name):
    X, y = _synthetic(); m = MODELS[name](); m.fit(X, y); return m

def predict(model, syms, top=3):
    x = np.array([[1.0 if k in syms else 0.0 for k in KEYS]]); pr = model.predict_proba(x)[0]
    idx = np.argsort(-pr)[:top]
    return [(CONDS[model.classes_[i]]["n"], "higher" if pr[i]>.4 else "lower") for i in idx]  # no fake percentages
