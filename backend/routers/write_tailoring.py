content = '''from fastapi import APIRouter
from pydantic import BaseModel
from utils.hf_client import hf_generate, tailor_prompt
from utils.nlp_engine import extract_experience_bullets, split_sections, ACTION_VERBS, TECH_SKILLS
import re

router = APIRouter()

class TailorRequest(BaseModel):
    resume_text: str
    job_description: str

def rule_based_tailor(resume_text: str, jd: str) -> dict:
    sections = split_sections(resume_text)
    bullets  = extract_experience_bullets(sections.get("experience", resume_text))
    jd_lower = jd.lower()
    suggestions = []
    for b in bullets[:8]:
        bl = b.lower()
        missing_kws = [s for s in TECH_SKILLS if s in jd_lower and s not in bl][:3]
        first_word  = bl.split()[0] if bl else ""
        is_weak     = first_word in ACTION_VERBS["weak"]
        suggestions.append({
            "original": b,
            "suggestion": f"Consider adding: {', '.join(missing_kws)}" if missing_kws else "Quantify this bullet with a number or percentage.",
            "is_weak_verb": is_weak,
        })
    resume_lower  = resume_text.lower()
    skills_to_add = [s for s in TECH_SKILLS if s in jd_lower and s not in resume_lower][:8]
    return {"mode": "rule_based", "suggestions": suggestions, "skills_to_add": skills_to_add}

@router.post("/")
async def tailor(req: TailorRequest):
    prompt = tailor_prompt(req.resume_text, req.job_description)
    result = await hf_generate(prompt)
    if result == "__MODEL_LOADING__":
        rb = rule_based_tailor(req.resume_text, req.job_description)
        rb["notice"] = "AI model warming up. Showing rule-based suggestions - retry in 20 seconds."
        return rb
    if result:
        lines = [l.strip() for l in result.split("\\n") if l.strip().startswith("-")]
        return {"mode": "ai", "rewritten_bullets": lines, "raw": result}
    rb = rule_based_tailor(req.resume_text, req.job_description)
    rb["notice"] = "Add HF_TOKEN to .env to enable AI rewrites. Showing rule-based analysis."
    return rb
'''

with open("routers/tailoring.py", "w", encoding="utf-8") as f:
    f.write(content)
print("routers/tailoring.py written OK")