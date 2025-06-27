"""
Database initialization script
"""

from src.database.connection import engine
from src.database.models import Base

def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized.") 