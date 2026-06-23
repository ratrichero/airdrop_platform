from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import Project, RetroAnalysis
from .funding_engine import fetch_defillama_projects
from .llm_provider import deep_analyze
from .ranking_engine import calculate_deep_score

Base.metadata.drop_all(bind=engine)   # reset clean
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/scan/funding")
def scan_funding(db: Session = Depends(get_db)):

    projects = fetch_defillama_projects()
    results = []

    for p in projects:
        if p["has_token"]:
            continue

        text = f"{p['name']} {p['chain']} funding:{p['funding']}"
        data = deep_analyze(text)

        score = calculate_deep_score(data, p["funding"], p["chain"])

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
            strategy=data["strategy"]
        )

        db.add(analysis)
        db.commit()

        results.append({
            "name": p["name"],
            "score": score
        })

    return results


@app.get("/api/top")
def top_projects(db: Session = Depends(get_db)):
    rows = db.query(Project, RetroAnalysis).join(
        RetroAnalysis, Project.id == RetroAnalysis.project_id
    ).order_by(RetroAnalysis.deep_score.desc()).limit(20).all()

    return [
        {
            "name": project.name,
            "chain": project.chain,
            "funding": project.funding,
            "score": analysis.deep_score,
            "retro_probability": analysis.retro_probability,
            "capital_required": analysis.capital_required
        }
        for project, analysis in rows
    ]