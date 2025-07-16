#!/usr/bin/env python3
"""
Job Applications Generator for Vetterati
Generates fake job applications linking candidates to jobs
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

class JobApplicationGenerator:
    def __init__(self):
        self.fake = fake
        
    def load_existing_data(self):
        """Load existing candidates and positions"""
        try:
            with open('../json/candidates.json', 'r', encoding='utf-8') as f:
                candidates = json.load(f)
            
            with open('../json/positions.json', 'r', encoding='utf-8') as f:
                positions = json.load(f)
                
            return candidates, positions
        except FileNotFoundError:
            print("Error: candidates.json or positions.json not found. Please run generate_sample_data.py first.")
            return [], []
    
    def generate_applications(self, candidates: List[Dict], positions: List[Dict]) -> List[Dict]:
        """Generate job applications"""
        applications = []
        
        # Generate 2-15 applications per job with varying match quality
        for position in positions:
            position_id = position['id']
            num_applications = random.randint(2, 15)
            
            # Select random candidates for this position
            selected_candidates = random.sample(candidates, min(num_applications, len(candidates)))
            
            for candidate in selected_candidates:
                candidate_id = candidate['id']
                
                # Generate application
                applied_date = fake.date_time_between(
                    start_date=datetime.fromisoformat(position['posted_date']),
                    end_date='now'
                )
                
                # Calculate match percentage based on skills overlap
                match_percentage = self.calculate_match_percentage(candidate, position)
                
                application = {
                    'id': str(uuid.uuid4()),
                    'job_id': position_id,
                    'candidate_id': candidate_id,
                    'status': random.choice([
                        'applied', 'applied', 'applied', 'applied',  # Higher probability for applied
                        'screening', 'screening',
                        'interview',
                        'offer',
                        'rejected',
                        'withdrawn'
                    ]),
                    'source': random.choice([
                        'website', 'website', 'website',  # Higher probability for website
                        'linkedin', 'linkedin',
                        'referral',
                        'job_board',
                        'career_fair',
                        'recruiter'
                    ]),
                    'cover_letter': fake.paragraph(nb_sentences=5) if random.random() > 0.3 else None,
                    'match_percentage': match_percentage,
                    'ahp_score': round(match_percentage / 100 * 0.95 + random.uniform(-0.05, 0.05), 2),
                    'applied_at': applied_date.isoformat(),
                    'last_updated': fake.date_time_between(
                        start_date=applied_date,
                        end_date='now'
                    ).isoformat()
                }
                
                applications.append(application)
        
        return applications
    
    def calculate_match_percentage(self, candidate: Dict, position: Dict) -> int:
        """Calculate match percentage based on skills overlap"""
        candidate_skills = set(candidate.get('skills', []))
        required_skills = set(position.get('requirements', {}).get('skills', {}).get('required', []))
        preferred_skills = set(position.get('requirements', {}).get('skills', {}).get('preferred', []))
        
        if not required_skills and not preferred_skills:
            return random.randint(60, 95)
        
        # Calculate overlap
        required_overlap = len(candidate_skills.intersection(required_skills))
        preferred_overlap = len(candidate_skills.intersection(preferred_skills))
        
        # Base score from required skills
        required_score = (required_overlap / len(required_skills)) * 70 if required_skills else 50
        
        # Bonus from preferred skills
        preferred_score = (preferred_overlap / len(preferred_skills)) * 30 if preferred_skills else 0
        
        # Add randomness for experience and other factors
        experience_factor = random.uniform(-10, 20)
        
        total_score = required_score + preferred_score + experience_factor
        
        # Clamp between 25 and 98
        return max(25, min(98, int(total_score)))
    
    def generate_job_stats(self, applications: List[Dict], positions: List[Dict]) -> Dict:
        """Generate job statistics"""
        stats = {}
        
        for position in positions:
            position_id = position['id']
            position_applications = [app for app in applications if app['job_id'] == position_id]
            
            if position_applications:
                match_percentages = [app['match_percentage'] for app in position_applications]
                stats[position_id] = {
                    'total_applications': len(position_applications),
                    'avg_match_percentage': sum(match_percentages) / len(match_percentages),
                    'highest_match_percentage': max(match_percentages),
                    'applications_by_status': {}
                }
                
                # Count applications by status
                for app in position_applications:
                    status = app['status']
                    stats[position_id]['applications_by_status'][status] = \
                        stats[position_id]['applications_by_status'].get(status, 0) + 1
            else:
                stats[position_id] = {
                    'total_applications': 0,
                    'avg_match_percentage': 0,
                    'highest_match_percentage': 0,
                    'applications_by_status': {}
                }
        
        return stats
    
    def save_to_files(self, applications: List[Dict], stats: Dict):
        """Save generated data to JSON files"""
        # Save applications
        with open('../json/job_applications.json', 'w', encoding='utf-8') as f:
            json.dump(applications, f, indent=2, ensure_ascii=False)
        
        # Save job stats
        with open('../json/job_stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(applications)} job applications to ../json/job_applications.json")
        print(f"Saved job statistics to ../json/job_stats.json")

def main():
    generator = JobApplicationGenerator()
    
    # Load existing data
    candidates, positions = generator.load_existing_data()
    
    if not candidates or not positions:
        print("Cannot generate applications without candidate and position data.")
        return
    
    print(f"Loaded {len(candidates)} candidates and {len(positions)} positions")
    
    # Generate applications
    applications = generator.generate_applications(candidates, positions)
    
    # Generate job statistics
    stats = generator.generate_job_stats(applications, positions)
    
    # Save to files
    generator.save_to_files(applications, stats)
    
    print("Job applications generation complete!")

if __name__ == "__main__":
    main()
