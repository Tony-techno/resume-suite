content = '''import os
import httpx
from typing import Optional

HF_URL   = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_TOKEN = os.getenv("HF_TOKEN", "")

async def hf_generate(prompt: str, max_tokens: int = 512) -> Optional[str]:
    if not HF_TOKEN:
        return None
    try:
        async with httpx.AsyncClient(timeout=45) as c:
            r = await c.post(HF_URL,
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json={"inputs": prompt,
                      "parameters": {"max_new_tokens": max_tokens, "temperature": 0.7,
                                     "do_sample": True, "return_full_text": False}})
            if r.status_code == 200:
                d = r.json()
                return d[0].get("generated_text","").strip() if isinstance(d,list) and d else None
            if r.status_code == 503:
                return "__MODEL_LOADING__"
    except Exception:
        pass
    return None

def tailor_prompt(resume: str, jd: str) -> str:
    return f"""[INST] You are a professional resume writer. Rewrite the experience bullets below to match the job description. Use strong action verbs, quantify impact. Return ONLY bullet points starting with a dash (-).

JOB DESCRIPTION:
{jd[:1500]}

CURRENT EXPERIENCE BULLETS:
{resume[:1500]}

6 rewritten tailored bullet points: [/INST]"""

def cover_letter_prompt(resume: str, jd: str, name: str, company: str, role: str) -> str:
    return f"""[INST] Write a concise 3-paragraph professional cover letter for {name} applying for {role} at {company}. No address headers. Sound human and specific.

JOB DESCRIPTION:
{jd[:1000]}

RESUME SUMMARY:
{resume[:800]}

Cover letter: [/INST]"""
'''

with open("utils/hf_client.py", "w", encoding="utf-8") as f:
    f.write(content)
print("hf_client.py written OK")