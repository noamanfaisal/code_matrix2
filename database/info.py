# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from code_matrix.settings import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)  # Logs SQL queries
SessionLocal = sessionmaker(bind=engine)
