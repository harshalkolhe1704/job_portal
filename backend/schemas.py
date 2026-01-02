from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

def empty_to_none(v):
    if v == "":
        return None
    return v

class UserRole(str, Enum):
    seeker = "seeker"
    employer = "employer"
    admin = "admin"

class ApplicationStatus(str, Enum):
    applied = "Applied"
    accepted = "Accepted"
    rejected = "Rejected"

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: UserRole
    # Additional fields for registration (could be separated depending on role)
    full_name: Optional[str] = None # For Seeker
    company_name: Optional[str] = None # For Employer

class UserOut(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    class Config:
        from_attributes = True

# --- Job Seeker Schemas ---
class JobSeekerBase(BaseModel):
    full_name: str
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    resume_link: Optional[str] = None

class JobSeekerCreate(JobSeekerBase):
    pass

class JobSeekerOut(JobSeekerBase):
    id: int
    class Config:
        from_attributes = True

# --- Employer Schemas ---
class EmployerBase(BaseModel):
    company_name: str
    company_description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None

class EmployerCreate(EmployerBase):
    pass

class EmployerOut(EmployerBase):
    id: int
    class Config:
        from_attributes = True

# --- Job Schemas ---
class JobBase(BaseModel):
    title: str
    description: str
    location: str
    job_type: str
    salary_range: str

class JobCreate(JobBase):
    closing_date: Optional[datetime] = None
    
    @field_validator('closing_date', mode='before')
    @classmethod
    def validate_closing_date(cls, v):
        return empty_to_none(v)

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None
    closing_date: Optional[datetime] = None
    
    @field_validator('closing_date', mode='before')
    @classmethod
    def validate_closing_date(cls, v):
        return empty_to_none(v)

class JobOut(JobBase):
    id: int
    employer_id: int
    posted_at: datetime
    closing_date: Optional[datetime] = None
    company_name: Optional[str] = None # Injected manually if needed
    class Config:
        from_attributes = True

# --- Application Schemas ---
class ApplicationBase(BaseModel):
    job_id: int

class ApplicationOut(BaseModel):
    id: int
    job_id: int
    seeker_id: int
    status: ApplicationStatus
    applied_at: datetime
    job_title: Optional[str] = None
    seeker_name: Optional[str] = None
    seeker_email: Optional[EmailStr] = None
    seeker_skills: Optional[str] = None
    seeker_education: Optional[str] = None
    seeker_experience: Optional[str] = None
    seeker_resume_link: Optional[str] = None
    class Config:
        from_attributes = True
