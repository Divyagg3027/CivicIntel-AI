"""
Demonstration Data Seeding Script for CivicIntel AI
Reads demonstration CSV files (population, infrastructure, investment) and seeds MySQL database.
Also seeds representative multilingual demonstration citizen requests if needed.
Idempotent: Avoids duplicate records and can be safely executed repeatedly.
"""

import os
import sys
import csv
from pathlib import Path

# Add backend directory to Python path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
DATA_DIR = PROJECT_ROOT / "data"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import database
import models
from services.analysis_service import analyze_request_data


def seed_population(db):
    pop_file = DATA_DIR / "population.csv"
    if not pop_file.exists():
        print(f"⚠️ {pop_file} not found. Skipping population seeding.")
        return

    print("🌱 Seeding population dataset...")
    with open(pop_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(row for row in f if not row.startswith("#"))
        for row in reader:
            loc = row["location"].strip()
            pop = int(row["population"].strip())

            existing = db.query(models.PopulationData).filter(models.PopulationData.location == loc).first()
            if existing:
                existing.population = pop
            else:
                db.add(models.PopulationData(location=loc, population=pop))
    db.commit()
    print("✅ Population data seeded successfully.")


def seed_infrastructure(db):
    infra_file = DATA_DIR / "infrastructure.csv"
    if not infra_file.exists():
        print(f"⚠️ {infra_file} not found. Skipping infrastructure seeding.")
        return

    print("🌱 Seeding infrastructure dataset...")
    with open(infra_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(row for row in f if not row.startswith("#"))
        for row in reader:
            loc = row["location"].strip()
            cat = row["category"].strip()
            score = float(row["infrastructure_score"].strip())
            avail = row.get("availability", "").strip()
            cap = row.get("capacity", "").strip()

            existing = (
                db.query(models.InfrastructureData)
                .filter(models.InfrastructureData.location == loc, models.InfrastructureData.category == cat)
                .first()
            )
            if existing:
                existing.infrastructure_score = score
                existing.availability = avail
                existing.capacity = cap
            else:
                db.add(models.InfrastructureData(
                    location=loc,
                    category=cat,
                    infrastructure_score=score,
                    availability=avail,
                    capacity=cap
                ))
    db.commit()
    print("✅ Infrastructure data seeded successfully.")


def seed_investment(db):
    inv_file = DATA_DIR / "investment.csv"
    if not inv_file.exists():
        print(f"⚠️ {inv_file} not found. Skipping investment seeding.")
        return

    print("🌱 Seeding investment dataset...")
    with open(inv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(row for row in f if not row.startswith("#"))
        for row in reader:
            loc = row["location"].strip()
            cat = row["category"].strip()
            amt = float(row["investment_amount"].strip())
            cnt = int(row.get("project_count", 1))
            yr = int(row.get("year", 2024))

            existing = (
                db.query(models.InvestmentData)
                .filter(models.InvestmentData.location == loc, models.InvestmentData.category == cat, models.InvestmentData.year == yr)
                .first()
            )
            if existing:
                existing.investment_amount = amt
                existing.project_count = cnt
            else:
                db.add(models.InvestmentData(
                    location=loc,
                    category=cat,
                    investment_amount=amt,
                    project_count=cnt,
                    year=yr
                ))
    db.commit()
    print("✅ Investment data seeded successfully.")


DEMO_CITIZEN_REQUESTS = [
    # English
    {"text": "There is no drinking water in our village. Around 500 people are affected.", "location": "Nagercoil"},
    {"text": "Many potholes have damaged our road and around 200 residents are affected.", "location": "Coimbatore"},
    {"text": "Frequent power outages in our ward affecting 350 families every evening.", "location": "Madurai"},
    {"text": "The primary healthcare centre has no doctor or emergency medicine for 800 villagers.", "location": "Tirunelveli"},
    {"text": "Severe open drainage overflow posing dangerous health risks to 400 households.", "location": "Salem"},
    {"text": "Garbage has not been collected for three weeks, affecting nearly 600 residents.", "location": "Trichy"},
    {"text": "Bus frequency is critically low during peak hours, affecting over 1200 daily commuters.", "location": "Chennai"},
    {"text": "Contaminated drinking water supply causing acute illness among 250 residents.", "location": "Thoothukudi"},
    {"text": "Primary school roof has collapsed after rains, urgent repair needed for 180 students.", "location": "Nagercoil"},
    {"text": "Street lights broken on the main junction, dangerous accident zone for 500 pedestrians.", "location": "Coimbatore"},
    # Tamil
    {"text": "எங்கள் பகுதியில் குடிநீர் இல்லை. 500 மக்கள் பாதிக்கப்பட்டுள்ளனர்.", "location": "Madurai"},
    {"text": "சாலை மிகவும் மோசமாக சேதமடைந்துள்ளது, 300 குடும்பங்கள் அவதிப்படுகின்றனர்.", "location": "Nagercoil"},
    {"text": "தினசரி மின்தடை பிரச்சனை காரணமாக 450 பேர் பாதிக்கப்பட்டுள்ளனர்.", "location": "Tirunelveli"},
    {"text": "குப்பைகள் நீண்ட நாட்களாக அகற்றப்படவில்லை, சுமார் 350 குடியிருப்புவாசிகள் அவதி.", "location": "Trichy"},
    # Hindi
    {"text": "हमारे क्षेत्र में पीने के पानी की भारी कमी है, लगभग 400 लोग प्रभावित हैं।", "location": "Chennai"},
    {"text": "सड़क पर गहरे गड्ढे हैं जिससे 250 नागरिकों को भारी परेशानी हो रही है।", "location": "Salem"},
    # Telugu
    {"text": "మా కాలనీలో మంచి నీరు రావడం లేదు, దాదాపు 300 మంది ప్రజలు ఇబ్బంది పడుతున్నారు.", "location": "Coimbatore"},
]


def seed_demo_requests(db):
    print("🌱 Checking and seeding representative multilingual demonstration requests...")
    count_existing = db.query(models.CitizenRequest).count()
    if count_existing >= 25:
        print(f"ℹ️ {count_existing} requests already present in database. Ensuring missing demo samples are added safely.")

    for req in DEMO_CITIZEN_REQUESTS:
        txt = req["text"].strip()
        loc = req["location"].strip()

        # Check if identical request text already exists
        exists = db.query(models.CitizenRequest).filter(models.CitizenRequest.request_text == txt).first()
        if not exists:
            analysis = analyze_request_data(txt, loc)
            new_r = models.CitizenRequest(
                request_text=txt,
                location=loc,
                latitude=analysis.get("latitude"),
                longitude=analysis.get("longitude"),
                language=analysis.get("language", "English"),
                category=analysis.get("category", "Other"),
                severity=analysis.get("severity", "Low"),
                affected_people=analysis.get("affected_people", 0),
                detected_need=analysis.get("detected_need", "Civic Support & Services"),
                status="Analyzed"
            )
            db.add(new_r)

    db.commit()
    total_now = db.query(models.CitizenRequest).count()
    print(f"✅ Citizen requests verified. Total records in database: {total_now}")


def main():
    print("🚀 Initializing CivicIntel AI database tables and demonstration data...")
    # Ensure all tables exist
    models.Base.metadata.create_all(bind=database.engine)

    db = database.SessionLocal()
    try:
        seed_population(db)
        seed_infrastructure(db)
        seed_investment(db)
        seed_demo_requests(db)
        print("🎉 Seeding completed successfully without errors!")
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    main()
