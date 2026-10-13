"""Rule engine: validation, text understanding, red flags, risk, conditions, medicines."""
import re

SYM = {"fever":"Fever","headache":"Headache","weak":"Weakness / tiredness","cough":"Cough","sore":"Sore throat",
"runny":"Runny or blocked nose","sneeze":"Sneezing / itchy eyes","ache":"Body aches","chills":"Chills","nausea":"Nausea",
"vomit":"Vomiting","diarrhea":"Diarrhea","abd":"Stomach pain","burn":"Burning when urinating","freq":"Frequent urination",
"sob":"Shortness of breath","chest":"Chest pain","wheeze":"Wheezing","dizzy":"Dizziness","rash":"Rash","itch":"Itching",
"smell":"Loss of smell or taste","neck":"Stiff neck","light":"Light sensitivity","sinus":"Facial / sinus pressure",
"back":"Back pain","joint":"Joint or muscle pain","confuse":"Confusion","faint":"Fainting","bleed":"Heavy bleeding",
"swell":"Swelling of face or lips","dry":"Very dry mouth / little urine","palp":"Racing heartbeat"}

NLP = {"fever":r"fever|temperature|feverish","headache":r"head ?ache|head pain|migraine","weak":r"weak|tired|fatigue|exhaust",
"cough":r"cough","sore":r"sore throat|throat pain","runny":r"runny|blocked nose|stuffy|congest","sneeze":r"sneez|itchy eyes",
"ache":r"body ache|aching","chills":r"chill|shiver","nausea":r"nause|queasy","vomit":r"vomit|throwing up",
"diarrhea":r"diarrh|loose stool","abd":r"stomach|abdom|belly","burn":r"burning.*(urin|pee)|painful urin",
"freq":r"frequent urin|urinat.*often","sob":r"short(ness)? of breath|breathless|can.?t breathe|difficulty breathing",
"chest":r"chest (pain|pressure|tight)","wheeze":r"wheez","dizzy":r"dizz|light.?headed","rash":r"rash|hives","itch":r"itch",
"smell":r"lost.*(smell|taste)|no smell","neck":r"stiff neck|neck stiff","light":r"light sensitiv|photophobia",
"sinus":r"sinus|facial pressure","back":r"back pain","joint":r"joint|muscle pain","confuse":r"confus|disorient",
"faint":r"faint|passed out|unconscious","bleed":r"bleeding|blood loss","swell":r"swollen (face|lips|tongue)|face swelling",
"dry":r"dry mouth|not urinating|dehydrat","palp":r"palpitat|racing heart"}
STROKE = r"slurred|face droop|drooping|weakness on one side|one side.*(weak|numb)|sudden.*(vision|speech)"

