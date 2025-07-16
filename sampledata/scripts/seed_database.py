#!/usr/bin/env python3
"""
Database seeding script for Vetterati sample data
Seeds PostgreSQL databases with generated candidates and positions
"""

import json
import psycopg2
from psycopg2.extras import Json
from datetime import datetime
import uuid

class DatabaseSeeder:
    def __init__(self):
        # Database connection parameters
        self.db_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'vetterati_ats',
            'user': 'ats_user',
            'password': 'ats_password'
        }
        
        # Connection pools for different services
        self.connections = {}
    
    def connect_to_database(self, service_name: str, database_name: str = None):
        """Create connection to specific service database"""
        params = self.db_params.copy()
        if database_name:
            params['database'] = database_name
        
        try:
            conn = psycopg2.connect(**params)
            conn.autocommit = True
            self.connections[service_name] = conn
            print(f"Connected to {service_name} database")
            return conn
        except Exception as e:
            print(f"Error connecting to {service_name} database: {e}")
            return None
    
    def create_tables(self):
        """Create necessary tables for sample data"""
        
        # Connect to main database
        conn = self.connect_to_database('main', 'vetterati_ats')
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Create candidates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id UUID PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                location VARCHAR(255),
                linkedin_url VARCHAR(500),
                github_url VARCHAR(500),
                portfolio_url VARCHAR(500),
                summary TEXT,
                skills JSONB,
                experience JSONB,
                education JSONB,
                certifications JSONB,
                languages JSONB,
                years_experience INTEGER,
                salary_expectation JSONB,
                availability VARCHAR(50),
                remote_preference VARCHAR(50),
                resume_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id UUID PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                company_name VARCHAR(255) NOT NULL,
                company_info JSONB,
                location VARCHAR(255),
                remote_policy VARCHAR(50),
                employment_type VARCHAR(50),
                department VARCHAR(100),
                level VARCHAR(50),
                description TEXT,
                responsibilities JSONB,
                requirements JSONB,
                salary JSONB,
                benefits JSONB,
                application_deadline DATE,
                posted_date DATE,
                status VARCHAR(50),
                hiring_manager JSONB,
                team_size INTEGER,
                reports_to VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create candidate_matches table for AHP results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidate_matches (
                id UUID PRIMARY KEY,
                candidate_id UUID REFERENCES candidates(id),
                position_id UUID REFERENCES positions(id),
                overall_score DECIMAL(5,4),
                match_percentage INTEGER,
                criteria_scores JSONB,
                score_breakdown JSONB,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                methodology VARCHAR(50) DEFAULT 'AHP',
                metadata JSONB,
                UNIQUE(candidate_id, position_id)
            );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_skills ON candidates USING GIN(skills);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_positions_title ON positions(title);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_positions_company ON positions(company_name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_score ON candidate_matches(overall_score DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_candidate ON candidate_matches(candidate_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_position ON candidate_matches(position_id);")
        
        print("Tables created successfully!")
        cursor.close()
        return True
    
    def load_sample_data(self):
        """Load sample data from JSON files"""
        try:
            with open('../json/candidates.json', 'r', encoding='utf-8') as f:
                candidates = json.load(f)
            
            with open('../json/positions.json', 'r', encoding='utf-8') as f:
                positions = json.load(f)
            
            print(f"Loaded {len(candidates)} candidates and {len(positions)} positions")
            return candidates, positions
        except FileNotFoundError:
            print("Sample data files not found. Please run generate_sample_data.py first.")
            return None, None
    
    def seed_candidates(self, candidates):
        """Seed candidates table with sample data"""
        conn = self.connections.get('main')
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("TRUNCATE TABLE candidate_matches CASCADE;")
        cursor.execute("TRUNCATE TABLE candidates CASCADE;")
        
        for candidate in candidates:
            # Generate resume content
            resume_content = self.generate_resume_content(candidate)
            
            cursor.execute("""
                INSERT INTO candidates (
                    id, first_name, last_name, email, phone, location,
                    linkedin_url, github_url, portfolio_url, summary,
                    skills, experience, education, certifications, languages,
                    years_experience, salary_expectation, availability,
                    remote_preference, resume_content, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                candidate['id'],
                candidate['personal_info']['first_name'],
                candidate['personal_info']['last_name'],
                candidate['personal_info']['email'],
                candidate['personal_info']['phone'],
                candidate['personal_info']['location'],
                candidate['personal_info']['linkedin_url'],
                candidate['personal_info']['github_url'],
                candidate['personal_info']['portfolio_url'],
                candidate['summary'],
                Json(candidate['skills']),
                Json(candidate['experience']),
                Json(candidate['education']),
                Json(candidate['certifications']),
                Json(candidate['languages']),
                candidate['years_experience'],
                Json(candidate['salary_expectation']),
                candidate['availability'],
                candidate['remote_preference'],
                resume_content,
                candidate['created_at'],
                candidate['updated_at']
            ))
        
        print(f"Seeded {len(candidates)} candidates")
        cursor.close()
        return True
    
    def seed_positions(self, positions):
        """Seed positions table with sample data"""
        conn = self.connections.get('main')
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("TRUNCATE TABLE positions CASCADE;")
        
        for position in positions:
            cursor.execute("""
                INSERT INTO positions (
                    id, title, company_name, company_info, location,
                    remote_policy, employment_type, department, level,
                    description, responsibilities, requirements, salary,
                    benefits, application_deadline, posted_date, status,
                    hiring_manager, team_size, reports_to, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                position['id'],
                position['title'],
                position['company']['name'],
                Json(position['company']),
                position['location'],
                position['remote_policy'],
                position['employment_type'],
                position['department'],
                position['level'],
                position['description'],
                Json(position['responsibilities']),
                Json(position['requirements']),
                Json(position['salary']),
                Json(position['benefits']),
                position['application_deadline'],
                position['posted_date'],
                position['status'],
                Json(position['hiring_manager']),
                position['team_size'],
                position['reports_to'],
                position['created_at'],
                position['updated_at']
            ))
        
        print(f"Seeded {len(positions)} positions")
        cursor.close()
        return True
    
    def generate_resume_content(self, candidate):
        """Generate formatted resume content from candidate data"""
        content = f"""
{candidate['personal_info']['first_name']} {candidate['personal_info']['last_name']}
{candidate['personal_info']['email']} | {candidate['personal_info']['phone']}
{candidate['personal_info']['location']}
LinkedIn: {candidate['personal_info']['linkedin_url']}
GitHub: {candidate['personal_info']['github_url']}

PROFESSIONAL SUMMARY
{candidate['summary']}

SKILLS
{', '.join(candidate['skills'])}

EXPERIENCE
"""
        
        for exp in candidate['experience']:
            end_date = exp['end_date'] if exp['end_date'] else 'Present'
            content += f"""
{exp['title']} | {exp['company']} | {exp['location']}
{exp['start_date']} - {end_date}
{exp['description']}
"""
            for achievement in exp['achievements']:
                content += f"• {achievement}\n"
        
        content += "\nEDUCATION\n"
        for edu in candidate['education']:
            content += f"{edu['degree']} | {edu['institution']} | {edu['graduation_year']}\n"
        
        if candidate['certifications']:
            content += "\nCERTIFICATIONS\n"
            for cert in candidate['certifications']:
                content += f"{cert['name']} | {cert['issuer']} | {cert['date']}\n"
        
        return content
    
    def generate_ahp_matches(self, candidates, positions):
        """Generate AHP match scores for all candidate-position combinations"""
        conn = self.connections.get('main')
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        print("Generating AHP matches...")
        
        # For demonstration, we'll generate matches for top candidates per position
        for position in positions:
            # Get position requirements
            req_skills = set(position['requirements']['skills']['required'])
            pref_skills = set(position['requirements']['skills']['preferred'])
            min_exp = position['requirements']['experience']['min_years']
            max_exp = position['requirements']['experience']['max_years']
            
            # Calculate matches for all candidates
            candidate_scores = []
            
            for candidate in candidates:
                score = self.calculate_ahp_score(candidate, position, req_skills, pref_skills, min_exp, max_exp)
                candidate_scores.append((candidate, score))
            
            # Sort by score and take top 20 matches per position
            candidate_scores.sort(key=lambda x: x[1]['overall_score'], reverse=True)
            top_matches = candidate_scores[:20]
            
            # Insert matches into database
            for candidate, score_data in top_matches:
                match_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO candidate_matches (
                        id, candidate_id, position_id, overall_score,
                        match_percentage, criteria_scores, score_breakdown,
                        calculated_at, methodology, metadata
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    match_id,
                    candidate['id'],
                    position['id'],
                    score_data['overall_score'],
                    score_data['match_percentage'],
                    Json(score_data['criteria_scores']),
                    Json(score_data['score_breakdown']),
                    datetime.now(),
                    'AHP',
                    Json(score_data['metadata'])
                ))
        
        print(f"Generated AHP matches for {len(positions)} positions")
        cursor.close()
        return True
    
    def calculate_ahp_score(self, candidate, position, req_skills, pref_skills, min_exp, max_exp):
        """Calculate AHP score for a candidate-position pair"""
        import random
        
        # Candidate skills
        candidate_skills = set(candidate['skills'])
        candidate_exp = candidate['years_experience']
        
        # Calculate skill match
        required_match = len(req_skills.intersection(candidate_skills)) / len(req_skills) if req_skills else 0
        preferred_match = len(pref_skills.intersection(candidate_skills)) / len(pref_skills) if pref_skills else 0
        skill_score = (required_match * 0.7) + (preferred_match * 0.3)
        
        # Calculate experience match
        if candidate_exp < min_exp:
            exp_score = max(0, candidate_exp / min_exp)
        elif candidate_exp > max_exp:
            exp_score = max(0.5, 1 - ((candidate_exp - max_exp) / 10))
        else:
            exp_score = 1.0
        
        # AHP criteria weights
        criteria_weights = {
            'technical_skills': 0.35,
            'experience': 0.25,
            'education': 0.15,
            'communication': 0.10,
            'cultural_fit': 0.10,
            'leadership': 0.05
        }
        
        # Calculate individual scores (some randomization for realism)
        criteria_scores = {
            'technical_skills': min(1.0, skill_score + random.uniform(-0.1, 0.1)),
            'experience': min(1.0, exp_score + random.uniform(-0.1, 0.1)),
            'education': random.uniform(0.6, 1.0),
            'communication': random.uniform(0.5, 0.9),
            'cultural_fit': random.uniform(0.4, 0.8),
            'leadership': random.uniform(0.3, 0.7)
        }
        
        # Ensure scores are between 0 and 1
        for key in criteria_scores:
            criteria_scores[key] = max(0, min(1, criteria_scores[key]))
        
        # Calculate overall score
        overall_score = sum(criteria_scores[key] * criteria_weights[key] for key in criteria_weights)
        match_percentage = int(overall_score * 100)
        
        # Detailed breakdown
        score_breakdown = {
            'skill_breakdown': {
                'required_skills_match': required_match,
                'preferred_skills_match': preferred_match,
                'total_skills': len(candidate_skills),
                'matched_required': list(req_skills.intersection(candidate_skills)),
                'matched_preferred': list(pref_skills.intersection(candidate_skills))
            },
            'experience_breakdown': {
                'candidate_years': candidate_exp,
                'required_min': min_exp,
                'required_max': max_exp,
                'experience_fit': exp_score
            }
        }
        
        metadata = {
            'position_title': position['title'],
            'company': position['company']['name'],
            'calculation_method': 'weighted_criteria',
            'criteria_weights': criteria_weights
        }
        
        return {
            'overall_score': round(overall_score, 4),
            'match_percentage': match_percentage,
            'criteria_scores': criteria_scores,
            'score_breakdown': score_breakdown,
            'metadata': metadata
        }
    
    def close_connections(self):
        """Close all database connections"""
        for service_name, conn in self.connections.items():
            if conn:
                conn.close()
                print(f"Closed connection to {service_name}")

def main():
    seeder = DatabaseSeeder()
    
    try:
        # Create tables
        if not seeder.create_tables():
            print("Failed to create tables")
            return
        
        # Load sample data
        candidates, positions = seeder.load_sample_data()
        if not candidates or not positions:
            print("Failed to load sample data")
            return
        
        # Seed candidates
        if not seeder.seed_candidates(candidates):
            print("Failed to seed candidates")
            return
        
        # Seed positions
        if not seeder.seed_positions(positions):
            print("Failed to seed positions")
            return
        
        # Generate AHP matches
        if not seeder.generate_ahp_matches(candidates, positions):
            print("Failed to generate AHP matches")
            return
        
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        seeder.close_connections()

if __name__ == "__main__":
    main()
