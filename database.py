import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

# Define the database file path
DATABASE_URL = "sqlite:///./analysis_results.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# Define the database models
class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    celery_task_id = Column(String, index=True, nullable=True)
    status = Column(String, default="PENDING")
    query = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    result = relationship("AnalysisResult", back_populates="request", uselist=False)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, ForeignKey("analysis_requests.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    request = relationship("AnalysisRequest", back_populates="result")

# Function to create the database tables
def create_db_and_tables():
    # In a real application, you might use Alembic for migrations
    Base.metadata.create_all(bind=engine)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating database and tables...")
    create_db_and_tables()
    print("Database and tables created successfully.") 