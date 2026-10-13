import html
import streamlit as st
import engine as E, ml, storage
from knowledge import KnowledgeBase
import datasets as D

st.set_page_config(page_title="AI Healthcare Assistant", page_icon="🩺", layout="wide")

# ---------------- Styles & animation ----------------
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{--ink:#10272c;--mut:#5b7177;--line:#dde7ec;--teal:#0f766e;--teal2:#14b8a6;--sky:#3b82f6;
--shadow:0 1px 2px rgba(16,39,44,.04),0 10px 28px -14px rgba(16,39,44,.18)}
.stApp{font-family:'Plus Jakarta Sans',sans-serif;
background:radial-gradient(1100px 480px at 8% -8%,#d9f2ee 0,transparent 60%),radial-gradient(900px 420px at 100% 0,#e2eaff 0,transparent 55%),#f4f8fb}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1250px;padding-top:2.4rem;padding-bottom:3rem}
h1,h2,h3,h4{font-family:'Plus Jakarta Sans',sans-serif;letter-spacing:-.01em}

@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes grow{from{width:0}}
@keyframes pop{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}
@keyframes beat{0%,100%{transform:scale(1)}15%{transform:scale(1.15)}30%{transform:scale(1)}45%{transform:scale(1.1)}}
@keyframes ring{0%{box-shadow:0 0 0 0 rgba(192,33,47,.45)}70%{box-shadow:0 0 0 18px rgba(192,33,47,0)}100%{box-shadow:0 0 0 0 rgba(192,33,47,0)}}
@keyframes dash{to{stroke-dashoffset:-1200}}
@keyframes shine{from{background-position:-200% 0}to{background-position:200% 0}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}

/* Hero */
.hero{position:relative;overflow:hidden;border-radius:22px;padding:26px 30px 22px;color:#fff;margin-bottom:14px;
background:linear-gradient(120deg,#0b4f4a 0%,#0f766e 45%,#1d6fb8 100%);box-shadow:0 18px 40px -20px rgba(15,118,110,.6);animation:fadeUp .6s ease both}
.hero:before{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.10) 50%,transparent 70%);
background-size:200% 100%;animation:shine 6s linear infinite}
.hero-in{position:relative;display:flex;gap:18px;align-items:center;z-index:1}
.hero-badge{flex:none;width:64px;height:64px;border-radius:18px;display:grid;place-items:center;font-size:34px;
background:rgba(255,255,255,.16);backdrop-filter:blur(4px);border:1px solid rgba(255,255,255,.25);animation:floaty 4s ease-in-out infinite}
.hero h1{color:#fff;margin:0;font-size:2rem;font-weight:800;padding:0}
.hero p{margin:4px 0 10px;opacity:.9;font-size:.98rem}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips span{font-size:.78rem;font-weight:600;padding:5px 11px;border-radius:999px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22)}
.ecg{position:absolute;left:0;right:0;bottom:-4px;width:100%;height:56px;opacity:.35;z-index:0}
.ecg path{fill:none;stroke:#a7f3d0;stroke-width:2;stroke-dasharray:300 900;animation:dash 4.5s linear infinite}

/* Notice */
.notice{display:flex;gap:12px;align-items:flex-start;padding:12px 16px;border-radius:14px;margin:0 0 18px;font-size:.9rem;
background:#eef6ff;border:1px solid #cfe2fb;color:#183b5c;animation:fadeUp .6s .1s ease both}
.notice .i{font-size:1.2rem;line-height:1.2}

/* Cards (bordered containers given a card_* key) */
[class*="st-key-card"]{background:#fff;border:1px solid var(--line)!important;border-radius:18px!important;box-shadow:var(--shadow);
padding:6px 4px;animation:fadeUp .5s ease both;transition:transform .25s ease,box-shadow .25s ease}
[class*="st-key-card"]:hover{transform:translateY(-2px);box-shadow:0 1px 2px rgba(16,39,44,.05),0 18px 36px -16px rgba(16,39,44,.25)}
.sec{display:flex;align-items:center;gap:10px;margin:2px 0 8px}
.sec-ic{width:34px;height:34px;flex:none;border-radius:10px;display:grid;place-items:center;font-size:1.05rem;background:linear-gradient(135deg,#e0f5f2,#e5edff)}
.sec b{font-size:1.02rem;color:var(--ink)}
.sec small{display:block;color:var(--mut);font-size:.78rem;font-weight:500}

/* Risk card */
.risk{position:relative;border-radius:20px;padding:20px 22px 16px;margin:4px 0 14px;color:#14292e;overflow:hidden;
background:linear-gradient(135deg,var(--bg) 0%,#fff 120%);border:1px solid var(--fg);animation:fadeUp .5s ease both}
.risk:after{content:"";position:absolute;right:-40px;top:-40px;width:160px;height:160px;border-radius:50%;background:var(--fg);opacity:.07}
.risk.em{border-width:2px;animation:fadeUp .5s ease both,ring 1.8s ease-out .5s infinite}
.risk-top{display:flex;gap:16px;align-items:center}
.risk-ic{flex:none;width:58px;height:58px;border-radius:16px;display:grid;place-items:center;font-size:30px;background:#fff;box-shadow:0 6px 16px -8px var(--fg)}
.risk.em .risk-ic{animation:beat 1.4s ease-in-out infinite}
.risk-k{font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--fg)}
.risk h1{margin:0;font-size:1.75rem;font-weight:800;padding:0;color:#14292e}
.risk p{margin:2px 0 0}
.meter{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:16px 0 6px}
.meter i{height:8px;border-radius:99px;background:rgba(16,39,44,.09);transform-origin:left}
.meter i.on{background:var(--c);animation:pop .5s cubic-bezier(.2,.8,.2,1) both}
.meter i:nth-child(2){animation-delay:.12s}.meter i:nth-child(3){animation-delay:.24s}.meter i:nth-child(4){animation-delay:.36s}
.meter-l{display:grid;grid-template-columns:repeat(4,1fr);font-size:.72rem;color:var(--mut);font-weight:600}

/* Stat tiles */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:0 0 14px}
.stat{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px;box-shadow:var(--shadow);animation:fadeUp .5s ease both}
.stat:nth-child(2){animation-delay:.06s}.stat:nth-child(3){animation-delay:.12s}.stat:nth-child(4){animation-delay:.18s}
.stat .k{font-size:.72rem;color:var(--mut);font-weight:600;text-transform:uppercase;letter-spacing:.05em}
.stat .v{font-size:1.25rem;font-weight:800;color:var(--ink);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media (max-width:900px){.stats{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:1.5rem}}

/* Lists */
.why{list-style:none;padding:0;margin:0}
.why li{position:relative;padding:7px 10px 7px 30px;margin:5px 0;border-radius:10px;background:#f6fafb;border:1px solid #e9f0f3;animation:fadeUp .4s ease both}
.why li:before{content:"";position:absolute;left:12px;top:50%;width:8px;height:8px;margin-top:-4px;border-radius:50%;background:var(--teal2)}
.summary{font-size:1rem;line-height:1.55;padding:12px 14px;border-radius:12px;background:linear-gradient(135deg,#f0faf8,#f3f6ff);border:1px solid #e1edf0}

/* Condition matches */
.cond{padding:12px 0 10px;border-bottom:1px dashed var(--line);animation:fadeUp .45s ease both}
.cond:last-of-type{border-bottom:none}
.cond-h{display:flex;justify-content:space-between;gap:8px;align-items:baseline}
.tag{flex:none;font-size:.7rem;font-weight:700;padding:3px 9px;border-radius:999px}
.tag.t2{background:#dcf5ee;color:#0b6b57}.tag.t1{background:#e6efff;color:#2753a6}.tag.t0{background:#f0f2f4;color:#5b6770}
.bar{height:9px;border-radius:99px;background:#edf2f5;margin:8px 0 6px;overflow:hidden}
.bar i{display:block;height:100%;border-radius:99px;width:var(--w);animation:grow 1s cubic-bezier(.2,.8,.2,1) both;
background:linear-gradient(90deg,var(--teal2),var(--sky))}
.cond-d{color:var(--mut);font-size:.85rem}
.cond .ok{font-size:.88rem;margin-top:4px}.cond .no{font-size:.88rem;color:#b42318}.cond .q{font-size:.8rem;color:var(--mut);margin-top:2px}

/* Sources */
.src{border-left:3px solid var(--teal2);background:#f6fafb;border-radius:0 10px 10px 0;padding:8px 12px;margin:7px 0;font-size:.88rem;animation:fadeUp .4s ease both}

/* Empty state */
.empty{text-align:center;padding:42px 26px;border-radius:20px;background:#fff;border:1px dashed #c9dbe2;box-shadow:var(--shadow);animation:fadeUp .6s ease both}
.empty .pulse{width:84px;height:84px;margin:0 auto 14px;border-radius:50%;display:grid;place-items:center;font-size:38px;
background:linear-gradient(135deg,#e0f5f2,#e5edff);animation:beat 1.8s ease-in-out infinite}
.empty h3{margin:0 0 6px}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:20px;text-align:left}
.steps div{padding:12px;border-radius:12px;background:#f6fafb;border:1px solid #e9f0f3;font-size:.86rem}
.steps b{display:inline-grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--teal);color:#fff;font-size:.78rem;margin-bottom:6px}

/* History badges */
.hrow{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
.badge{font-weight:700;font-size:.85rem;padding:5px 12px;border-radius:999px;border:1px solid var(--fg);background:var(--bg);color:#14292e}
.ts{color:var(--mut);font-size:.8rem}

/* Streamlit widgets */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#ffffff 0%,#eef7f6 100%);border-right:1px solid var(--line)}
.side-brand{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:14px;margin-bottom:8px;color:#fff;
background:linear-gradient(120deg,#0f766e,#1d6fb8)}
.side-brand span{font-size:1.5rem}.side-brand b{display:block}.side-brand small{opacity:.85}
.side-h{font-size:.74rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--teal);margin:16px 0 4px}
[data-testid="stFileUploaderDropzone"]{border:1.5px dashed #9fcfc8;border-radius:14px;background:#f7fcfb;transition:border-color .2s,background .2s}
[data-testid="stFileUploaderDropzone"]:hover{border-color:var(--teal);background:#eefaf7}
[data-testid="stTabs"] [role="tablist"]{gap:6px;border-bottom:none;background:#fff;padding:6px;border-radius:14px;border:1px solid var(--line);box-shadow:var(--shadow);width:fit-content}
[data-testid="stTabs"] button[role="tab"]{border-radius:10px;padding:6px 16px;transition:background .2s,color .2s}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{background:linear-gradient(120deg,#0f766e,#1d6fb8);color:#fff}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p{color:#fff}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],[data-testid="stTabs"] [data-baseweb="tab-border"]{display:none}
[data-testid="stTabs"] [role="tabpanel"]{animation:fadeUp .4s ease both;padding-top:14px}
.stButton button,[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-secondary"]{border-radius:12px;font-weight:600;transition:transform .15s ease,box-shadow .2s ease}
.stButton button:hover{transform:translateY(-1px)}
[data-testid="stBaseButton-primary"]{background:linear-gradient(120deg,#0f766e,#1d6fb8);border:none;box-shadow:0 10px 22px -10px rgba(15,118,110,.7);padding:.65rem 1rem}
[data-testid="stBaseButton-primary"]:hover{box-shadow:0 14px 28px -10px rgba(15,118,110,.85)}
[data-testid="stExpander"] details{border-radius:14px;border-color:var(--line);background:#fbfdfe}
[data-testid="stAlert"]{border-radius:14px;animation:fadeUp .4s ease both}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px 18px;box-shadow:var(--shadow)}
[data-testid="stDataFrame"]{border-radius:14px;overflow:hidden;border:1px solid var(--line)}
.foot{text-align:center;color:var(--mut);font-size:.8rem;margin-top:26px}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
</style>""", unsafe_allow_html=True)

esc = html.escape
def card(key): return st.container(border=True, key=f"card_{key}")
def head(icon, title, sub=""):
    st.markdown(f'<div class="sec"><span class="sec-ic">{icon}</span><div><b>{title}</b>{f"<small>{sub}</small>" if sub else ""}</div></div>', unsafe_allow_html=True)
def bullets(items): st.markdown('<ul class="why">' + "".join(f"<li>{esc(str(x))}</li>" for x in items) + "</ul>", unsafe_allow_html=True)

if "kb" not in st.session_state: st.session_state.kb = KnowledgeBase()
if "res" not in st.session_state: st.session_state.res = None
kb = st.session_state.kb

st.markdown('<div class="hero"><div class="hero-in"><div class="hero-badge">🩺</div><div>'
            '<h1>AI Healthcare Assistant</h1><p>Symptom triage and decision support that runs entirely on your computer.</p>'
            '<div class="chips"><span>🛡️ Emergency checks first</span><span>🤖 ML second opinion</span>'
            '<span>📚 Answers from your documents</span><span>🔒 Private local history</span></div></div></div>'
            '<svg class="ecg" viewBox="0 0 1200 60" preserveAspectRatio="none"><path d="M0 34 H160 l12 -4 l10 4 H230 l10 -26 l12 46 l10 -30 l8 10 H420 l12 -4 l10 4 '
            'H560 l10 -26 l12 46 l10 -30 l8 10 H760 l12 -4 l10 4 H880 l10 -26 l12 46 l10 -30 l8 10 H1200"/></svg></div>', unsafe_allow_html=True)
st.markdown('<div class="notice"><span class="i">ℹ️</span><div>General health information and decision support only. It is <b>not a diagnosis</b> and does not replace a doctor. '
            'In an emergency call your local emergency number (1122 in Punjab, Pakistan; 911, 999 or 112 elsewhere).</div></div>', unsafe_allow_html=True)

# ---------------- Sidebar: uploads ----------------
with st.sidebar:
    st.markdown('<div class="side-brand"><span>🩺</span><div><b>Your data</b><small>Optional · stays on this computer</small></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-h">📄 Medical documents</div>', unsafe_allow_html=True)
    docs = st.file_uploader("PDF, TXT or MD (guidelines, medicine references, papers)", type=["pdf","txt","md"], accept_multiple_files=True)
    for f in docs or []:
        if f.name not in kb.docs:
            with st.spinner(f"Reading {f.name}…"): kb.add(f.name, f.getvalue())
    for n, s in kb.docs.items(): st.caption(f"📄 **{n}**: {s}")
    st.markdown('<div class="side-h">📊 Dataset</div>', unsafe_allow_html=True)
    dsf = st.file_uploader("CSV, Excel or JSON", type=["csv","xlsx","xls","json"])
    st.markdown('<div class="side-h">🤖 ML model</div>', unsafe_allow_html=True)
    model_name = st.selectbox("Second-opinion model", list(ml.MODELS))
    st.caption("Change models here without touching the rest of the app.")

tab_a, tab_d, tab_h = st.tabs(["🩺 Assessment", "📊 Dataset review", "🗂️ History"])

# ---------------- Assessment ----------------
with tab_a:
    left, right = st.columns([5, 7], gap="large")
    with left, card("form"):
        head("📝", "Tell us what is happening", "The more detail you give, the better the assessment")
        desc = st.text_area("Describe the problem in your own words", placeholder="e.g. I have had a headache for two days with fever and weakness.", height=90)
        syms = st.multiselect("Or pick symptoms (type to search)", list(E.SYM), format_func=E.SYM.get)
        c1, c2 = st.columns(2)
        age = c1.number_input("Age (years) *", 0, 130, None, step=1)
        sex = c2.selectbox("Sex (if relevant)", ["", "Female", "Male"], format_func=lambda x: x or "Prefer not to say")
        loc = c1.text_input("Where does it hurt?")
        sev = c2.slider("Pain / severity", 0, 10, 0)
        dur = c1.number_input("How long? (days)", 0.0, None, None, step=0.5)
        trend = c2.selectbox("Trend", ["", "better", "same", "worse"], format_func=lambda x: {"":"Not sure","better":"Getting better","same":"Staying the same","worse":"Getting worse"}[x])
        with st.expander("🧬 Medical background (recommended)"):
            cond = st.text_input("Existing conditions", placeholder="asthma, diabetes…")
            meds = st.text_input("Current medicines", placeholder="warfarin, aspirin…")
            alg = st.text_input("Allergies", placeholder="penicillin, ibuprofen…")
            hist = st.text_input("Relevant history", placeholder="surgery last month, pregnant…")
        with st.expander("💓 Vital signs (only if you have them)"):
            v1, v2, v3 = st.columns(3)
            temp = v1.number_input("Temp °C", value=None, step=0.1); hr = v2.number_input("Heart rate", value=None, step=1)
            spo = v3.number_input("SpO₂ %", value=None, step=1)
            sbp = v1.number_input("Systolic BP", value=None, step=1); glu = v2.number_input("Glucose mg/dL", value=None, step=1)
        go = st.button("🔍 Analyze symptoms", type="primary", use_container_width=True)

    if go:
        p = dict(desc=desc, syms=set(syms), age=age, sex=sex, loc=loc, sev=sev, dur=dur, trend=trend, cond=cond.lower(),
                 meds=meds.lower(), alg=alg.lower(), hist=hist.lower(), temp=temp, hr=hr, spo=spo, sbp=sbp, glu=glu)
        errs, warns = E.validate(p)
        if errs:
            st.session_state.res = None
            for e in errs: right.error(e)
        else:
            with right, st.spinner("Analyzing symptoms, checking warning signs and searching your documents…"):
                r = E.assess(p); r["warns"] = warns
                q = " ".join(r["names"] + [x["c"]["n"] for x in r["conds"]] + [desc])
                r["sources"] = kb.search(q)
                r["ml"] = ml.predict(ml.train(model_name), p["syms"]) if p["syms"] else []
                st.session_state.res = r

    with right:
        r = st.session_state.res
        if not r:
            st.markdown('<div class="empty"><div class="pulse">❤️</div><h3>Your assessment will appear here</h3>'
                        '<div style="color:var(--mut)">Enter the age and describe the symptoms, then press <b>Analyze symptoms</b>.</div>'
                        '<div class="steps"><div><b>1</b><br>Describe symptoms in your own words or pick from the list</div>'
                        '<div><b>2</b><br>Add age, duration and any vital signs you have</div>'
                        '<div><b>3</b><br>Get a risk level, possible causes and next steps</div></div></div>', unsafe_allow_html=True)
        else:
            name, lvl = r["names"], r["lvl"]; ic, title, msg, fg, bg = E.LEVELS[lvl]; em = lvl == 3
            seg = "".join(f'<i class="{"on" if i <= lvl else ""}" style="--c:{L[3]}"></i>' for i, L in enumerate(E.LEVELS))
            st.markdown(f'<div class="risk{" em" if em else ""}" style="--fg:{fg};--bg:{bg}"><div class="risk-top"><div class="risk-ic">{ic}</div>'
                        f'<div><div class="risk-k">Risk level</div><h1>{title}</h1><p>{msg}</p></div></div>'
                        f'<div class="meter">{seg}</div><div class="meter-l"><span>Low</span><span>Moderate</span><span>High</span><span>Emergency</span></div></div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="stats">' + "".join(f'<div class="stat"><div class="k">{k}</div><div class="v" title="{esc(str(v))}">{esc(str(v))}</div></div>' for k, v in [
                ("Symptoms", len(name)), ("Possible causes", len(r["conds"])), ("Reassess in", r["period"].replace(" to ", "–")), ("Warning signs", len(r["flags"]))]) + "</div>",
                unsafe_allow_html=True)
            if em:
                st.error("🚨 **Get emergency help now.** Do not wait for home treatment to work. Call your local emergency number "
                         "or go to the nearest hospital emergency department. If possible, do not travel alone.\n\n" + "\n".join(f"- {f}" for f in r["flags"]))
            with card("why"):
                head("🧭", "Why this level?", "Based only on the details entered. Emergency checks always come first.")
                bullets(r["why"])
            for w in r["warns"] + (["Duration was read from your description."] if r["p"].get("dur_auto") else []): st.warning(w)
            with card("summary"):
                head("🗒️", "Symptom summary", "Source: information you provided.")
                st.markdown(f'<div class="summary">{esc(r["summary"])}</div>', unsafe_allow_html=True)
            a, b = st.columns(2)
            with a, card("causes"):
                head("🔬", "Possible causes", "Possibilities only, not a diagnosis. Bars show relative match, not probability.")
                if not r["conds"]: st.write("The details do not clearly match a common cause. Add more symptoms or speak to a doctor.")
                out = ""
                for j, x in enumerate(r["conds"]):
                    t = 2 if x["ratio"]>=.55 else 1 if x["ratio"]>=.3 else 0
                    lab = ["Less likely", "Possible match", "Stronger match"][t]
                    out += (f'<div class="cond" style="animation-delay:{j*.08:.2f}s"><div class="cond-h"><b>Possible: {x["c"]["n"]}</b><span class="tag t{t}">{lab}</span></div>'
                            f'<div class="bar"><i style="--w:{min(1.0, max(.08, x["ratio"]))*100:.0f}%;animation-delay:{.15+j*.1:.2f}s"></i></div>'
                            f'<div class="cond-d">{x["c"]["d"]}</div><div class="ok">✔ Supports: {", ".join(E.SYM[k] for k in x["hit"])}</div>'
                            + (f'<div class="no">✖ Against: {", ".join(E.SYM[k] for k in x["con"])}</div>' if x["con"] else "")
                            + (f'<div class="q">Do you also have: {", ".join(E.SYM[k] for k in x["miss"])}?</div>' if x["miss"] else "") + "</div>")
                if out: st.markdown(out, unsafe_allow_html=True)
                if r["ml"]:
                    st.caption("🤖 ML second opinion (trained on synthetic demo data, not validated): " + "; ".join(f"{n} ({c})" for n, c in r["ml"]))
                st.caption("AI-generated assessment. It cannot confirm a diagnosis.")
            with b, card("todo"):
                head("✅", "What should I do now?")
                do = ["Get emergency help (see above).", "Stay with someone if you can."] if em else \
                     ["Arrange a medical check today.", "Note symptoms and any medicines taken."] if lvl==2 else \
                     ["Contact a doctor or pharmacist for advice.", "Use the home care tips."] if lvl==1 else \
                     ["Use the home care tips.", "Keep a simple symptom log."]
                st.markdown("**Do now**"); bullets(do)
                st.markdown("**Monitor**"); bullets(["Temperature twice a day", "Worsening or new symptoms", "Fluid intake and urine amount"])
                st.markdown("**See a doctor if**"); bullets([f"No improvement in {r['period']}", "Symptoms worsen or new ones appear"])
                st.markdown("**Go to hospital if**"); bullets(["Any warning sign below appears"])
            if not em:
                with card("care"):
                    head("🏠", "Home care", "Supportive only, not medical treatment")
                    bullets(["Rest and avoid strenuous activity", "Drink fluids regularly", "Eat light, balanced meals"] + r["care"])
                with card("meds"):
                    head("💊", "Medicine information", "General information, not a prescription. No doses are given. Ask a pharmacist or doctor first.")
                    for mid in r["meds"]:
                        m, issues = E.MEDS[mid], E.med_check(mid, r["p"])
                        st.markdown(f"**{m['n']}** · {'🧾 Prescription only' if m['rx'] else '🛒 Over the counter'}"); st.write(m["u"])
                        for x in m["pre"]: st.markdown(f"- {x}")
                        (st.error if issues else st.success)(("Check with a professional: " + "; ".join(issues) + ".") if issues else "No conflict found with the details you gave.")
                        st.caption("Professional advice is recommended before use.")
            with card("warn"):
                head("⚠️", "Warning signs: get urgent care if you notice")
                bullets(E.WARN)
            with card("doctor"):
                head("🏥", "Doctor or hospital")
                st.write("**Go to a hospital or call emergency services now.**" if em else "**See a doctor promptly, today if possible.**" if lvl==2 else
                         "Contact a doctor if symptoms persist or worsen." if lvl==1 else "A doctor visit is not urgent if you improve.")
                st.markdown(f"*When to see a doctor:* symptoms have not improved within {r['period']}; they get worse; new symptoms appear; self-care does not help; you have a worrying medical history; or you are unsure about this assessment.")
                st.markdown(f"**Follow-up:** reassess in **{r['period']}**.")
            with card("sources"):
                head("📚", "Sources")
                st.markdown('<div class="src"><b>Your input:</b> details you entered.</div><div class="src"><b>Built-in demo knowledge base:</b> simple rules. Replace with verified guidelines.</div>', unsafe_allow_html=True)
                for s in r["sources"]: st.markdown(f'<div class="src"><b>Retrieved from “{esc(str(s["doc"]))}”, page {s["page"]}:</b> {esc(s["text"][:300])}…</div>', unsafe_allow_html=True)
                if kb.docs and not r["sources"]: st.caption("No matching passage in the uploaded documents.")
                st.markdown('<div class="src"><b>AI-generated:</b> summary and match labels.</div>', unsafe_allow_html=True)
            if st.button("💾 Save to my history"):
                storage.save(", ".join(name), f"{ic} {title}", r["summary"]); st.toast("Saved to your history.", icon="✅"); st.success("Saved.")

# ---------------- Dataset ----------------
with tab_d:
    if not dsf:
        st.markdown('<div class="empty"><div class="pulse">📊</div><h3>No dataset yet</h3><div style="color:var(--mut)">'
                    'Upload a CSV, Excel or JSON dataset in the sidebar. Nothing is used until you review it here.</div></div>', unsafe_allow_html=True)
    else:
        try:
            df = D.load(dsf.name, dsf.getvalue()); prof, issues, dup = D.profile(df)
            st.success(f"Read **{dsf.name}**: {len(df)} rows, {df.shape[1]} columns, {dup} duplicate rows.")
            st.markdown('<div class="stats">' + "".join(f'<div class="stat"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in [
                ("Rows", f"{len(df):,}"), ("Columns", df.shape[1]), ("Duplicate rows", dup), ("Quality issues", len(issues))]) + "</div>", unsafe_allow_html=True)
            for i in issues: st.warning(i)
            if not issues: st.success("No major quality problems found.")
            with card("profile"):
                head("🧪", "Column profile"); st.dataframe(prof, use_container_width=True)
            with card("preview"):
                head("👀", "Preview", "First 20 rows"); st.dataframe(df.head(20), use_container_width=True)
            with card("stats"):
                head("📈", "Statistics"); st.dataframe(df.describe(include="all").T, use_container_width=True)
            with card("train"):
                head("🤖", "Train a test model", f"Using: {model_name}")
                tg = prof[prof.possible_target].column.tolist() or df.columns.tolist()
                t = st.selectbox("Target column to predict", tg)
                if st.button("⚙️ Prepare data and train"):
                    try:
                        with st.spinner("Training with cross-validation…"): acc, n, num, cat = D.train_on(df, t, model_name)
                        st.success(f"Used {n} rows after removing duplicates and empty targets. Numeric: {num}. Categorical: {cat}.")
                        st.metric("Cross-validated accuracy", f"{acc:.2f}"); st.caption("Trained only for testing. It is not used for patient advice unless validated by experts.")
                    except Exception as e: st.error(f"Training failed: {e}")
        except Exception as e: st.error(f"Could not read this file (it may be corrupted or unsupported): {e}")

# ---------------- History ----------------
with tab_h:
    rows = storage.all_rows()
    if not rows:
        st.markdown('<div class="empty"><div class="pulse">🗂️</div><h3>No saved assessments yet</h3><div style="color:var(--mut)">'
                    'Run an assessment and press <b>Save to my history</b> to track how you are doing.</div></div>', unsafe_allow_html=True)
    for i, ts, sy, rk, sm, stt in rows:
        fg, bg = next(((L[3], L[4]) for L in E.LEVELS if rk.startswith(L[0])), ("#9bb", "#f3f6f7"))
        with card(f"h{i}"):
            st.markdown(f'<div class="hrow"><span class="badge" style="--fg:{fg};--bg:{bg}">{esc(rk)}</span><span class="ts">🕒 {esc(ts)}</span></div>', unsafe_allow_html=True)
            st.write(sm)
            c1, c2 = st.columns([3, 1], vertical_alignment="bottom"); opts = ["Open", "Improving", "Worse", "Resolved", "Saw a doctor"]
            n = c1.selectbox("Follow-up status", opts, opts.index(stt) if stt in opts else 0, key=f"s{i}")
            if n != stt: storage.set_status(i, n)
            if c2.button("🗑️ Delete", key=f"d{i}", use_container_width=True): storage.delete(i); st.rerun()
    if rows and st.button("Delete all records"): storage.delete(); st.rerun()
    st.caption("Stored only in history.db on this computer.")

st.markdown('<div class="foot">AI Healthcare Assistant · Decision support only, not a diagnosis · Data never leaves this computer</div>', unsafe_allow_html=True)
