from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class UserRole(str, enum.Enum):
    seeker = "seeker"
    employer = "employer"
    admin = "admin"

class ApplicationStatus(str, enum.Enum):
    applied = "Applied"
    accepted = "Accepted"
    rejected = "Rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(Enum(UserRole))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    seeker_profile = relationship("JobSeeker", back_populates="user", uselist=False)
    employer_profile = relationship("Employer", back_populates="user", uselist=False)

class JobSeeker(Base):
    __tablename__ = "job_seekers"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    full_name = Column(String(255))
    skills = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    resume_link = Column(String(255), nullable=True)

    user = relationship("User", back_populates="seeker_profile")
    applications = relationship("Application", back_populates="seeker")

class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    company_name = Column(String(255))
    company_description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)

    user = relationship("User", back_populates="employer_profile")
    jobs = relationship("Job", back_populates="employer")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("employers.id"))
    title = Column(String(255))
    description = Column(Text)
    location = Column(String(255))
    job_type = Column(String(50)) # e.g. Full-time, Part-time
    salary_range = Column(String(100))
    posted_at = Column(DateTime(timezone=True), server_default=func.now())
    closing_date = Column(DateTime(timezone=True), nullable=True)

    employer = relationship("Employer", back_populates="jobs")
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    seeker_id = Column(Integer, ForeignKey("job_seekers.id"))
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.applied)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="applications")
    seeker = relationship("JobSeeker", back_populates="applications")
