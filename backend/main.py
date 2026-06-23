import json
import csv
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import Project, Analysis
from .scanner import scrape_url
from .llm_provider import analyze_text
from .scoring import calculate_score
from .funding import fetch_defillama_protocols

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/scan")
def scan(url: str, db: Session = Depends(get_db)):
    text = scrape_url(url)
    data = analyze_text(text)

    score = calculate_score(data["legitimacy"], data["complexity"], data["capital"])

    project = Project(name=url, source="manual", url=url, chain="unknown", funding=0)
    db.add(project)
    db.commit()
    db.refresh(project)

    analysis = Analysis(
        project_id=project.id,
        legitimacy=data["legitimacy"],
        complexity=data["complexity"],
        capital=data["capital"],
        risk=data["risk"],
        strategy=data["strategy"],
        final_score=score
    )
    db.add(analysis)
    db.commit()

    return {"score": score, "data": data}

@app.post("/scan/funding")
def scan_funding(db: Session = Depends(get_db)):
    projects = fetch_defillama_protocols()
    results = []

    for p in projects:
        text = f"{p['name']} {p['chain']} {p['funding']}"
        data = analyze_text(text)
        score = calculate_score(data["legitimacy"], data["complexity"], data["capital"])

        project = Project(name=p["name"], source="funding", url=p["url"], chain=p["chain"], funding=p["funding"])
        db.add(project)
        db.commit()
        db.refresh(project)

        analysis = Analysis(
            project_id=project.id,
            legitimacy=data["legitimacy"],
            complexity=data["complexity"],
            capital=data["capital"],
            risk=data["risk"],
            strategy=data["strategy"],
            final_score=score
        )
        db.add(analysis)
        db.commit()

        results.append({"name": p["name"], "score": score})

    return results

@app.get("/projects")
def list_projects(chain: str = None, db: Session = Depends(get_db)):
    query = db.query(Project)
    if chain:
        query = query.filter(Project.chain == chain)
    return query.all()

@app.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    rows = db.query(Project, Analysis).join(Analysis, Project.id == Analysis.project_id).all()

    def generate():
        yield "name,chain,funding,legitimacy,complexity,capital,risk,score,strategy\n"
        for project, analysis in rows:
            yield f"{project.name},{project.chain},{project.funding},{analysis.legitimacy},{analysis.complexity},{analysis.capital},{analysis.risk},{analysis.final_score},{analysis.strategy}\n"

    return StreamingResponse(generate(), media_type="text/csv")