CONDS = [
 {"n":"Common cold","s":{"runny":2,"sore":2,"cough":2,"sneeze":1,"fever":.5,"ache":.5},"no":["sob"],"d":"A mild viral infection of nose and throat, usually settling within about a week.","care":["Rest and drink plenty of fluids","Warm drinks or steam can soothe the throat"],"m":["paracetamol","saline"]},
 {"n":"Influenza (flu) or other viral fever","s":{"fever":3,"ache":2,"chills":2,"weak":2,"headache":1.5,"cough":1.5,"sore":1},"no":[],"d":"Viral infections often cause fever, aches and tiredness together.","care":["Rest and drink often","Check your temperature twice a day","Stay home to avoid spreading it"],"m":["paracetamol"]},
 {"n":"Dengue, malaria or typhoid-type fever (region-dependent)","s":{"fever":3,"headache":2,"joint":2,"weak":1.5,"rash":1.5,"chills":1.5,"nausea":1,"abd":1},"no":["runny"],"d":"Fever with headache and body pain can need a blood test, especially where mosquito-borne illness is common.","care":["Do not start aspirin or ibuprofen before dengue is ruled out","Ask a doctor about a blood test if fever lasts over 2 days"],"m":["paracetamol"]},
 {"n":"Tension-type headache","s":{"headache":3,"dizzy":.5,"weak":.5,"neck":.5},"no":["fever","neck","confuse"],"d":"Common headache linked to stress, poor sleep, screens or dehydration.","care":["Rest in a quiet room","Take breaks from screens"],"m":["paracetamol","ibuprofen"]},
 {"n":"Migraine","s":{"headache":3,"light":2.5,"nausea":2,"dizzy":1},"no":["fever"],"d":"Throbbing headaches, often with nausea and light sensitivity.","care":["Rest in a dark, quiet room","Keep a diary of triggers"],"m":["paracetamol"]},
 {"n":"Stomach infection (gastroenteritis) or food poisoning","s":{"diarrhea":3,"vomit":2.5,"nausea":2,"abd":2,"fever":1},"no":["runny"],"d":"Usually a virus or contaminated food; the main risk is fluid loss.","care":["Sip oral rehydration solution often","Eat light foods when you can"],"m":["ors"]},
 {"n":"Dehydration","s":{"dry":3,"dizzy":1.5,"weak":1.5,"vomit":1,"diarrhea":1,"fever":.5},"no":[],"d":"Not enough body fluid, often after fever, vomiting or diarrhea.","care":["Sip fluids or oral rehydration solution regularly"],"m":["ors"]},
 {"n":"Urinary tract infection","s":{"burn":3.5,"freq":2.5,"abd":1,"back":1,"fever":1},"no":["runny","cough"],"d":"Usually needs a urine test and sometimes antibiotics.","care":["Drink water","See a clinician for a urine test"],"m":["abx"]},
 {"n":"Allergy (e.g. hay fever)","s":{"sneeze":3,"runny":2,"itch":2,"rash":1.5},"no":["fever"],"d":"The immune system reacting to pollen, dust or other triggers.","care":["Avoid known triggers","Rinse nose with saline"],"m":["antihist","saline"]},
 {"n":"Sinusitis","s":{"sinus":3,"runny":2,"headache":1.5,"fever":1,"cough":1},"no":[],"d":"Inflamed sinuses, often after a cold.","care":["Steam inhalation and saline rinses"],"m":["saline","paracetamol"]},
 {"n":"Chest infection or asthma flare-up","s":{"cough":2.5,"wheeze":3,"sob":2.5,"fever":1.5,"chest":1},"no":[],"d":"Breathing symptoms with cough or fever need careful monitoring.","care":["Sit upright and stay calm","Use your own prescribed inhaler as directed"],"m":["abx"]},
 {"n":"Muscle strain or joint pain","s":{"back":3,"joint":3,"ache":1},"no":["fever"],"d":"Often follows overuse, lifting or poor posture.","care":["Gentle movement and warmth","Avoid heavy lifting for a few days"],"m":["paracetamol","ibuprofen"]}]

MEDS = {
 "paracetamol":{"n":"Paracetamol (acetaminophen)","u":"Eases fever and mild pain.","rx":False,"pre":["Do not combine with other paracetamol-containing products","Liver disease or heavy alcohol use need medical advice first"],"cond":r"liver|hepat","alg":r"paracetamol|acetaminophen"},
 "ibuprofen":{"n":"Ibuprofen","u":"Eases pain and inflammation.","rx":False,"pre":["Take with food","Can irritate stomach and affect kidneys","Avoid with suspected dengue"],"cond":r"asthma|ulcer|kidney|renal|heart|gastritis|pregnan","alg":r"ibuprofen|nsaid|aspirin","med":r"warfarin|aspirin|clopidogrel|naproxen|diclofenac|apixaban|rivaroxaban","age":lambda a:a<12 or a>=65},
 "ors":{"n":"Oral rehydration salts (ORS)","u":"Replaces water and salts lost with diarrhea, vomiting or fever.","rx":False,"pre":["Mix exactly as the packet says","Seek care if you cannot keep fluids down"],"cond":r"kidney|renal|heart failure"},
 "antihist":{"n":"Non-drowsy antihistamine (e.g. cetirizine)","u":"Relieves sneezing, itching and runny nose from allergy.","rx":False,"pre":["May cause drowsiness in some people","Ask a pharmacist if pregnant or on other medicines"],"alg":r"cetirizine|loratadine|antihistamine"},
 "saline":{"n":"Saline nasal spray or rinse","u":"Clears blocked nose and sinuses.","rx":False,"pre":["Use clean or boiled-and-cooled water for rinses"]},
 "abx":{"n":"Antibiotics","u":"Only for bacterial infections; they do not work on viruses.","rx":True,"pre":["Prescription only: a doctor must decide if needed","Never use leftover antibiotics"]}}

LEVELS = [("🟢","Low risk","Self-care and monitoring are usually reasonable.","#1f8a4c","#e5f5ec"),
          ("🟡","Moderate risk","Speak to a doctor or pharmacist, especially if it does not improve.","#a87a00","#fff6d6"),
          ("🟠","High risk","Get a medical check promptly, ideally today.","#c2570c","#ffe9d6"),
          ("🔴","Emergency: get help now","Call emergency services or go to the nearest emergency department immediately.","#c0212f","#fde4e6")]
