#!/usr/bin/env python3
"""
Sample Data Generator for Vetterati
Generates 500 resumes and 50 positions with realistic data
"""

import json
import os
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
from typing import List, Dict, Any

# Initialize Faker
fake = Faker()

# Skills database organized by categories
SKILLS_DATABASE = {
    'programming': [
        'Python', 'JavaScript', 'Java', 'C#', 'C++', 'Go', 'Rust', 'TypeScript',
        'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl'
    ],
    'web_frontend': [
        'React', 'Vue.js', 'Angular', 'HTML5', 'CSS3', 'SASS', 'LESS',
        'Bootstrap', 'Tailwind CSS', 'Material-UI', 'jQuery', 'Webpack'
    ],
    'web_backend': [
        'Node.js', 'Django', 'Flask', 'Spring Boot', 'ASP.NET Core',
        'Express.js', 'FastAPI', 'Laravel', 'Ruby on Rails', 'Phoenix'
    ],
    'databases': [
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'SQLite', 'Oracle', 'SQL Server', 'DynamoDB', 'Cassandra'
    ],
    'cloud_platforms': [
        'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes',
        'Terraform', 'Ansible', 'Jenkins', 'GitLab CI', 'GitHub Actions'
    ],
    'data_science': [
        'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch',
        'Jupyter', 'Matplotlib', 'Seaborn', 'Apache Spark', 'Hadoop'
    ],
    'mobile': [
        'React Native', 'Flutter', 'iOS Development', 'Android Development',
        'Xamarin', 'Ionic', 'Cordova', 'Unity', 'Unreal Engine'
    ],
    'design': [
        'Figma', 'Adobe XD', 'Sketch', 'Photoshop', 'Illustrator',
        'InDesign', 'Canva', 'Blender', 'After Effects', 'Premiere Pro'
    ],
    'soft_skills': [
        'Leadership', 'Communication', 'Problem Solving', 'Team Management',
        'Project Management', 'Agile', 'Scrum', 'Public Speaking',
        'Mentoring', 'Strategic Planning'
    ]
}

# Job titles by category
JOB_TITLES = {
    'engineering': [
        'Software Engineer', 'Senior Software Engineer', 'Lead Software Engineer',
        'Principal Software Engineer', 'Staff Software Engineer', 'Frontend Developer',
        'Backend Developer', 'Full Stack Developer', 'DevOps Engineer',
        'Site Reliability Engineer', 'Cloud Engineer', 'Security Engineer'
    ],
    'data': [
        'Data Scientist', 'Senior Data Scientist', 'Data Engineer',
        'Machine Learning Engineer', 'Data Analyst', 'Business Intelligence Developer',
        'Research Scientist', 'AI Engineer', 'MLOps Engineer'
    ],
    'product': [
        'Product Manager', 'Senior Product Manager', 'Principal Product Manager',
        'Product Owner', 'Technical Product Manager', 'Associate Product Manager',
        'VP of Product', 'Head of Product'
    ],
    'design': [
        'UX Designer', 'UI Designer', 'Senior UX Designer', 'Product Designer',
        'Visual Designer', 'Design Lead', 'Creative Director', 'UX Researcher'
    ],
    'management': [
        'Engineering Manager', 'Senior Engineering Manager', 'Director of Engineering',
        'VP of Engineering', 'CTO', 'Technical Lead', 'Team Lead'
    ],
    'marketing': [
        'Marketing Manager', 'Digital Marketing Manager', 'Content Marketing Manager',
        'Growth Marketing Manager', 'Brand Manager', 'Marketing Director'
    ]
}

# Companies by size
COMPANIES = {
    'startup': [
        'Stripe', 'Airbnb', 'Uber', 'Lyft', 'Snapchat', 'Discord',
        'Notion', 'Figma', 'Canva', 'Zoom', 'Slack', 'Dropbox'
    ],
    'big_tech': [
        'Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Netflix',
        'Tesla', 'Salesforce', 'Oracle', 'Adobe', 'Nvidia', 'Intel'
    ],
    'enterprise': [
        'IBM', 'Accenture', 'Deloitte', 'PwC', 'EY', 'KPMG',
        'Cognizant', 'Infosys', 'TCS', 'Capgemini', 'Wipro'
    ]
}

