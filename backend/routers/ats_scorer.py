from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.nlp_engine import (split_sections, extract_experience_bullets,
    detect_formatting_issues, score_action_verbs, score_quantification, SECTION_HEADERS)
import re

router = APIRouter()

class ATSRequest(BaseModel):
    resume_text: str
    job_description: str

def extract_jd_keywords(jd: str) -> list:
    stop = {"and","or","the","a","an","in","on","at","to","for","of","with","is","are","was",
            "be","will","have","has","that","this","we","you","our","your","they","it","as","by"}
    words = re.findall(r"[a-z][a-z0-9+#\-\.]{1,}", jd.lower())
    seen, out = set(), []
    for w in words:
        if w not in stop and w not in seen and len(w) > 2:
            seen.add(w); out.append(w)
    return out[:80]

def kw_score(resume, keywords):
    rl = resume.lower()
    matched = [k for k in keywords if re.search(r"\b" + re.escape(k) + r"\b", rl)]
    missing = [k for k in keywords if k not in matched]
    return min(100, int(len(matched)/max(len(keywords),1)*100)), matched, missing

def sec_score(resume):
    rl       = resume.lower()
    required = ["experience","education","skills"]
    optional = ["summary","projects","certifications"]
    found    = [s for s in required+optional if any(k in rl for k in SECTION_HEADERS.get(s,[s]))]
    missing  = [s for s in required+optional if s not in found]
    score    = int(sum(1 for s in required if s in found)/3*70 + sum(1 for s in optional if s in found)/3*30)
    return score, found, missing

def ct_score(resume):
    chk = {
        "email":    bool(re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", resume)),
        "phone":    bool(re.search(r"(\+?\d[\d\s\-().]{7,}\d)", resume)),
        "linkedin": bool(re.search(r"linkedin\.com/in/", resume, re.I)),
        "github":   bool(re.search(r"github\.com/", resume, re.I)),
    }
    return int(sum(chk.values())/4*100), chk

@router.post("/score")
async def score(req: ATSRequest):
    if not req.resume_text or not req.job_description:
        raise HTTPException(400, "Both fields required")
    sec        = split_sections(req.resume_text)
    bul        = extract_experience_bullets(sec.get("experience", req.resume_text))
    kws        = extract_jd_keywords(req.job_description)
    k,mat,mis  = kw_score(req.resume_text, kws)
    s,fnd,msec = sec_score(req.resume_text)
    fmt        = detect_formatting_issues(req.resume_text)
    f          = max(0, 100-len(fmt)*33)
    av         = score_action_verbs(bul)
    qt         = score_quantification(bul)
    ct,chk     = ct_score(req.resume_text)
    total      = int(k*0.35 + s*0.20 + f*0.15 + av["score"]*0.15 + qt["score"]*0.10 + ct*0.05)
    grade      = "A" if total>=85 else "B" if total>=70 else "C" if total>=55 else "D" if total>=40 else "F"
    recs = []
    if msec: recs.append(f"Add missing sections: {', '.join(msec)}")
    if mis:  recs.append(f"Include JD keywords: {', '.join(mis[:5])}")
    if fmt:  recs.extend(fmt)
    if av["weak"]: recs.append(f"Replace {av['weak']} weak verbs with strong action verbs")
    if qt["score"]<50: recs.append("Quantify more bullets with numbers/percentages")
    return {
        "total_score": total, "grade": grade,
        "breakdown": {
            "keyword_match":        {"score":k,          "weight":35, "matched":mat[:20], "missing":mis[:20]},
            "section_completeness": {"score":s,          "weight":20, "found":fnd, "missing":msec},
            "formatting":           {"score":f,          "weight":15, "issues":fmt},
            "action_verbs":         {"score":av["score"],"weight":15, "strong":av["strong"],"medium":av["medium"],"weak":av["weak"]},
            "quantification":       {"score":qt["score"],"weight":10, "quantified":qt["quantified"],"total":qt["total"]},
            "contact_info":         {"score":ct,         "weight":5,  "checks":chk},
        },
        "recommendations": recs,
    }
