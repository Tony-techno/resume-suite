from fastapi import APIRouter
from pydantic import BaseModel
from routers.ats_scorer import extract_jd_keywords
import re

router = APIRouter()

class KWRequest(BaseModel):
    resume_text: str
    job_description: str

def classify(kw, resume_lower):
    if re.search(r"\b" + re.escape(kw) + r"\b", resume_lower): return "matched"
    if len(kw) > 4 and kw[:4] in resume_lower: return "partial"
    return "missing"

def suggest_section(kw):
    tech = ["python","java","react","sql","aws","docker","linux","git","api","node","css","html"]
    if any(t in kw for t in tech): return "skills"
    if any(s in kw for s in ["lead","manage","communicat","team"]): return "summary"
    return "experience"

@router.post("/analyze")
async def analyze(req: KWRequest):
    rl  = req.resume_text.lower()
    kws = extract_jd_keywords(req.job_description)
    results, stats = [], {"matched":0,"partial":0,"missing":0}
    for kw in kws[:60]:
        status = classify(kw, rl)
        stats[status] += 1
        r = {"keyword": kw, "status": status}
        if status != "matched": r["add_to"] = suggest_section(kw)
        results.append(r)
    total = len(results) or 1
    return {
        "keywords":         results,
        "stats":            stats,
        "match_percentage": int(stats["matched"]/total*100),
        "top_missing":      [r["keyword"] for r in results if r["status"]=="missing"][:15],
        "top_matched":      [r["keyword"] for r in results if r["status"]=="matched"][:15],
    }
