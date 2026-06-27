content = '''from fastapi import APIRouter
from pydantic import BaseModel
from utils.hf_client import hf_generate, cover_letter_prompt
from utils.nlp_engine import extract_skills
from typing import Optional

router = APIRouter()

class CLRequest(BaseModel):
    resume_text: str
    job_description: str
    name: Optional[str] = "the applicant"
    company: Optional[str] = "the company"
    role: Optional[str] = "this position"

def rule_based_letter(name, company, role, resume_text, jd) -> str:
    skills = extract_skills(resume_text)[:5]
    skills_line = f"My core competencies include {', '.join(skills)}, which align directly with your requirements." if skills else ""
    return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {role} position at {company}. With my background and passion for delivering results, I am confident I would be a valuable addition to your team.

{skills_line} Throughout my career, I have consistently focused on building practical skills and delivering measurable impact. I am excited by {company}\'s work and would welcome the opportunity to contribute to your team\'s success.

I would welcome the chance to discuss how my experience aligns with your needs. Thank you for considering my application.

Sincerely,
{name}"""

@router.post("/generate")
async def generate(req: CLRequest):
    prompt = cover_letter_prompt(req.resume_text, req.job_description, req.name, req.company, req.role)
    result = await hf_generate(prompt, max_tokens=400)
    if result == "__MODEL_LOADING__":
        return {
            "mode": "rule_based",
            "content": rule_based_letter(req.name, req.company, req.role, req.resume_text, req.job_description),
            "notice": "AI model warming up. Showing template - retry in 20 seconds for AI version.",
        }
    if result:
        return {"mode": "ai", "content": result}
    return {
        "mode": "rule_based",
        "content": rule_based_letter(req.name, req.company, req.role, req.resume_text, req.job_description),
        "notice": "Add HF_TOKEN to .env for AI-generated letters.",
    }
'''

with open("routers/cover_letter.py", "w", encoding="utf-8") as f:
    f.write(content)
print("routers/cover_letter.py written OK")