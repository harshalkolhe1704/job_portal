from sqlalchemy import text
from backend.database import engine

def migrate():
    print("Starting migration...")
    try:
        with engine.connect() as conn:
            # Check if column already exists to avoid error if run multiple times
            result = conn.execute(text("SHOW COLUMNS FROM jobs LIKE 'closing_date'"))
            if not result.fetchone():
                print("Adding closing_date column to jobs table...")
                conn.execute(text("ALTER TABLE jobs ADD COLUMN closing_date DATETIME DEFAULT NULL"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("closing_date column already exists.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
