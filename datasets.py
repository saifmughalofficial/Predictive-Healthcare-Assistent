"""Read CSV/Excel/JSON, show what is inside, check quality, optionally train a model."""
import io, json
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from ml import MODELS

def load(name, data):
    n = name.lower()
    if n.endswith(".csv"): return pd.read_csv(io.BytesIO(data))
    if n.endswith((".xlsx", ".xls")): return pd.read_excel(io.BytesIO(data))
    if n.endswith(".json"):
        j = json.loads(data.decode("utf-8"))
        return pd.json_normalize(j if isinstance(j, list) else j.get("data", j.get("records", [j])))
    raise ValueError("Unsupported file type. Use .csv, .xlsx or .json")

def profile(df):
    num = df.select_dtypes("number").columns.tolist(); cat = [c for c in df.columns if c not in num]
    rows = [{"column":c,"type":"numeric" if c in num else "categorical","missing":int(df[c].isna().sum()),
             "unique":int(df[c].nunique()),"possible_target":(c in cat and 1<df[c].nunique()<=10) or (c in num and df[c].nunique()==2)} for c in df.columns]
    issues = []
    dup = int(df.duplicated().sum())
    if dup: issues.append(f"{dup} duplicate row(s)")
    for c in df.columns:
        if df[c].isna().mean() > .2: issues.append(f"'{c}' is {df[c].isna().mean():.0%} empty")
    if df.shape[1] < 2: issues.append("Only one column found")
    if len(df) < 30: issues.append("Fewer than 30 rows: too small to train a reliable model")
    return pd.DataFrame(rows), issues, dup

def train_on(df, target, model_name):
    """Prepare data (impute, scale, one-hot) and cross-validate the chosen model."""
    d = df.dropna(subset=[target]).drop_duplicates(); X, y = d.drop(columns=[target]), d[target].astype(str)
    num = X.select_dtypes("number").columns.tolist(); cat = [c for c in X.columns if c not in num]
    pre = ColumnTransformer([("n", Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]), num),
                             ("c", Pipeline([("i", SimpleImputer(strategy="most_frequent")), ("o", OneHotEncoder(handle_unknown="ignore"))]), cat)])
    pipe = Pipeline([("pre", pre), ("m", MODELS[model_name]())])
    cv = min(5, y.value_counts().min()); 
    if cv < 2: raise ValueError("Each target class needs at least 2 rows.")
    return cross_val_score(pipe, X, y, cv=cv).mean(), len(d), num, cat
