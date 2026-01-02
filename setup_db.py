import pymysql

# Database connection details
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Harshal"
DB_NAME = "job_portal"

try:
    # Connect to MySQL Server (no database selected yet)
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()
    
    # Create database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f"Database '{DB_NAME}' created or already exists.")
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"Error creating database: {e}")
