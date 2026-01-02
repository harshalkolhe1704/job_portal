import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_workflow():
    # 1. Register new employer
    email = "test_employer_new@example.com"
    password = "password123"
    
    register_payload = {
        "email": email,
        "password": password,
        "role": "employer",
        "company_name": "Test Corp"
    }
    
    print(f"Registering {email}...")
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json=register_payload)
        if r.status_code == 400 and "Email already registered" in r.text:
            print("User already exists, proceeding to login.")
        elif r.status_code != 200:
            print(f"Registration failed: {r.status_code} {r.text}")
            return
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 2. Login
    print("Logging in...")
    login_data = {
        "username": email,
        "password": password
    }
    r = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if r.status_code != 200:
        print(f"Login failed: {r.status_code} {r.text}")
        return
    
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in successfully.")

    # 3. Post Job
    print("Posting job...")
    job_payload = {
        "title": "Software Engineer",
        "description": "Develop stuff",
        "location": "Remote",
        "job_type": "Full-time",
        "salary_range": "$100k-120k"
    }
    
    r = requests.post(f"{BASE_URL}/employer/jobs", json=job_payload, headers=headers)
    print(f"Post Job Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    test_workflow()