WARN = ["Trouble breathing or chest pain/pressure","Fainting, confusion or a seizure","Stiff neck with fever or severe headache",
        "Swelling of face or lips, or a spreading rash","Uncontrolled bleeding, black or bloody stools or vomit",
        "Cannot keep fluids down, or very little urine for 8+ hours","Sudden weakness, numbness, speech or vision problems"]

RANGES = {"temp":(30,45,"Temperature (°C)"),"hr":(20,250,"Heart rate"),"spo":(50,100,"Oxygen saturation"),
          "sbp":(40,300,"Systolic blood pressure"),"glu":(20,1000,"Glucose")}

def validate(p):
    """Return (errors, warnings). Errors block the analysis; we ask instead of assuming."""
    e, w = [], []
    if p.get("age") is None: e.append("Please enter the age. Risk depends on it.")
    elif not 0 <= p["age"] <= 120: e.append("Age must be between 0 and 120.")
    for k,(a,b,n) in RANGES.items():
        v = p.get(k)
        if v is not None and not a <= v <= b: e.append(f"{n} of {v} looks impossible (expected {a} to {b}). Please check it.")
    if not p.get("desc","").strip() and not p.get("syms"): e.append("Describe the problem or pick at least one symptom.")
    if p.get("dur") is not None and p["dur"] < 0: e.append("Duration cannot be negative.")
    if p.get("sex") == "Male" and re.search("pregnan", p.get("hist","")+p.get("cond","")): w.append("'Male' and 'pregnant' conflict. Please check your entries.")
    if p.get("temp") is not None and p["temp"] >= 38 and "fever" not in p["syms"]:
        p["syms"].add("fever"); w.append("Temperature is 38 °C or higher, so 'fever' was counted.")
    if p.get("dur") is None: w.append("No duration given, so we could not judge how long this has lasted.")
    return e, w

def extract(p):
    """Understand free text: add symptoms, duration, trend, stroke words. Simple negation handling."""
    t = p.get("desc","").lower()
    for k, rx in NLP.items():
        if re.search(rx, t) and not re.search(r"(no|without|denies|not)\s+(\w+\s+){0,2}"+rx.split("|")[0], t): p["syms"].add(k)
    m = re.search(r"(\d+(?:\.\d+)?)\s*(day|days|week|weeks|hour|hours)", t)
    if m and p.get("dur") is None:
        n = float(m[1]); p["dur"] = n*7 if "week" in m[2] else n/24 if "hour" in m[2] else n; p["dur_auto"] = True
    p["stroke"] = bool(re.search(STROKE, t))
    if re.search(r"worse|worsening|deteriorat", t) and not p.get("trend"): p["trend"] = "worse"
    return p

def redflags(p):
    """Separate safety layer. Any hit means Emergency and overrides everything else."""
    s, a, sev, f = p["syms"], p.get("age"), p.get("sev",0), []
    v = lambda k: p.get(k)
    if p.get("stroke"): f.append("Possible stroke signs (face drooping, slurred speech, one-sided weakness)")
    if "sob" in s and (sev>=7 or s&{"chest","faint"} or p.get("trend")=="worse" or re.search(r"can.?t breathe|difficulty breathing", p.get("desc","").lower())): f.append("Serious difficulty breathing")
    if "chest" in s and (sev>=6 or s&{"sob","palp","faint"} or (a or 0)>=40): f.append("Chest pain, which can be a heart problem")
    if "faint" in s: f.append("Loss of consciousness or fainting")
    if "confuse" in s: f.append("New confusion")
    if "neck" in s and s&{"fever","headache","light"}: f.append("Stiff neck with fever or headache (possible meningitis)")
    if "swell" in s and s&{"sob","rash","itch"}: f.append("Possible severe allergic reaction")
    if "bleed" in s and sev>=5: f.append("Heavy or uncontrolled bleeding")
    if "dry" in s and s&{"vomit","diarrhea","dizzy"}: f.append("Signs of severe dehydration")
    if v("spo") is not None and v("spo")<92: f.append(f"Low oxygen level ({v('spo')}%)")
    if v("hr") is not None and (v("hr")>130 or v("hr")<40): f.append(f"Very abnormal heart rate ({v('hr')}/min)")
    if v("sbp") is not None and (v("sbp")<90 or v("sbp")>180): f.append(f"Very abnormal blood pressure ({v('sbp')})")
    if v("temp") is not None and v("temp")>=40: f.append(f"Very high temperature ({v('temp')} °C)")
    if v("glu") is not None and (v("glu")<54 or v("glu")>400): f.append(f"Dangerous blood glucose ({v('glu')} mg/dL)")
    if a is not None and a<1 and ("fever" in s or (v("temp") or 0)>=38): f.append("Fever in a baby under 1 year")
    if sev>=9 and p.get("trend")=="worse": f.append("Severe symptoms that are getting worse quickly")
    return f

