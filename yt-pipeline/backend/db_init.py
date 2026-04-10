"""
Standalone script to create all database tables.
Run from the /backend directory: python db_init.py
"""
from app.database import Base, engine
from app.models.job import Job  # noqa: F401 — registers model with Base

Base.metadata.create_all(bind=engine)
print("Database tables created successfully.")
