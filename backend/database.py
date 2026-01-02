from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL format: mysql+pymysql://username:password@host:port/database_name
# Assuming root:Harshal as per user's previous context.
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Harshal@localhost:3306/job_portal"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
