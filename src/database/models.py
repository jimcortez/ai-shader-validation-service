"""
SQLAlchemy database models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Shader(Base):
    __tablename__ = "shaders"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=True)
    format = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    validation_results = relationship("ValidationResult", back_populates="shader")
    analysis_results = relationship("AnalysisResult", back_populates="shader")
    generated_images = relationship("GeneratedImage", back_populates="shader")

class ValidationRecord(Base):
    """Model for storing validation records."""
    __tablename__ = "validation_records"
    id = Column(String, primary_key=True, default=generate_uuid)
    format = Column(String, nullable=False)
    target_version = Column(String, nullable=True)
    target_platforms = Column(String, nullable=True)
    is_valid = Column(Boolean, nullable=True)
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    quality_score = Column(Float, nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    user_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ValidationHistory(Base):
    """Model for storing validation history."""
    __tablename__ = "validation_history"
    id = Column(String, primary_key=True, default=generate_uuid)
    validation_id = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    format = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ValidationResult(Base):
    __tablename__ = "validation_results"
    id = Column(String, primary_key=True, default=generate_uuid)
    shader_id = Column(String, ForeignKey("shaders.id"), nullable=False)
    status = Column(String, nullable=False)
    errors = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    info = Column(JSON, nullable=True)
    performance_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    suggestions = Column(JSON, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    shader = relationship("Shader", back_populates="validation_results")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(String, primary_key=True, default=generate_uuid)
    shader_id = Column(String, ForeignKey("shaders.id"), nullable=False)
    analysis_types = Column(JSON, nullable=True)
    syntax_analysis = Column(JSON, nullable=True)
    semantic_analysis = Column(JSON, nullable=True)
    performance_analysis = Column(JSON, nullable=True)
    security_analysis = Column(JSON, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    shader = relationship("Shader", back_populates="analysis_results")

class GeneratedImage(Base):
    __tablename__ = "generated_images"
    id = Column(String, primary_key=True, default=generate_uuid)
    shader_id = Column(String, ForeignKey("shaders.id"), nullable=False)
    image_url = Column(String, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    format = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    shader = relationship("Shader", back_populates="generated_images") 