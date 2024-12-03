# create_db.py
from .info import engine, Base
from code_matrix.app.models import Project, Module, File, Relation

def create_database():
    print("Creating the database...")
    Base.metadata.create_all(bind=engine)
    print("Database created successfully!")

if __name__ == "__main__":
    create_database()
