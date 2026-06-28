import re
from typing import Optional

EMAIL_RE    = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}")
PHONE_RE    = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")
LINKEDIN_RE = re.compile(r"linkedin\.com(?:/in)?/[\w\-]+", re.I)
GITHUB_RE   = re.compile(r"github\.com/[\w\-]+", re.I)

SECTION_HEADERS = {
    "summary":        ["summary","objective","profile","about","overview","professional summary","career objective"],
    "experience":     ["experience","work experience","employment","work history","professional experience","internships","internship"],
    "education":      ["education","academic","qualification","degree","university","college","schooling"],
    "skills":         ["skills","technical skills","core competencies","technologies","tools","competencies","technical expertise"],
    "projects":       ["projects","personal projects","key projects","portfolio","academic projects"],
    "certifications": ["certifications","certificates","awards","achievements","licenses","honors","accomplishments","extra","extracurricular","activities"],
}

ACTION_VERBS = {
    "strong": ["achieved","built","created","designed","developed","drove","engineered",
               "established","exceeded","generated","grew","improved","increased","launched",
               "led","optimized","pioneered","reduced","saved","scaled","spearheaded",
               "streamlined","transformed","delivered","automated","architected","deployed",
               "implemented","analyzed","trained","evaluated","integrated","migrated"],
    "medium": ["collaborated","completed","conducted","contributed","coordinated","executed",
               "facilitated","maintained","managed","mentored","monitored","performed",
               "provided","researched","resolved","reviewed","supported","tested","worked",
               "assisted","prepared","presented","documented"],
    "weak":   ["helped","tried","attempted","did","was responsible for","responsible for"],
}

TECH_SKILLS = [
    "python","java","javascript","typescript","c++","c#","c","go","rust","swift","kotlin",
    "php","ruby","scala","r","matlab","sql","bash","shell","react","angular","vue",
    "nextjs","nodejs","express","django","flask","fastapi","html","css","tailwind",
    "bootstrap","graphql","rest","api","tensorflow","pytorch","scikit-learn","sklearn",
    "pandas","numpy","matplotlib","seaborn","plotly","spark","kafka","opencv",
    "machine learning","deep learning","nlp","computer vision","neural networks",
    "object detection","image processing","transfer learning","cnn","rnn","lstm",
    "aws","azure","gcp","docker","kubernetes","ci/cd","git","github","gitlab","jenkins",
    "terraform","linux","ubuntu","mysql","postgresql","mongodb","redis","elasticsearch",
    "sqlite","oracle","agile","scrum","jira","figma","tableau","power bi","excel",
    "postman","arduino","raspberry pi","jetson nano","pygame","data analysis",
    "data visualization","data cleaning","etl","business intelligence","statistics",
    "feature engineering","model evaluation","data science",
]

# Lines that look like section headers or company/role titles — not bullets
SKIP_PATTERNS = [
    re.compile(r"^(tech|technologies|tools|skills used)\s*:", re.I),
    re.compile(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}", re.I),
    re.compile(r"\d{4}\s*[-–]\s*(\d{4}|present)", re.I),
    re.compile(r"^(pvt|ltd|inc|llc|solutions|technologies|systems)", re.I),
]

def is_skip_line(line: str) -> bool:
    line = line.strip()
    if len(line) < 10: return True
    for pat in SKIP_PATTERNS:
        if pat.search(line): return True
    return False

def extract_name(text: str) -> Optional[str]:
    for line in text.split("\n")[:6]:
        line = line.strip()
        if line and 2 <= len(line.split()) <= 4 and not any(c in line for c in ["@",":","/","+","|","."]):
            if not any(kw in line.lower() for kw in ["resume","curriculum","vitae","phone","email","address"]):
                return line
    return None

def extract_contact(text: str) -> dict:
    emails    = EMAIL_RE.findall(text)
    phones    = PHONE_RE.findall(text)
    linkedins = LINKEDIN_RE.findall(text)
    githubs   = GITHUB_RE.findall(text)
    linkedin  = linkedins[0] if linkedins else None
    if not linkedin:
        for line in text.split("\n"):
            if "linkedin" in line.lower():
                match = re.search(r"[\w\-]+$", line.strip())
                if match and len(match.group()) > 3:
                    linkedin = "linkedin.com/in/" + match.group()
                    break
    return {
        "email":    emails[0] if emails else None,
        "phone":    phones[0].strip() if phones else None,
        "linkedin": linkedin,
        "github":   githubs[0] if githubs else None,
    }

