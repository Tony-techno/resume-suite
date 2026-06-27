content = '''from docx import Document
import io

def parse_docx(file_bytes: bytes) -> str:
    try:
        doc = Document(io.BytesIO(file_bytes))
        lines = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        lines.append(cell.text.strip())
        return "\\n".join(lines)
    except Exception as e:
        raise ValueError(f"DOCX parsing failed: {e}")
'''

with open("utils/docx_parser.py", "w", encoding="utf-8") as f:
    f.write(content)
print("docx_parser.py written OK")