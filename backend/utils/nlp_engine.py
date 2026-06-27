import re
from typing import Optional

EMAIL_RE    = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}")
PHONE_RE    = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.I)
GITHUB_RE   = re.compile(r"github\.com/[\w\-]+", re.I)

SECTION_HEADERS = {
    "summary":        ["summary","objective","profile","about","overview","professional summary"],
    "experience":     ["experience","work experience","employment","work history","professional experience"],
    "education":      ["education","academic","qualification","degree","university","college"],
    "skills":         ["skills","technical skills","core competencies","technologies","tools"],
    "projects":       ["projects","personal projects","key projects","portfolio"],
    "certifications": ["certifications","certificates","awards","achievements","licenses"],
}

ACTION_VERBS = {
    "strong": ["achieved","built","created","designed","developed","drove","engineered",
               "established","exceeded","generated","grew","improved","increased","launched",
               "led","optimized","pioneered","reduced","saved","scaled","spearheaded",
               "streamlined","transformed","delivered","automated","architected","deployed"],
    "medium": ["analyzed","collaborated","completed","conducted","contributed","coordinated",
               "executed","facilitated","implemented","maintained","managed","mentored",
               "monitored","performed","provided","researched","resolved","reviewed",
               "supported","tested","worked"],
    "weak":   ["helped","assisted","tried","attempted","did","was responsible for","responsible for"],
}

TECH_SKILLS = [
    "python","java","javascript","typescript","c++","c#","go","rust","swift","kotlin",
    "php","ruby","scala","r","matlab","sql","bash","shell","react","angular","vue",
    "nextjs","nodejs","express","django","flask","fastapi","html","css","tailwind",
    "bootstrap","graphql","rest","api","tensorflow","pytorch","scikit-learn","pandas",
    "numpy","spark","kafka","machine learning","deep learning","nlp","computer vision",
    "aws","azure","gcp","docker","kubernetes","ci/cd","git","github","gitlab","jenkins",
    "terraform","linux","ubuntu","mysql","postgresql","mongodb","redis","elasticsearch",
    "sqlite","oracle","agile","scrum","jira","figma","tableau","power bi",
]

def extract_name(text):
    for line in text.split("\n")[:6]:
        line = line.strip()
        if line and 2 <= len(line.split()) <= 4 and not any(c in line for c in ["@",":","/"," +","|"]):
            if not any(kw in line.lower() for kw in ["resume","curriculum","vitae","phone","email"]):
                return line
    return None

def extract_contact(text):
    emails    = EMAIL_RE.findall(text)
    phones    = PHONE_RE.findall(text)
    linkedins = LINKEDIN_RE.findall(text)
    githubs   = GITHUB_RE.findall(text)
    return {
        "email":    emails[0] if emails else None,
        "phone":    phones[0].strip() if phones else None,
        "linkedin": linkedins[0] if linkedins else None,
        "github":   githubs[0] if githubs else None,
    }

def split_sections(text):
    sections = {"raw": text, "header": []}
    current  = "header"
    for line in text.split("\n"):
        s = line.strip().lower()
        matched = False
        for key, kws in SECTION_HEADERS.items():
            if any(s == kw or s.startswith(kw) for kw in kws):
                current = key
                sections.setdefault(key, [])
                matched = True
                break
        if not matched:
            sections.setdefault(current, [])
            if isinstance(sections[current], list):
                sections[current].append(line)
    return {k: "\n".join(v).strip() if isinstance(v, list) else v for k, v in sections.items()}

def extract_skills(text):
    tl = text.lower()
    return list(dict.fromkeys(s for s in TECH_SKILLS if re.search(r"\b" + re.escape(s) + r"\b", tl)))

def extract_education(text):
    pat = r"(B\.?Tech|B\.?E|B\.?Sc|M\.?Tech|M\.?Sc|MBA|PhD|Bachelor|Master|Diploma|BCA|MCA)[^\n]{0,100}"
    return list(dict.fromkeys(re.findall(pat, text, re.I)))[:8]

def extract_experience_bullets(text):
    bullets = []
    for l in text.split("\n"):
        stripped = l.strip()
        if stripped and stripped[0] in "-*" and len(stripped) > 21:
            bullets.append(stripped[1:].strip())
        elif stripped and len(stripped) > 20:
            bullets.append(stripped)
    return bullets

def detect_formatting_issues(text):
    issues = []
    if re.search(r"\|{2,}", text):
        issues.append("Table layout detected - ATS may misread columns")
    if text.count("\t") > 10:
        issues.append("Heavy tabs suggest multi-column layout")
    if len([l for l in text.split("\n") if len(l) > 120]) > 5:
        issues.append("Very long lines detected - possible text boxes")
    return issues

def score_action_verbs(bullets):
    strong = medium = weak = 0
    for b in bullets:
        fw = b.strip().split()[0].lower() if b.strip() else ""
        if fw in ACTION_VERBS["strong"]:   strong += 1
        elif fw in ACTION_VERBS["weak"]:   weak   += 1
        elif fw in ACTION_VERBS["medium"]: medium += 1
    t = len(bullets) or 1
    return {"score": min(100, int((strong*3+medium*1.5)/(t*3)*100)), "strong":strong, "medium":medium, "weak":weak}

def score_quantification(bullets):
    qr = re.compile(r"\d+[\%xX]?|\$\d+|[\d,]+\s*(users|customers|projects|hours|teams|lines|records)", re.I)
    q  = sum(1 for b in bullets if qr.search(b))
    t  = len(bullets) or 1
    return {"score": min(100, int(q/t*100)), "quantified": q, "total": t}

def parse_resume(text):
    sections = split_sections(text)
    bullets  = extract_experience_bullets(sections.get("experience", ""))
    return {
        "name":                 extract_name(text),
        "contact":              extract_contact(text),
        "skills":               extract_skills(text),
        "education":            extract_education(sections.get("education", text)),
        "experience_bullets":   bullets[:20],
        "sections_found":       [k for k in SECTION_HEADERS if k in sections and sections.get(k)],
        "summary":              sections.get("summary", "")[:500],
        "projects":             sections.get("projects", "")[:1000],
        "certifications":       sections.get("certifications", "")[:500],
        "word_count":           len(text.split()),
        "action_verb_score":    score_action_verbs(bullets),
        "quantification_score": score_quantification(bullets),
        "formatting_issues":    detect_formatting_issues(text),
    }
