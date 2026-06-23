from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    chain = Column(String)
    funding = Column(Float)
    has_token = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("RetroAnalysis", back_populates="project")


class RetroAnalysis(Base):
    __tablename__ = "retro_analysis"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))

    retro_probability = Column(Float)
    snapshot_likelihood = Column(Float)
    funding_tier = Column(Integer)
    effort_level = Column(Integer)
    sybil_strength = Column(Integer)
    capital_required = Column(Float)
    deep_score = Column(Float)
    strategy = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="analysis")