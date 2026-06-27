from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.pdf_parser import parse_pdf
from utils.docx_parser import parse_docx
from utils.nlp_engine import parse_resume

router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    fn = file.filename.lower()
    if fn.endswith(".pdf"):
        text = parse_pdf(content)
    elif fn.endswith(".docx"):
        text = parse_docx(content)
    elif fn.endswith(".txt"):
        text = content.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(400, "Unsupported file. Use PDF, DOCX, or TXT.")
    if not text.strip():
        raise HTTPException(400, "Could not extract text from file.")
    result = parse_resume(text)
    result["raw_text"] = text[:5000]
    return result

@router.post("/parse-text")
async def parse_text(payload: dict):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(400, "No text provided")
    result = parse_resume(text)
    result["raw_text"] = text[:5000]
    return result
