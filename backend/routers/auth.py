from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, database, auth

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if user already exists
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    
    # Create User
    hashed_password = auth.get_password_hash(user_in.password)
    user = models.User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create associated profile based on role
    if user.role == models.UserRole.seeker:
        seeker = models.JobSeeker(
            id=user.id,
            full_name=user_in.full_name or "New User",
        )
        db.add(seeker)
    elif user.role == models.UserRole.employer:
        employer = models.Employer(
            id=user.id,
            company_name=user_in.company_name or "New Company",
        )
        db.add(employer)
    
    db.commit()
    
    return user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value}

@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user
