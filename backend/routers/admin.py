from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.get("/users", response_model=List[schemas.UserOut])
def list_users(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    users = db.query(models.User).all()
    return users

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@router.get("/jobs", response_model=List[schemas.JobOut])
def list_jobs(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    jobs = db.query(models.Job).all()
    result = []
    for job in jobs:
        job_data = schemas.JobOut.model_validate(job)
        job_data.company_name = job.employer.company_name if job.employer else "Unknown"
        result.append(job_data)
    return result

@router.get("/stats")
def get_stats(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    total_users = db.query(models.User).count()
    total_jobs = db.query(models.Job).count()
    total_applications = db.query(models.Application).count()
    
    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "total_applications": total_applications
    }

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}
