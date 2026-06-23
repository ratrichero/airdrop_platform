from apscheduler.schedulers.background import BackgroundScheduler
from engine import fetch_defillama, calculate_score
from llm import deep_analyze
from database import SessionLocal
from models import Project, RetroAnalysis

def auto_scan():

    db = SessionLocal()
    projects = fetch_defillama(limit=15)

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

    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(auto_scan, "interval", hours=6)
    scheduler.start()