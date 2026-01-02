from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth

router = APIRouter(
    prefix="/employer",
    tags=["employer"],
)

@router.get("/profile", response_model=schemas.EmployerOut)
def get_profile(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized")
    employer = db.query(models.Employer).filter(models.Employer.id == current_user.id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Profile not found")
    return employer

@router.put("/profile", response_model=schemas.EmployerOut)
def update_profile(
    profile: schemas.EmployerCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    employer = db.query(models.Employer).filter(models.Employer.id == current_user.id).first()
    if not employer:
        employer = models.Employer(id=current_user.id, company_name=profile.company_name)
        db.add(employer)
    
    employer.company_name = profile.company_name
    employer.company_description = profile.company_description
    employer.website = profile.website
    employer.location = profile.location
    
    db.commit()
    db.refresh(employer)
    return employer

@router.post("/jobs", response_model=schemas.JobOut)
def post_job(
    job: schemas.JobCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_job = models.Job(
        **job.dict(exclude={"closing_date"}),
        employer_id=current_user.id,
        closing_date=job.closing_date
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    job_out = schemas.JobOut.model_validate(new_job)
    job_out.company_name = current_user.employer_profile.company_name
    return job_out

@router.get("/jobs", response_model=List[schemas.JobOut])
def my_jobs(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    jobs = db.query(models.Job).filter(models.Job.employer_id == current_user.id).all()
    
    result = []
    for job in jobs:
        job_out = schemas.JobOut.model_validate(job)
        job_out.company_name = current_user.employer_profile.company_name
        result.append(job_out)
    return result

@router.put("/jobs/{job_id}", response_model=schemas.JobOut)
def update_job(
    job_id: int,
    job_update: schemas.JobUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    job = db.query(models.Job).filter(models.Job.id == job_id, models.Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = job_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)
    
    db.commit()
    db.refresh(job)
    job_out = schemas.JobOut.model_validate(job)
    job_out.company_name = current_user.employer_profile.company_name
    return job_out

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    job = db.query(models.Job).filter(models.Job.id == job_id, models.Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}

@router.get("/jobs/{job_id}/applicants", response_model=List[schemas.ApplicationOut])
def view_applicants(
    job_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Ensure job belongs to employer
    job = db.query(models.Job).filter(models.Job.id == job_id, models.Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not owned by you")
    
    apps = db.query(models.Application).filter(models.Application.job_id == job_id).all()
    
    result = []
    for app in apps:
        app_out = schemas.ApplicationOut.model_validate(app)
        app_out.job_title = job.title
        app_out.seeker_name = app.seeker.full_name
        app_out.seeker_email = app.seeker.user.email
        app_out.seeker_skills = app.seeker.skills
        app_out.seeker_education = app.seeker.education
        app_out.seeker_experience = app.seeker.experience
        app_out.seeker_resume_link = app.seeker.resume_link
        result.append(app_out)
    return result

@router.put("/applications/{app_id}/status")
def update_application_status(
    app_id: int,
    status: schemas.ApplicationStatus,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != models.UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check ownership via job
    if app.job.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this application")
    
    app.status = status
    db.commit()
    return {"message": "Status updated"}
