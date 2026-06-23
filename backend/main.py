from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import Project, RetroAnalysis
from engine import apply_decay
from scheduler import start_scheduler

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
            "score": apply_decay(a.deep_score, a.created_at),
            "retro_probability": a.retro_probability,
            "capital_required": a.capital_required
        }
        for p, a in rows
    ]

@app.get("/api/health")
def health():
    return {"status": "running"}

from engine import fetch_defillama, calculate_score
from llm import deep_analyze
from models import Project, RetroAnalysis

@app.post("/api/manual-scan")
def manual_scan(db: Session = Depends(get_db)):

    projects = fetch_defillama(limit=10)
    results = []

    for p in projects:

        has_token = bool(p.get("symbol"))
        if has_token:
            continue

        text = f"{p.get('name')} {p.get('chain')} funding:{p.get('tvl',0)}"

        try:
            data = deep_analyze(text)
        except:
            continue

        score = calculate_score(data, p.get("tvl",0), p.get("chain","Unknown"))

        project = Project(
            name=p.get("name"),
            chain=p.get("chain","Unknown"),
            funding=p.get("tvl",0),
            has_token=has_token
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
            strategy=data["strategy"]
        )

        db.add(analysis)
        db.commit()

        results.append({
            "name": p.get("name"),
            "score": score
        })

    return {
        "scanned": len(results),
        "results": results
    }