content = '''from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.database import get_db
from typing import Optional
import json

router = APIRouter()

class VersionSave(BaseModel):
    name: str
    label: Optional[str] = ""
    content_text: Optional[str] = ""
    structured_json: Optional[dict] = None
    ats_score: Optional[int] = None

@router.get("/")
def list_versions():
    db = get_db()
    rows = db.execute("SELECT id,name,label,ats_score,created_at FROM resume_versions ORDER BY created_at DESC").fetchall()
    db.close()
    return [dict(r) for r in rows]

@router.post("/")
def save_version(v: VersionSave):
    db = get_db()
    cur = db.execute(
        "INSERT INTO resume_versions (name,label,content_text,structured_json,ats_score) VALUES (?,?,?,?,?)",
        (v.name, v.label, v.content_text, json.dumps(v.structured_json) if v.structured_json else None, v.ats_score)
    )
    db.commit()
    new_id = cur.lastrowid
    db.close()
    return {"id": new_id, "message": "Version saved"}

@router.get("/compare/{id1}/{id2}")
def compare(id1: int, id2: int):
    db = get_db()
    r1 = db.execute("SELECT * FROM resume_versions WHERE id=?", (id1,)).fetchone()
    r2 = db.execute("SELECT * FROM resume_versions WHERE id=?", (id2,)).fetchone()
    db.close()
    if not r1 or not r2: raise HTTPException(404, "One or both versions not found")
    def parse(r):
        d = dict(r)
        if d.get("structured_json"):
            try: d["structured_json"] = json.loads(d["structured_json"])
            except: pass
        return d
    return {"version1": parse(r1), "version2": parse(r2)}

@router.get("/{version_id}")
def get_version(version_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM resume_versions WHERE id=?", (version_id,)).fetchone()
    db.close()
    if not row: raise HTTPException(404, "Version not found")
    r = dict(row)
    if r.get("structured_json"):
        try: r["structured_json"] = json.loads(r["structured_json"])
        except: pass
    return r

@router.delete("/{version_id}")
def delete_version(version_id: int):
    db = get_db()
    db.execute("DELETE FROM resume_versions WHERE id=?", (version_id,))
    db.commit()
    db.close()
    return {"message": "Deleted"}
'''

with open("routers/versions.py", "w", encoding="utf-8") as f:
    f.write(content)
print("routers/versions.py written OK")