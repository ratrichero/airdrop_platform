from apscheduler.schedulers.background import BackgroundScheduler
from funding_engine import fetch_defillama
from llm_engine import deep_analyze
from ranking_engine import calculate_score
from sybil_engine import classify_sybil
from database import SessionLocal
from models import Project, RetroAnalysis

def auto_scan():

    db = SessionLocal()
    projects = fetch_defillama(limit=15)

    for p in projects:

        if p["has_token"]:
            continue

        text = f"{p['name']} {p['chain']} funding:{p['funding']}"

        try:
            data = deep_analyze(text)
        except:
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

    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(auto_scan, "interval", hours=6)
    scheduler.start()