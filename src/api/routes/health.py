"""
Health check endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database.connection import get_db

router = APIRouter()

@router.get("/health/db", tags=["health"])
async def db_health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to check DB connection
        db.execute(text("SELECT 1"))
        return {"database": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {e}") 