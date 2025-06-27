"""
Validation API routes
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import uuid
import time
from datetime import datetime, timedelta

from ..models.requests import (
    ValidationRequest, BatchValidationRequest, ValidationHistoryRequest,
    ValidationStatusRequest, ValidationParameters
)
from ..models.responses import (
    ValidationResult, BatchValidationResult, ValidationHistoryResponse,
    ValidationStatusResponse, ValidationSummary, ValidationError, ErrorResponse
)
from ...services.validation_service import validation_service
from ...database.models import ValidationRecord, ValidationHistory
from ...database.connection import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

router = APIRouter(tags=["validation"])


@router.post("/validate", response_model=ValidationResult)
async def validate_shader(
    request: ValidationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Validate a single shader.
    
    This endpoint performs comprehensive validation of a shader including:
    - Syntax and semantic analysis
    - Logic flow analysis
    - Quality metrics calculation
    - Portability analysis
    - Performance analysis
    """
    start_time = time.time()
    validation_id = f"val_{uuid.uuid4().hex[:12]}"
    
    try:
        # Convert request to validation parameters
        parameters = {
            "target_version": request.target_version,
            "target_platforms": [p.value for p in request.target_platforms],
            "enable_quality_analysis": request.enable_quality_analysis,
            "enable_portability_analysis": request.enable_portability_analysis,
            "enable_performance_analysis": request.enable_performance_analysis,
            "custom_parameters": request.custom_parameters
        }
        
        # Perform validation
        validation_result = validation_service.validate(
            request.code, 
            request.format.value, 
            parameters
        )
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Create validation record
        validation_record = ValidationRecord(
            id=validation_id,
            format=request.format.value,
            target_version=request.target_version,
            target_platforms=",".join([p.value for p in request.target_platforms]),
            is_valid=validation_result["is_valid"],
            error_count=len(validation_result.get("errors", [])),
            warning_count=len(validation_result.get("warnings", [])),
            quality_score=validation_result.get("quality_metrics", {}).get("overall_score"),
            processing_time_ms=processing_time,
            created_at=datetime.utcnow()
        )
        
        # Store in database
        db.add(validation_record)
        db.commit()
        
        # Convert to response model
        response = ValidationResult(
            validation_id=validation_id,
            is_valid=validation_result["is_valid"],
            status=_determine_status(validation_result),
            format=request.format.value,
            target_version=request.target_version,
            target_platforms=[p.value for p in request.target_platforms],
            errors=_convert_errors(validation_result.get("errors", [])),
            warnings=_convert_errors(validation_result.get("warnings", [])),
            info=_convert_errors(validation_result.get("info", [])),
            quality_metrics=validation_result.get("quality_metrics"),
            performance_analysis=_create_performance_analysis(validation_result),
            portability_issues=_create_portability_issues(validation_result.get("portability_issues", [])),
            metadata=validation_result.get("metadata"),
            created_at=datetime.utcnow(),
            processing_time_ms=processing_time,
            recommendations=validation_result.get("recommendations", [])
        )
        
        return response
        
    except Exception as e:
        # Log error and return error response
        error_response = ValidationResult(
            validation_id=validation_id,
            is_valid=False,
            status="error",
            format=request.format.value,
            target_version=request.target_version,
            target_platforms=[p.value for p in request.target_platforms],
            errors=[ValidationError(
                message=f"Validation failed: {str(e)}",
                line=0,
                column=0,
                severity="error",
                error_code="VALIDATION_ERROR"
            )],
            created_at=datetime.utcnow(),
            processing_time_ms=(time.time() - start_time) * 1000
        )
        
        # Store error record
        validation_record = ValidationRecord(
            id=validation_id,
            format=request.format.value,
            target_version=request.target_version,
            target_platforms=",".join([p.value for p in request.target_platforms]),
            is_valid=False,
            error_count=1,
            warning_count=0,
            processing_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
        
        db.add(validation_record)
        db.commit()
        
        return error_response


@router.post("/validate/batch", response_model=BatchValidationResult)
async def validate_shaders_batch(
    request: BatchValidationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Validate multiple shaders in batch.
    
    This endpoint performs validation on multiple shaders, optionally using
    parallel processing for improved performance.
    """
    batch_id = request.batch_id or f"batch_{uuid.uuid4().hex[:12]}"
    start_time = time.time()
    
    try:
        # Perform batch validation
        batch_results = validation_service.validate_batch([
            {
                "id": f"shader_{i}",
                "code": shader.code,
                "format": shader.format.value,
                "parameters": {
                    "target_version": shader.target_version,
                    "target_platforms": [p.value for p in shader.target_platforms],
                    "enable_quality_analysis": shader.enable_quality_analysis,
                    "enable_portability_analysis": shader.enable_portability_analysis,
                    "enable_performance_analysis": shader.enable_performance_analysis,
                    "custom_parameters": shader.custom_parameters
                }
            }
            for i, shader in enumerate(request.shaders)
        ])
        
        # Convert to response models
        validation_results = []
        total_errors = 0
        total_warnings = 0
        quality_scores = []
        processing_times = []
        
        for i, result in enumerate(batch_results):
            validation_id = f"val_{uuid.uuid4().hex[:12]}"
            
            # Create validation record
            validation_record = ValidationRecord(
                id=validation_id,
                format=request.shaders[i].format.value,
                target_version=request.shaders[i].target_version,
                target_platforms=",".join([p.value for p in request.shaders[i].target_platforms]),
                is_valid=result["is_valid"],
                error_count=len(result.get("errors", [])),
                warning_count=len(result.get("warnings", [])),
                quality_score=result.get("quality_metrics", {}).get("overall_score"),
                processing_time_ms=result.get("processing_time_ms", 0),
                created_at=datetime.utcnow()
            )
            
            db.add(validation_record)
            
            # Convert to response model
            validation_result = ValidationResult(
                validation_id=validation_id,
                is_valid=result["is_valid"],
                status=_determine_status(result),
                format=request.shaders[i].format.value,
                target_version=request.shaders[i].target_version,
                target_platforms=[p.value for p in request.shaders[i].target_platforms],
                errors=_convert_errors(result.get("errors", [])),
                warnings=_convert_errors(result.get("warnings", [])),
                info=_convert_errors(result.get("info", [])),
                quality_metrics=result.get("quality_metrics"),
                performance_analysis=_create_performance_analysis(result),
                portability_issues=_create_portability_issues(result.get("portability_issues", [])),
                metadata=result.get("metadata"),
                created_at=datetime.utcnow(),
                processing_time_ms=result.get("processing_time_ms", 0),
                recommendations=result.get("recommendations", [])
            )
            
            validation_results.append(validation_result)
            total_errors += len(result.get("errors", []))
            total_warnings += len(result.get("warnings", []))
            
            if result.get("quality_metrics", {}).get("overall_score"):
                quality_scores.append(result["quality_metrics"]["overall_score"])
            
            processing_times.append(result.get("processing_time_ms", 0))
        
        db.commit()
        
        # Calculate batch statistics
        successful_validations = sum(1 for r in batch_results if r["is_valid"])
        failed_validations = len(batch_results) - successful_validations
        average_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        average_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        batch_result = BatchValidationResult(
            batch_id=batch_id,
            total_shaders=len(request.shaders),
            processed_shaders=len(request.shaders),
            successful_validations=successful_validations,
            failed_validations=failed_validations,
            results=validation_results,
            total_errors=total_errors,
            total_warnings=total_warnings,
            average_quality_score=average_quality_score,
            average_processing_time_ms=average_processing_time,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            parallel_processing=request.parallel_processing
        )
        
        return batch_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch validation failed: {str(e)}")


@router.get("/validate/history", response_model=ValidationHistoryResponse)
async def get_validation_history(
    user_id: Optional[str] = Query(None, description="User identifier"),
    format: Optional[str] = Query(None, description="Filter by shader format"),
    status: Optional[str] = Query(None, description="Filter by validation status"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve validation history with filtering and pagination.
    """
    try:
        # Build query
        query = db.query(ValidationRecord)
        
        # Apply filters
        if user_id:
            query = query.filter(ValidationRecord.user_id == user_id)
        if format:
            query = query.filter(ValidationRecord.format == format)
        if status:
            if status == "valid":
                query = query.filter(ValidationRecord.is_valid == True)
            elif status == "invalid":
                query = query.filter(ValidationRecord.is_valid == False)
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(ValidationRecord.created_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(ValidationRecord.created_at <= end_dt)
        
        # Get total count
        total_count = query.count()
        
        # Apply sorting
        if sort_order == "desc":
            query = query.order_by(desc(getattr(ValidationRecord, sort_by)))
        else:
            query = query.order_by(asc(getattr(ValidationRecord, sort_by)))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        records = query.all()
        
        # Convert to response models
        items = []
        for record in records:
            item = ValidationHistoryItem(
                validation_id=record.id,
                format=record.format,
                status=_determine_status_from_record(record),
                is_valid=record.is_valid,
                error_count=record.error_count,
                warning_count=record.warning_count,
                quality_score=record.quality_score,
                created_at=record.created_at,
                processing_time_ms=record.processing_time_ms,
                user_id=record.user_id
            )
            items.append(item)
        
        # Calculate pagination info
        page_size = limit
        current_page = (offset // page_size) + 1
        page_count = (total_count + page_size - 1) // page_size
        
        # Build applied filters
        applied_filters = {}
        if user_id:
            applied_filters["user_id"] = user_id
        if format:
            applied_filters["format"] = format
        if status:
            applied_filters["status"] = status
        if start_date:
            applied_filters["start_date"] = start_date
        if end_date:
            applied_filters["end_date"] = end_date
        
        response = ValidationHistoryResponse(
            items=items,
            total_count=total_count,
            page_count=page_count,
            current_page=current_page,
            page_size=page_size,
            applied_filters=applied_filters
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve validation history: {str(e)}")


@router.get("/validate/status/{validation_id}", response_model=ValidationStatusResponse)
async def get_validation_status(
    validation_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of a validation request.
    """
    try:
        # Query validation record
        record = db.query(ValidationRecord).filter(ValidationRecord.id == validation_id).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="Validation not found")
        
        # Determine status
        if record.is_valid is None:
            status = "processing"
            progress = 0.5  # Placeholder
            estimated_completion = datetime.utcnow() + timedelta(seconds=30)
        else:
            status = "valid" if record.is_valid else "invalid"
            progress = 1.0
            estimated_completion = None
        
        response = ValidationStatusResponse(
            validation_id=validation_id,
            status=status,
            progress=progress,
            estimated_completion=estimated_completion,
            created_at=record.created_at,
            updated_at=record.updated_at or record.created_at
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get validation status: {str(e)}")


@router.get("/validate/summary", response_model=ValidationSummary)
async def get_validation_summary(
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for all validations.
    """
    try:
        # Get basic counts
        total_validations = db.query(func.count(ValidationRecord.id)).scalar()
        valid_shaders = db.query(func.count(ValidationRecord.id)).filter(ValidationRecord.is_valid == True).scalar()
        invalid_shaders = db.query(func.count(ValidationRecord.id)).filter(ValidationRecord.is_valid == False).scalar()
        warning_shaders = db.query(func.count(ValidationRecord.id)).filter(ValidationRecord.warning_count > 0).scalar()
        
        # Get error statistics
        total_errors = db.query(func.sum(ValidationRecord.error_count)).scalar() or 0
        total_warnings = db.query(func.sum(ValidationRecord.warning_count)).scalar() or 0
        
        # Get quality statistics
        quality_stats = db.query(
            func.avg(ValidationRecord.quality_score),
            func.min(ValidationRecord.quality_score),
            func.max(ValidationRecord.quality_score)
        ).filter(ValidationRecord.quality_score.isnot(None)).first()
        
        average_quality_score = quality_stats[0] if quality_stats[0] else 0.0
        
        # Get performance statistics
        perf_stats = db.query(
            func.avg(ValidationRecord.processing_time_ms),
            func.min(ValidationRecord.processing_time_ms),
            func.max(ValidationRecord.processing_time_ms)
        ).filter(ValidationRecord.processing_time_ms.isnot(None)).first()
        
        average_processing_time_ms = perf_stats[0] if perf_stats[0] else 0.0
        fastest_validation_ms = perf_stats[1] if perf_stats[1] else 0.0
        slowest_validation_ms = perf_stats[2] if perf_stats[2] else 0.0
        
        # Get format distribution
        format_distribution = {}
        format_counts = db.query(
            ValidationRecord.format,
            func.count(ValidationRecord.id)
        ).group_by(ValidationRecord.format).all()
        
        for format_name, count in format_counts:
            format_distribution[format_name] = count
        
        # Create quality distribution (simplified)
        quality_distribution = {
            "excellent": 0,
            "good": 0,
            "fair": 0,
            "poor": 0
        }
        
        # Get most common errors (simplified - would need error tracking table)
        most_common_errors = [
            {"error_code": "SYNTAX_ERROR", "count": 0},
            {"error_code": "SEMANTIC_ERROR", "count": 0}
        ]
        
        summary = ValidationSummary(
            total_validations=total_validations,
            valid_shaders=valid_shaders,
            invalid_shaders=invalid_shaders,
            warning_shaders=warning_shaders,
            total_errors=total_errors,
            total_warnings=total_warnings,
            most_common_errors=most_common_errors,
            average_quality_score=average_quality_score,
            quality_distribution=quality_distribution,
            average_processing_time_ms=average_processing_time_ms,
            fastest_validation_ms=fastest_validation_ms,
            slowest_validation_ms=slowest_validation_ms,
            format_distribution=format_distribution
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get validation summary: {str(e)}")


# Helper functions

def _determine_status(validation_result: Dict[str, Any]) -> str:
    """Determine validation status from result."""
    if not validation_result["is_valid"]:
        return "invalid"
    elif validation_result.get("warnings"):
        return "warning"
    else:
        return "valid"


def _determine_status_from_record(record: ValidationRecord) -> str:
    """Determine validation status from database record."""
    if record.is_valid is None:
        return "processing"
    elif not record.is_valid:
        return "invalid"
    elif record.warning_count > 0:
        return "warning"
    else:
        return "valid"


def _convert_errors(errors: List[Dict[str, Any]]) -> List[ValidationError]:
    """Convert error dictionaries to ValidationError models."""
    converted_errors = []
    for error in errors:
        converted_error = ValidationError(
            message=error.get("message", ""),
            line=error.get("line", 0),
            column=error.get("column", 0),
            severity=error.get("severity", "error"),
            error_code=error.get("error_code", "UNKNOWN_ERROR"),
            context=error.get("context"),
            suggestions=error.get("suggestions")
        )
        converted_errors.append(converted_error)
    return converted_errors


def _create_performance_analysis(validation_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create performance analysis from validation result."""
    if "performance_analysis" not in validation_result:
        return None
    
    perf = validation_result["performance_analysis"]
    return {
        "complexity_score": perf.get("complexity_score", 0.0),
        "instruction_count": perf.get("instruction_count", 0),
        "texture_samples": perf.get("texture_samples", 0),
        "branch_count": perf.get("branch_count", 0),
        "recommendations": perf.get("recommendations", [])
    }


def _create_portability_issues(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create portability issues from validation result."""
    converted_issues = []
    for issue in issues:
        converted_issue = {
            "issue_type": issue.get("issue_type", ""),
            "message": issue.get("message", ""),
            "affected_platforms": issue.get("affected_platforms", []),
            "severity": issue.get("severity", "warning"),
            "suggestions": issue.get("suggestions", [])
        }
        converted_issues.append(converted_issue)
    return converted_issues 