"""Quick safety tests. Run: python test_engine.py"""
import engine as E
def P(**k):
    b = dict(desc="", syms=set(), age=30, sex="", loc="", sev=0, dur=None, trend="", cond="", meds="", alg="", hist="", temp=None, hr=None, spo=None, sbp=None, glu=None); b.update(k); return b
r = E.assess(P(desc="I have had a headache for two days with fever and weakness.", temp=38.6, sev=5)); assert r["lvl"] in (1,2) and r["conds"], r["lvl"]
assert E.assess(P(syms={"chest","sob"}, age=55))["lvl"] == 3
assert E.assess(P(desc="I can't breathe", age=30))["lvl"] == 3
assert E.assess(P(syms={"neck","fever","headache"}))["lvl"] == 3
assert E.assess(P(syms={"cough"}, spo=88))["lvl"] == 3
assert E.assess(P(desc="slurred speech", syms={"weak"}))["lvl"] == 3
assert E.assess(P(syms={"runny","sore"}, sev=1))["lvl"] == 0
assert E.validate(P(syms={"fever"}, temp=99))[0] and E.validate(P(age=None, syms={"fever"}))[0] and E.validate(P())[0]
assert E.med_check("ibuprofen", P(syms={"fever"}, meds="warfarin", cond="asthma"))
print("All safety tests passed")
