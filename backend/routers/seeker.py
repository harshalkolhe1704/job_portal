from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, database, auth

router = APIRouter(
    prefix="/seeker",
    tags=["seeker"],
)

@router.get("/profile", response_model=schemas.JobSeekerOut)
def get_profile(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.seeker:
        raise HTTPException(status_code=403, detail="Not authorized")
    seeker = db.query(models.JobSeeker).filter(models.JobSeeker.id == current_user.id).first()
    if not seeker:
        raise HTTPException(status_code=404, detail="Profile not found")
    return seeker

@router.put("/profile", response_model=schemas.JobSeekerOut)
def update_profile(
    profile: schemas.JobSeekerCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.seeker:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    seeker = db.query(models.JobSeeker).filter(models.JobSeeker.id == current_user.id).first()
    if not seeker:
        # Should create if missing (though auth/register does it)
        seeker = models.JobSeeker(id=current_user.id, full_name=profile.full_name)
        db.add(seeker)
    
    seeker.full_name = profile.full_name
    seeker.skills = profile.skills
    seeker.experience = profile.experience
    seeker.education = profile.education
    seeker.resume_link = profile.resume_link
    
    db.commit()
    db.refresh(seeker)
    return seeker

@router.get("/jobs", response_model=List[schemas.JobOut])
def search_jobs(
    title: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Job)
    if title:
        query = query.filter(models.Job.title.contains(title))
    if location:
        query = query.filter(models.Job.location.contains(location))
    
    jobs = query.all()
    # Populate company_name manually for the response provided manually
    # Note: Using Pydantic's orm_mode, we might need a richer query or property.
    # For simplicity, let's just use the relationship in schema or loop.
    # Actually, JobOut has company_name field, but model doesn't.
    # We can rely on relationship "employer" -> "company_name" and schema update
    # But let's just stick to simpler approach:
    result = []
    for job in jobs:
        job_data = schemas.JobOut.model_validate(job)
        job_data.company_name = job.employer.company_name if job.employer else "Unknown"
        result.append(job_data)
    return result

@router.post("/apply/{job_id}", response_model=schemas.ApplicationOut)
def apply_for_job(
    job_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.seeker:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    existing_app = db.query(models.Application).filter(
        models.Application.job_id == job_id,
        models.Application.seeker_id == current_user.id
    ).first()
    
    if existing_app:
        raise HTTPException(status_code=400, detail="Already applied")
    
    application = models.Application(
        job_id=job_id,
        seeker_id=current_user.id
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    
    # Return with extra data
    app_out = schemas.ApplicationOut.model_validate(application)
    app_out.job_title = job.title
    return app_out

@router.get("/applications", response_model=List[schemas.ApplicationOut])
def my_applications(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.seeker:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    apps = db.query(models.Application).filter(models.Application.seeker_id == current_user.id).all()
    
    result = []
    for app in apps:
        app_out = schemas.ApplicationOut.model_validate(app)
        app_out.job_title = app.job.title
        result.append(app_out)
    return result
