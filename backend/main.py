import os
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .models import Project, RetroAnalysis
from .scheduler import start_scheduler
from .funding_engine import fetch_defillama
from .llm_engine import deep_analyze
from .ranking_engine import calculate_score
from .sybil_engine import classify_sybil

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.get("/api/debug-count")
def debug_count(db: Session = Depends(get_db)):
    return {
        "projects": db.query(Project).count(),
        "analysis": db.query(RetroAnalysis).count()
    }

@app.post("/api/manual-scan")
def manual_scan(db: Session = Depends(get_db)):

    projects = fetch_defillama(limit=10)
    results = []

    for p in projects:

        if not is_candidate(p):
            continue

        if p["has_token"] and p["funding"] < 50000000:
            continue

        text = f"{p['name']} {p['chain']} funding:{p['funding']}"

        try:
            data = deep_analyze(text)
        except Exception as e:
            print("LLM ERROR:", e)
            continue

        score = calculate_score(data, p["funding"], p["chain"])
        sybil_risk = classify_sybil(data)

        project = Project(
            name=p["name"],
            chain=p["chain"],
            funding=p["funding"],
            has_token=p["has_token"]
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        analysis = RetroAnalysis(
            project_id=project.id,
            retro_probability=data["retro_probability"],
            snapshot_likelihood=data["snapshot_likelihood"],
            funding_tier=data["funding_tier"],
            effort_level=data["effort_level"],
            sybil_strength=data["sybil_strength"],
            capital_required=data["capital_required"],
            deep_score=score,
            sybil_risk=sybil_risk,
            strategy=data["strategy"]
        )

        db.add(analysis)
        db.commit()

        results.append({"name": p["name"], "score": score})

    return results

@app.get("/api/top")
def top(db: Session = Depends(get_db)):

    rows = db.query(Project, RetroAnalysis).join(
        RetroAnalysis, Project.id == RetroAnalysis.project_id
    ).order_by(RetroAnalysis.deep_score.desc()).limit(20).all()

    return [
        {
            "name": p.name,
            "chain": p.chain,
            "funding": p.funding,
            "score": a.deep_score,
            "retro_probability": a.retro_probability,
            "capital_required": a.capital_required,
            "sybil_risk": a.sybil_risk
        }
        for p, a in rows
    ]

@app.get("/api/health")
def health():
    return {"status": "running"}

# ===== Serve Frontend =====

frontend_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "frontend",
    "dist"
)

if os.path.exists(frontend_path):

    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(frontend_path, "assets")),
        name="assets"
    )

    @app.get("/")
    def serve_root():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        if full_path.startswith("api"):
            return {"detail": "API route not found"}
        return FileResponse(os.path.join(frontend_path, "index.html"))