def split_sections(text: str) -> dict:
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

def extract_skills(text: str) -> list:
    tl = text.lower()
    return list(dict.fromkeys(s for s in TECH_SKILLS if re.search(r"\b" + re.escape(s) + r"\b", tl)))

def extract_education(text: str) -> list:
    pat = r"(B\.?Tech|B\.?E|B\.?Sc|M\.?Tech|M\.?Sc|MBA|PhD|Bachelor|Master|Diploma|BCA|MCA|12th|10th|HSC|SSC)[^\n]{0,150}"
    return list(dict.fromkeys(re.findall(pat, text, re.I)))[:8]

def extract_experience_bullets(text: str) -> list:
    bullets = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or len(stripped) < 25:
            continue
        if is_skip_line(stripped):
            continue
        clean = re.sub(r"^[\•\-\*\→\►\✓\◆\▸\◦\·]+\s*", "", stripped).strip()
        if len(clean) < 25:
            continue
        first_word = clean.split()[0].lower() if clean.split() else ""
        all_verbs = ACTION_VERBS["strong"] + ACTION_VERBS["medium"] + ACTION_VERBS["weak"]
        if first_word in all_verbs:
            bullets.append(clean)
    return bullets[:20]

def detect_formatting_issues(text: str) -> list:
    issues = []
    if re.search(r"\|{2,}", text):
        issues.append("Table layout detected - ATS may misread columns")
    if text.count("\t") > 10:
        issues.append("Heavy tabs suggest multi-column layout")
    if len([l for l in text.split("\n") if len(l) > 120]) > 5:
        issues.append("Very long lines detected - possible text boxes")
    return issues

def score_action_verbs(bullets: list) -> dict:
    strong = medium = weak = 0
    for b in bullets:
        fw = b.strip().split()[0].lower() if b.strip() else ""
        if fw in ACTION_VERBS["strong"]:   strong += 1
        elif fw in ACTION_VERBS["weak"]:   weak   += 1
        elif fw in ACTION_VERBS["medium"]: medium += 1
    t = len(bullets) or 1
    return {"score": min(100, int((strong*3+medium*1.5)/(t*3)*100)), "strong":strong, "medium":medium, "weak":weak}

def score_quantification(bullets: list) -> dict:
    qr = re.compile(r"\d+[\%xX]?|\$\d+|[\d,]+\s*(users|customers|projects|hours|teams|lines|records|samples|images|classes|accuracy)", re.I)
    q  = sum(1 for b in bullets if qr.search(b))
    t  = len(bullets) or 1
    return {"score": min(100, int(q/t*100)), "quantified": q, "total": t}

def extract_certifications(text: str) -> list:
    certs = []
    cert_pat = re.compile(r"(hackerrank|coursera|udemy|google|aws|microsoft|oracle|cisco|comptia|ibm|linkedin learning)[^\n]{0,80}", re.I)
    for match in cert_pat.finditer(text):
        certs.append(match.group().strip())
    return certs[:10]

def parse_resume(text: str) -> dict:
    sections = split_sections(text)
    exp_text = sections.get("experience", "")
    bullets  = extract_experience_bullets(exp_text)
    certs    = extract_certifications(text)
    return {
        "name":                 extract_name(text),
        "contact":              extract_contact(text),
        "skills":               extract_skills(text),
        "education":            extract_education(sections.get("education", text)),
        "experience_bullets":   bullets,
        "sections_found":       [k for k in SECTION_HEADERS if k in sections and sections.get(k)],
        "summary":              sections.get("summary", "")[:500],
        "projects":             sections.get("projects", "")[:1000],
        "certifications":       certs,
        "word_count":           len(text.split()),
        "action_verb_score":    score_action_verbs(bullets),
        "quantification_score": score_quantification(bullets),
        "formatting_issues":    detect_formatting_issues(text),
    }