# Education institutions
UNIVERSITIES = [
    'MIT', 'Stanford University', 'Harvard University', 'Carnegie Mellon University',
    'UC Berkeley', 'Georgia Tech', 'University of Washington', 'Cornell University',
    'Princeton University', 'Yale University', 'Columbia University', 'NYU',
    'University of Texas at Austin', 'University of Illinois', 'Purdue University',
    'University of Michigan', 'Johns Hopkins University', 'Duke University'
]

# Degree types
DEGREES = [
    'Bachelor of Science in Computer Science',
    'Bachelor of Science in Software Engineering',
    'Bachelor of Science in Information Technology',
    'Bachelor of Science in Data Science',
    'Bachelor of Engineering in Computer Engineering',
    'Master of Science in Computer Science',
    'Master of Science in Software Engineering',
    'Master of Science in Data Science',
    'Master of Business Administration',
    'PhD in Computer Science'
]

class SampleDataGenerator:
    def __init__(self):
        self.fake = Faker()
        
    def generate_skills(self, category: str, count: int) -> List[str]:
        """Generate a list of skills from a specific category"""
        available_skills = SKILLS_DATABASE.get(category, [])
        return random.sample(available_skills, min(count, len(available_skills)))
    
    def generate_mixed_skills(self, total_count: int) -> List[str]:
        """Generate a mix of skills from different categories"""
        skills = []
        categories = list(SKILLS_DATABASE.keys())
        
        # Ensure we have skills from multiple categories
        for category in random.sample(categories, min(4, len(categories))):
            category_skills = random.sample(
                SKILLS_DATABASE[category], 
                random.randint(1, min(4, len(SKILLS_DATABASE[category])))
            )
            skills.extend(category_skills)
        
        # Add more skills if needed
        while len(skills) < total_count:
            category = random.choice(categories)
            available = [s for s in SKILLS_DATABASE[category] if s not in skills]
            if available:
                skills.append(random.choice(available))
            else:
                break
                
        return skills[:total_count]
    
    def generate_experience(self, years_experience: int) -> List[Dict[str, Any]]:
        """Generate work experience based on years of experience"""
        experiences = []
        current_date = datetime.now()
        
        # Generate 2-5 jobs based on experience level
        num_jobs = min(max(2, years_experience // 3), 5)
        
        for i in range(num_jobs):
            # Calculate job duration
            if i == 0:  # Current job
                start_date = current_date - timedelta(days=random.randint(365, 1095))
                end_date = None
            else:
                start_date = current_date - timedelta(days=random.randint(365 * (i + 1), 365 * (i + 3)))
                end_date = current_date - timedelta(days=random.randint(365 * i, 365 * (i + 1)))
            
            # Select company and job title
            company_type = random.choice(list(COMPANIES.keys()))
            company = random.choice(COMPANIES[company_type])
            
            job_category = random.choice(list(JOB_TITLES.keys()))
            job_title = random.choice(JOB_TITLES[job_category])
            
            experience = {
                'title': job_title,
                'company': company,
                'location': fake.city() + ', ' + fake.state_abbr(),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
                'description': fake.text(max_nb_chars=200),
                'achievements': [
                    fake.sentence() for _ in range(random.randint(2, 4))
                ]
            }
            experiences.append(experience)
        
        return experiences
    
    def generate_education(self) -> List[Dict[str, Any]]:
        """Generate education history"""
        education = []
        
        # Bachelor's degree
        bachelor_year = datetime.now().year - random.randint(5, 15)
        education.append({
            'degree': random.choice([d for d in DEGREES if 'Bachelor' in d]),
            'institution': random.choice(UNIVERSITIES),
            'graduation_year': bachelor_year,
            'gpa': round(random.uniform(3.0, 4.0), 2)
        })
        
        # Maybe add master's degree
        if random.random() < 0.3:
            master_year = bachelor_year + random.randint(2, 5)
            education.append({
                'degree': random.choice([d for d in DEGREES if 'Master' in d]),
                'institution': random.choice(UNIVERSITIES),
                'graduation_year': master_year,
                'gpa': round(random.uniform(3.2, 4.0), 2)
            })
        
        return education
    
    def generate_candidate(self) -> Dict[str, Any]:
        """Generate a single candidate/resume"""
        candidate_id = str(uuid.uuid4())
        
        # Basic info
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
        
        # Experience level
        years_experience = random.randint(0, 20)
        
        # Generate skills based on experience
        skill_count = min(max(5, years_experience + random.randint(0, 5)), 15)
        skills = self.generate_mixed_skills(skill_count)
        
        candidate = {
            'id': candidate_id,
            'personal_info': {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': fake.phone_number(),
                'location': fake.city() + ', ' + fake.state_abbr(),
                'linkedin_url': f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
                'github_url': f"https://github.com/{first_name.lower()}{last_name.lower()}",
                'portfolio_url': f"https://{first_name.lower()}{last_name.lower()}.dev"
            },
            'summary': fake.paragraph(nb_sentences=3),
            'skills': skills,
            'experience': self.generate_experience(years_experience),
            'education': self.generate_education(),
            'certifications': [
                {
                    'name': random.choice([
                        'AWS Certified Solutions Architect',
                        'Google Cloud Professional',
                        'Microsoft Azure Fundamentals',
                        'Certified Kubernetes Administrator',
                        'PMP Certification',
                        'Scrum Master Certification'
                    ]),
                    'issuer': random.choice(['AWS', 'Google', 'Microsoft', 'Linux Foundation', 'PMI', 'Scrum Alliance']),
                    'date': fake.date_between(start_date='-3y', end_date='today').strftime('%Y-%m-%d')
                } for _ in range(random.randint(0, 3))
            ],
            'languages': [
                {
                    'language': 'English',
                    'proficiency': 'Native'
                }
            ] + [
                {
                    'language': random.choice(['Spanish', 'French', 'German', 'Mandarin', 'Japanese', 'Korean']),
                    'proficiency': random.choice(['Conversational', 'Proficient', 'Fluent'])
                } for _ in range(random.randint(0, 2))
            ],
            'years_experience': years_experience,
            'salary_expectation': {
                'min': random.randint(60000, 120000),
                'max': random.randint(120000, 250000),
                'currency': 'USD'
            },
            'availability': random.choice(['Immediate', '2 weeks', '1 month', '2 months']),
            'remote_preference': random.choice(['Remote', 'Hybrid', 'On-site', 'Flexible']),
            'created_at': fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
            'updated_at': fake.date_time_between(start_date='-30d', end_date='now').isoformat()
        }
        
        return candidate
    
    def generate_position(self) -> Dict[str, Any]:
        """Generate a single job position"""
        position_id = str(uuid.uuid4())
        
        # Select job details
        job_category = random.choice(list(JOB_TITLES.keys()))
        job_title = random.choice(JOB_TITLES[job_category])
        company_type = random.choice(list(COMPANIES.keys()))
        company = random.choice(COMPANIES[company_type])
        
        # Generate required skills
        required_skills = self.generate_mixed_skills(random.randint(5, 12))
        preferred_skills = self.generate_mixed_skills(random.randint(3, 8))
        
        # Experience requirements
        min_experience = random.randint(0, 8)
        max_experience = min_experience + random.randint(3, 8)
        
        # Salary range
        base_salary = random.randint(60000, 120000)
        salary_min = base_salary + (min_experience * random.randint(5000, 10000))
        salary_max = salary_min + random.randint(20000, 80000)
        
        position = {
            'id': position_id,
            'title': job_title,
            'company': {
                'name': company,
                'size': random.choice(['Startup', 'Mid-size', 'Large', 'Enterprise']),
                'industry': random.choice([
                    'Technology', 'Finance', 'Healthcare', 'E-commerce',
                    'Media', 'Education', 'Government', 'Consulting'
                ])
            },
            'location': fake.city() + ', ' + fake.state_abbr(),
            'remote_policy': random.choice(['Remote', 'Hybrid', 'On-site']),
            'employment_type': random.choice(['Full-time', 'Part-time', 'Contract', 'Internship']),
            'department': job_category.title(),
            'level': random.choice(['Entry', 'Mid', 'Senior', 'Lead', 'Principal']),
            'description': fake.paragraph(nb_sentences=5),
            'responsibilities': [
                fake.sentence() for _ in range(random.randint(4, 8))
            ],
            'requirements': {
                'education': random.choice([
                    'Bachelor\'s degree or equivalent',
                    'Master\'s degree preferred',
                    'Advanced degree required',
                    'Relevant experience in lieu of degree'
                ]),
                'experience': {
                    'min_years': min_experience,
                    'max_years': max_experience,
                    'description': f"{min_experience}-{max_experience} years of relevant experience"
                },
                'skills': {
                    'required': required_skills,
                    'preferred': preferred_skills
                },
                'certifications': [
                    random.choice([
                        'AWS Certified Solutions Architect',
                        'Google Cloud Professional',
                        'Microsoft Azure Fundamentals',
                        'Certified Kubernetes Administrator',
                        'PMP Certification',
                        'Scrum Master Certification'
                    ]) for _ in range(random.randint(0, 2))
                ]
            },
            'salary': {
                'min': salary_min,
                'max': salary_max,
                'currency': 'USD',
                'type': 'Annual'
            },
            'benefits': [
                'Health insurance',
                'Dental insurance',
                'Vision insurance',
                '401(k) matching',
                'Paid time off',
                'Professional development budget',
                'Flexible work hours',
                'Stock options'
            ],
            'application_deadline': (datetime.now() + timedelta(weeks=2)).strftime('%Y-%m-%d'),
            'posted_date': (datetime.now() - timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d'),
            'status': random.choice(['Active', 'Paused', 'Filled']),
            'hiring_manager': {
                'name': fake.name(),
                'email': fake.email(),
                'title': random.choice([
                    'Engineering Manager', 'Senior Engineering Manager',
                    'Director of Engineering', 'VP of Engineering',
                    'Product Manager', 'HR Manager'
                ])
            },
            'team_size': random.randint(3, 25),
            'reports_to': random.choice([
                'Engineering Manager', 'Senior Engineering Manager',
                'Director of Engineering', 'VP of Engineering',
                'CTO', 'Product Manager'
            ]),
            'created_at': fake.date_time_between(start_date='-3m', end_date='now').isoformat(),
            'updated_at': fake.date_time_between(start_date='-1w', end_date='now').isoformat()
        }
        
        return position
    
    def generate_all_data(self, num_candidates: int = 500, num_positions: int = 50):
        """Generate all sample data"""
        print(f"Generating {num_candidates} candidates...")
        candidates = []
        for i in range(num_candidates):
            if i % 50 == 0:
                print(f"Generated {i} candidates...")
            candidates.append(self.generate_candidate())
        
        print(f"Generating {num_positions} positions...")
        positions = []
        for i in range(num_positions):
            if i % 10 == 0:
                print(f"Generated {i} positions...")
            positions.append(self.generate_position())
        
        return candidates, positions
    
    def save_to_files(self, candidates: List[Dict], positions: List[Dict]):
        """Save generated data to JSON files"""
        # Save candidates
        with open('../json/candidates.json', 'w', encoding='utf-8') as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
        
        # Save positions
        with open('../json/positions.json', 'w', encoding='utf-8') as f:
            json.dump(positions, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(candidates)} candidates to ../json/candidates.json")
        print(f"Saved {len(positions)} positions to ../json/positions.json")

def main():
    # Get configuration from environment variables or use defaults
    num_candidates = int(os.environ.get('NUM_CANDIDATES', 500))
    num_positions = int(os.environ.get('NUM_POSITIONS', 50))
    
    generator = SampleDataGenerator()
    candidates, positions = generator.generate_all_data(num_candidates, num_positions)
    generator.save_to_files(candidates, positions)
    print("Sample data generation complete!")

if __name__ == "__main__":
    main()
