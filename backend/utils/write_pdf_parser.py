content = '''from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import io

def parse_pdf(file_bytes: bytes) -> str:
    try:
        laparams = LAParams(line_margin=0.5, word_margin=0.1)
        return extract_text(io.BytesIO(file_bytes), laparams=laparams).strip()
    except Exception as e:
        raise ValueError(f"PDF parsing failed: {e}")
'''

with open("utils/pdf_parser.py", "w", encoding="utf-8") as f:
    f.write(content)
print("pdf_parser.py written OK")