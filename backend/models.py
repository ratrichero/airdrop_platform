from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime
from .database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    source = Column(String)
    url = Column(String)
    chain = Column(String)
    funding = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer)
    legitimacy = Column(Integer)
    complexity = Column(Integer)
    capital = Column(Float)
    risk = Column(String)
    strategy = Column(Text)
    final_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)