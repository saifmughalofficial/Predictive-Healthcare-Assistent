# AI Healthcare Assistant (free, offline mock project)

Decision-support tool. NOT a diagnosis and NOT a replacement for a doctor.

## Run in VS Code
1. Open this folder in VS Code, then open a terminal (Ctrl+`).
2. `python -m venv .venv`
3. Activate: Windows `.venv\Scripts\activate` | Mac/Linux `source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `streamlit run app.py`  (opens http://localhost:8501)

## Files
- `app.py`        Streamlit interface and single-page results dashboard
- `engine.py`     validation, text understanding, red flags, risk, conditions, medicines
- `ml.py`         swappable ML models (add one entry to `MODELS`)
- `knowledge.py`  PDF/text upload, optional OCR, TF-IDF retrieval (RAG sources)
- `datasets.py`   CSV/Excel/JSON profiling, quality checks, optional model training
- `storage.py`    local SQLite history (view/delete)
- `test_engine.py` quick safety tests: `python test_engine.py`

## Important
The built-in medical rules are a small demo. Replace them with verified guidelines
(upload trusted PDFs in the sidebar) before any real use. Data stays on your computer.
