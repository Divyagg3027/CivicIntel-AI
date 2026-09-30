from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from database import Base


class CitizenRequest(Base):
    __tablename__ = "citizen_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_text = Column(Text, nullable=False)
    location = Column(String(255), nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    language = Column(String(50), default="English", index=True)
    category = Column(String(100), default="Other", index=True)
    severity = Column(String(50), default="Low", index=True)
    affected_people = Column(Integer, default=0)
    status = Column(String(50), default="Analyzed")
    detected_need = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class PopulationData(Base):
    __tablename__ = "population_data"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(255), unique=True, nullable=False, index=True)
    population = Column(Integer, nullable=False)


class InfrastructureData(Base):
    __tablename__ = "infrastructure_data"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    infrastructure_score = Column(Float, nullable=False)  # 0 to 100
    availability = Column(String(50), nullable=True)
    capacity = Column(String(100), nullable=True)


class InvestmentData(Base):
    __tablename__ = "investment_data"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    investment_amount = Column(Float, nullable=False)
    project_count = Column(Integer, default=1)
    year = Column(Integer, default=2024)


class HotspotAnalysis(Base):
    __tablename__ = "hotspot_analysis"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(255), unique=True, nullable=False, index=True)
    civic_need_index = Column(Float, nullable=False)  # 0 to 100
    request_count = Column(Integer, nullable=False, default=0)
    affected_people = Column(Integer, nullable=False, default=0)
    severity_score = Column(Float, nullable=False, default=0.0)
    infrastructure_gap = Column(Float, nullable=False, default=0.0)
    investment_context = Column(Float, nullable=False, default=0.0)
    dominant_category = Column(String(100), nullable=True)
    explanation = Column(Text, nullable=True)
    calculated_at = Column(DateTime, default=datetime.utcnow)