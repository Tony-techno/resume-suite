from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models.database import init_db
from routers import parser, ats_scorer, keyword_gap, tailoring, cover_letter, versions

load_dotenv()

app = FastAPI(title="Resume Intelligence Suite API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(parser.router,       prefix="/api/parser",       tags=["Parser"])
app.include_router(ats_scorer.router,   prefix="/api/ats",          tags=["ATS"])
app.include_router(keyword_gap.router,  prefix="/api/keywords",     tags=["Keywords"])
app.include_router(tailoring.router,    prefix="/api/tailor",       tags=["Tailoring"])
app.include_router(cover_letter.router, prefix="/api/cover-letter", tags=["Cover Letter"])
app.include_router(versions.router,     prefix="/api/versions",     tags=["Versions"])

@app.get("/")
def root():
    return {"status": "Resume Intelligence Suite running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}