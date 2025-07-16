#!/usr/bin/env python3
"""
Simple script to seed the database via job-service API
"""

import requests
import json
from datetime import datetime, timedelta
from faker import Faker
import random
import uuid

fake = Faker()

# API Configuration
API_BASE_URL = "http://localhost:5000/api/v1"

# Sample data
DEPARTMENTS = ["Engineering", "Product", "Design", "Marketing", "Sales", "HR", "Operations"]
EMPLOYMENT_TYPES = ["full-time", "part-time", "contract", "internship"]
EXPERIENCE_LEVELS = ["entry", "mid", "senior", "executive"]
JOB_STATUSES = ["draft", "active", "paused", "closed"]
APPLICATION_STATUSES = ["applied", "screening", "interview", "offer", "rejected", "withdrawn"]

TECH_SKILLS = [
    "Python", "JavaScript", "React", "Node.js", "TypeScript", "Java", "C#", "SQL",
    "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure",
    "Git", "CI/CD", "REST APIs", "GraphQL", "HTML", "CSS", "Vue.js", "Angular"
]

def create_sample_jobs(num_jobs=20):
    """Create sample jobs via API"""
    jobs = []
    
    for i in range(num_jobs):
        job_data = {
            "title": fake.job(),
            "description": fake.text(max_nb_chars=1000),
            "requirements": fake.text(max_nb_chars=500),
            "responsibilities": fake.text(max_nb_chars=500),
            "benefits": fake.text(max_nb_chars=300),
            "department": random.choice(DEPARTMENTS),
            "location": fake.city(),
            "employment_type": random.choice(EMPLOYMENT_TYPES),
            "experience_level": random.choice(EXPERIENCE_LEVELS),
            "salary_min": random.randint(40000, 80000),
            "salary_max": random.randint(80000, 150000),
            "salary_currency": "USD",
            "status": random.choice(JOB_STATUSES),
            "priority": random.choice(["low", "medium", "high", "urgent"]),
            "required_skills": random.sample(TECH_SKILLS, random.randint(3, 8)),
            "preferred_skills": random.sample(TECH_SKILLS, random.randint(2, 5)),
            "certifications": [],
            "languages": ["English"],
            "created_by": str(uuid.uuid4()),
            "posted_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/jobs", json=job_data)
            if response.status_code == 201:
                job = response.json()
                jobs.append(job)
                print(f"Created job: {job['title']}")
            else:
                print(f"Failed to create job: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error creating job: {e}")
    
    return jobs

def create_sample_applications(jobs, num_applications_per_job=5):
    """Create sample job applications"""
    applications = []
    
    for job in jobs:
        for i in range(random.randint(1, num_applications_per_job)):
            application_data = {
                "job_id": job["id"],
                "candidate_id": str(uuid.uuid4()),
                "status": random.choice(APPLICATION_STATUSES),
                "source": random.choice(["website", "linkedin", "referral", "job_board"]),
                "cover_letter": fake.text(max_nb_chars=500),
                "ahp_score": round(random.uniform(0.3, 0.95), 2)
            }
            
            try:
                response = requests.post(f"{API_BASE_URL}/jobs/{job['id']}/applications", json=application_data)
                if response.status_code == 201:
                    application = response.json()
                    applications.append(application)
                    print(f"Created application for job: {job['title']}")
                else:
                    print(f"Failed to create application: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error creating application: {e}")
    
    return applications

def main():
    print("Starting database seeding via API...")
    
    # Create sample jobs
    print("Creating sample jobs...")
    jobs = create_sample_jobs(20)
    
    # Create sample applications
    print("Creating sample job applications...")
    applications = create_sample_applications(jobs, 8)
    
    print(f"Seeding complete! Created {len(jobs)} jobs and {len(applications)} applications")

if __name__ == "__main__":
    main()