def assess_risk(p, flags):
    """Return (level 0-3, list of reasons actually used)."""
    if flags: return 3, ["Warning signs found: " + "; ".join(flags)]
    sc, why = 0.0, []
    def add(n, t): nonlocal sc; sc += n; why.append(t)
    sev, dur, age = p.get("sev",0), p.get("dur"), p.get("age")
    if sev>=7: add(3, f"High severity ({sev}/10)")
    elif sev>=4: add(1.5, f"Moderate severity ({sev}/10)")
    if dur is not None and dur>=7: add(2, f"Lasting {dur:g} days")
    elif dur is not None and dur>=3: add(1, f"Lasting {dur:g} days")
    if age is not None and (age<5 or age>=65): add(1.5, f"Age {age} carries higher risk")
    if re.search(r"asthma|diabet|heart|copd|kidney|cancer|immun|hiv|pregnan|transplant|hypertens|blood pressure", p.get("cond","")+" "+p.get("hist","")): add(1.5, "Existing health condition may raise the risk")
    if p.get("trend")=="worse": add(2, "Symptoms are getting worse")
    t = p.get("temp")
    if t is not None and t>=39: add(1.5, f"Fever of {t} °C")
    elif t is not None and t>=38: add(.7, f"Fever of {t} °C")
    if p.get("spo") is not None and p["spo"]<95: add(2, f"Oxygen {p['spo']}% is below normal")
    if p.get("hr") is not None and (p["hr"]>110 or p["hr"]<50): add(1, f"Heart rate {p['hr']}/min is outside normal")
    n = len(p["syms"])
    if n>=5: add(1.5, f"{n} different symptoms together")
    elif n>=3: add(.7, "Several symptoms together")
    if {"fever","headache","weak"} <= p["syms"]: add(1, "Fever with headache and weakness together")
    if not why: why.append("No worrying features found in what was entered")
    return (2 if sc>=7 else 1 if sc>=3.5 else 0), why

def rank_conditions(p, top=4):
    out = []
    for c in CONDS:
        tot = sum(c["s"].values()); hit = [k for k in c["s"] if k in p["syms"]]
        m = sum(c["s"][k] for k in hit); con = [k for k in c["no"] if k in p["syms"]]; m -= 1.5*len(con)
        if hit and m >= 2:
            out.append({"c":c,"m":m,"ratio":m/tot,"hit":hit,"con":con,"miss":[k for k,w in c["s"].items() if w>=2 and k not in p["syms"]]})
    return sorted(out, key=lambda x:-x["m"])[:top]

def med_check(mid, p):
    m, r = MEDS[mid], []
    txt, age = p.get("cond","")+" "+p.get("hist",""), p.get("age")
    if m.get("cond") and re.search(m["cond"], txt): r.append("your listed conditions may make this unsuitable")
    if m.get("alg") and re.search(m["alg"], p.get("alg","")): r.append("matches an allergy you listed")
    if m.get("med") and re.search(m["med"], p.get("meds","")): r.append("may interact with a medicine you take")
    if m.get("age") and age is not None and m["age"](age): r.append("age needs extra care")
    if mid=="ibuprofen" and p["syms"] & {"vomit","dry"}: r.append("avoid when vomiting or dehydrated")
    return r

def assess(p):
    """Full pipeline. Emergency layer is decided first and cannot be overridden."""
    p = extract(p); flags = redflags(p); lvl, why = assess_risk(p, flags); conds = rank_conditions(p)
    names = [SYM[k] for k in sorted(p["syms"])]
    tr = {"better":"improving","same":"unchanged","worse":"getting worse"}.get(p.get("trend"),"")
    summary = (f"{p['age']}-year-old{(' '+p['sex'].lower()) if p.get('sex') else ''} reporting "
               f"{', '.join(names).lower() or 'symptoms'}" + (f" (location: {p['loc']})" if p.get("loc") else "")
               + (f", for about {p['dur']:g} day(s)" if p.get("dur") is not None else "")
               + (f", severity {p['sev']}/10" if p.get("sev") else "") + (f", {tr}" if tr else "") + ".")
    meds = list(dict.fromkeys(m for x in conds for m in x["c"]["m"]))
    care = list(dict.fromkeys(c for x in conds for c in x["c"]["care"]))[:5]
    return {"p":p,"flags":flags,"lvl":lvl,"why":why,"conds":conds,"summary":summary,"meds":meds,"care":care,
            "period":"48 to 72 hours" if lvl==0 else "24 to 48 hours","names":names}
