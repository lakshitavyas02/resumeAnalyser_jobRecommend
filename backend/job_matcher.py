import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
import os
from textblob import TextBlob
from datetime import datetime, timedelta
from live_job_fetcher import LiveJobFetcher
from dynamic_skill_learner import DynamicSkillLearner

class JobMatcher:
    def __init__(self):
        """Initialize the job matcher with TF-IDF vectorizer"""
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.job_data = None
        self.job_vectors = None

        # Initialize live data components
        self.live_job_fetcher = LiveJobFetcher()
        self.skill_learner = DynamicSkillLearner()
        self.last_update = None
        self.update_interval = timedelta(hours=6)  # Update every 6 hours

    def load_job_data(self, csv_path='../database/jobs.csv', use_live_data=True):
        """Load job data from CSV file and optionally fetch live data"""
        try:
            # Check if we need to update live data
            if use_live_data and self.should_update_live_data():
                print("🔄 Fetching live job data...")
                self.update_live_job_data()

            # Load existing data
            if os.path.exists(csv_path):
                self.job_data = pd.read_csv(csv_path)
                print(f"✅ Loaded {len(self.job_data)} jobs from {csv_path}")
            else:
                # Create sample job data if file doesn't exist
                self.create_sample_job_data(csv_path)
                self.job_data = pd.read_csv(csv_path)
                print(f"✅ Created and loaded {len(self.job_data)} sample jobs")

            # Prepare job descriptions for vectorization
            job_descriptions = []
            for _, job in self.job_data.iterrows():
                # Combine title, description, and requirements for better matching
                combined_text = f"{job['title']} {job['description']} {job.get('requirements', '')}"
                job_descriptions.append(combined_text)

            # Fit TF-IDF vectorizer on job descriptions
            self.job_vectors = self.vectorizer.fit_transform(job_descriptions)
            print(f"✅ Vectorized {len(job_descriptions)} job descriptions")

        except Exception as e:
            print(f"❌ Error loading job data: {str(e)}")
            self.create_sample_job_data(csv_path)
            self.load_job_data(csv_path)

    def create_sample_job_data(self, csv_path):
        """Create sample job data for demonstration"""
        sample_jobs = [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'description': 'We are looking for a Senior Software Engineer to join our team. You will be responsible for developing scalable web applications using modern technologies.',
                'requirements': 'Python, JavaScript, React, Node.js, SQL, AWS, 5+ years experience',
                'salary_range': '$120,000 - $160,000',
                'job_type': 'Full-time',
                'experience_level': 'Senior'
            },
            {
                'title': 'Data Scientist',
                'company': 'DataAnalytics Pro',
                'location': 'New York, NY',
                'description': 'Join our data science team to build machine learning models and extract insights from large datasets.',
                'requirements': 'Python, R, SQL, Machine Learning, Statistics, Pandas, Scikit-learn, TensorFlow',
                'salary_range': '$100,000 - $140,000',
                'job_type': 'Full-time',
                'experience_level': 'Mid-level'
            },
            {
                'title': 'Frontend Developer',
                'company': 'WebSolutions LLC',
                'location': 'Austin, TX',
                'description': 'Create beautiful and responsive user interfaces using modern frontend technologies.',
                'requirements': 'JavaScript, React, Vue.js, HTML, CSS, TypeScript, 3+ years experience',
                'salary_range': '$80,000 - $110,000',
                'job_type': 'Full-time',
                'experience_level': 'Mid-level'
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudFirst Technologies',
                'location': 'Seattle, WA',
                'description': 'Manage cloud infrastructure and implement CI/CD pipelines for our development teams.',
                'requirements': 'AWS, Docker, Kubernetes, Jenkins, Terraform, Linux, Python, Bash',
                'salary_range': '$110,000 - $150,000',
                'job_type': 'Full-time',
                'experience_level': 'Senior'
            },
            {
                'title': 'Product Manager',
                'company': 'InnovateTech',
                'location': 'Boston, MA',
                'description': 'Lead product development from conception to launch, working with cross-functional teams.',
                'requirements': 'Product Management, Agile, Scrum, Analytics, Communication, Leadership, MBA preferred',
                'salary_range': '$130,000 - $170,000',
                'job_type': 'Full-time',
                'experience_level': 'Senior'
            },
            {
                'title': 'Machine Learning Engineer',
                'company': 'AI Innovations',
                'location': 'Palo Alto, CA',
                'description': 'Build and deploy machine learning models at scale using cutting-edge technologies.',
                'requirements': 'Python, TensorFlow, PyTorch, Kubernetes, MLOps, Statistics, Deep Learning',
                'salary_range': '$140,000 - $180,000',
                'job_type': 'Full-time',
                'experience_level': 'Senior'
            },
            {
                'title': 'Full Stack Developer',
                'company': 'StartupXYZ',
                'location': 'Remote',
                'description': 'Work on both frontend and backend development for our growing SaaS platform.',
                'requirements': 'JavaScript, Node.js, React, MongoDB, Express, Git, 2+ years experience',
                'salary_range': '$70,000 - $100,000',
                'job_type': 'Full-time',
                'experience_level': 'Junior'
            },
            {
                'title': 'Cybersecurity Analyst',
                'company': 'SecureNet Corp',
                'location': 'Washington, DC',
                'description': 'Monitor and protect our systems from security threats and vulnerabilities.',
                'requirements': 'Network Security, CISSP, Penetration Testing, Risk Assessment, Incident Response',
                'salary_range': '$90,000 - $120,000',
                'job_type': 'Full-time',
                'experience_level': 'Mid-level'
            },
            {
                'title': 'UX/UI Designer',
                'company': 'DesignStudio',
                'location': 'Los Angeles, CA',
                'description': 'Create intuitive and engaging user experiences for web and mobile applications.',
                'requirements': 'Figma, Sketch, Adobe Creative Suite, User Research, Prototyping, Design Thinking',
                'salary_range': '$75,000 - $105,000',
                'job_type': 'Full-time',
                'experience_level': 'Mid-level'
            },
            {
                'title': 'Database Administrator',
                'company': 'DataManagement Inc',
                'location': 'Chicago, IL',
                'description': 'Manage and optimize database systems to ensure high performance and reliability.',
                'requirements': 'SQL, PostgreSQL, MySQL, Oracle, Database Optimization, Backup and Recovery',
                'salary_range': '$85,000 - $115,000',
                'job_type': 'Full-time',
                'experience_level': 'Mid-level'
            }
        ]

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        # Save to CSV
        df = pd.DataFrame(sample_jobs)
        df.to_csv(csv_path, index=False)
        print(f"✅ Created sample job data at {csv_path}")

    def preprocess_resume_text(self, resume_data):
        """Preprocess resume data for matching"""
        # Combine all resume information into a single text
        text_parts = []

        # Add skills
        if 'skills' in resume_data and resume_data['skills']:
            text_parts.append(' '.join(resume_data['skills']))

        # Add experience information
        if 'experience' in resume_data and resume_data['experience']:
            if 'job_titles' in resume_data['experience']:
                text_parts.append(' '.join(resume_data['experience']['job_titles']))

            if 'timeline' in resume_data['experience']:
                for exp in resume_data['experience']['timeline']:
                    if 'description' in exp:
                        text_parts.append(exp['description'])

        # Add education information
        if 'education' in resume_data and resume_data['education']:
            if 'degrees' in resume_data['education']:
                for degree in resume_data['education']['degrees']:
                    if 'field' in degree:
                        text_parts.append(degree['field'])

        # Add raw text if available
        if 'text' in resume_data:
            text_parts.append(resume_data['text'])

        return ' '.join(text_parts)

    def find_matches(self, resume_data, top_n=10):
        """Find top matching jobs for the given resume"""
        if self.job_data is None or self.job_vectors is None:
            return []

        try:
            # Preprocess resume text
            resume_text = self.preprocess_resume_text(resume_data)

            # Vectorize resume text
            resume_vector = self.vectorizer.transform([resume_text])

            # Calculate cosine similarity
            similarities = cosine_similarity(resume_vector, self.job_vectors).flatten()

            # Get top matches
            top_indices = similarities.argsort()[-top_n:][::-1]

            matches = []
            for idx in top_indices:
                job = self.job_data.iloc[idx]
                match_score = float(similarities[idx])

                # Calculate additional metrics
                skill_match = self.calculate_skill_match(resume_data.get('skills', []), job['requirements'])

                matches.append({
                    'title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'description': job['description'],
                    'requirements': job['requirements'],
                    'salary_range': job.get('salary_range', 'Not specified'),
                    'job_type': job.get('job_type', 'Full-time'),
                    'experience_level': job.get('experience_level', 'Not specified'),
                    'match_score': round(match_score * 100, 2),
                    'skill_match_percentage': skill_match
                })

            return matches

        except Exception as e:
            print(f"Error in find_matches: {str(e)}")
            return []

    def calculate_skill_match(self, resume_skills, job_requirements):
        """Calculate percentage of skill match between resume and job"""
        if not resume_skills or not job_requirements:
            return 0

        # Extract skills from job requirements
        job_requirements_lower = job_requirements.lower()
        resume_skills_lower = [skill.lower() for skill in resume_skills]

        # Count matching skills
        matching_skills = 0
        total_resume_skills = len(resume_skills)

        for skill in resume_skills_lower:
            if skill in job_requirements_lower:
                matching_skills += 1

        if total_resume_skills == 0:
            return 0

        return round((matching_skills / total_resume_skills) * 100, 2)

    def analyze_skill_gap(self, resume_skills, job_description):
        """Analyze skill gaps between resume and job requirements"""
        try:
            # Extract skills mentioned in job description
            job_skills = self.extract_skills_from_text(job_description)

            # Convert to lowercase for comparison
            resume_skills_lower = [skill.lower() for skill in resume_skills]
            job_skills_lower = [skill.lower() for skill in job_skills]

            # Find matching and missing skills
            matching_skills = list(set(resume_skills_lower) & set(job_skills_lower))
            missing_skills = list(set(job_skills_lower) - set(resume_skills_lower))
            extra_skills = list(set(resume_skills_lower) - set(job_skills_lower))

            # Calculate match percentage
            total_job_skills = len(job_skills_lower)
            match_percentage = (len(matching_skills) / total_job_skills * 100) if total_job_skills > 0 else 0

            return {
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'extra_skills': extra_skills,
                'match_percentage': round(match_percentage, 2),
                'total_job_skills': total_job_skills,
                'total_resume_skills': len(resume_skills_lower)
            }

        except Exception as e:
            print(f"Error in analyze_skill_gap: {str(e)}")
            return {
                'matching_skills': [],
                'missing_skills': [],
                'extra_skills': [],
                'match_percentage': 0,
                'total_job_skills': 0,
                'total_resume_skills': len(resume_skills)
            }

    def extract_skills_from_text(self, text):
        """Extract potential skills from job description text"""
        # Common technical skills and keywords
        common_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'html', 'css', 'mongodb', 'postgresql', 'mysql',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'flask',
            'django', 'express', 'angular', 'vue', 'typescript', 'c++', 'c#',
            'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r',
            'machine learning', 'deep learning', 'data science', 'artificial intelligence',
            'devops', 'ci/cd', 'jenkins', 'terraform', 'ansible', 'linux', 'bash'
        ]

        text_lower = text.lower()
        found_skills = []

        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill)

        return found_skills

    def should_update_live_data(self):
        """Check if live data should be updated"""
        if self.last_update is None:
            return True

        return datetime.now() - self.last_update > self.update_interval

    def update_live_job_data(self):
        """Fetch and update live job data"""
        try:
            # Fetch live jobs
            search_terms = ["python developer", "data scientist", "frontend developer",
                          "backend developer", "full stack developer", "software engineer"]

            live_jobs = self.live_job_fetcher.fetch_all_jobs(search_terms)

            if live_jobs:
                # Save live jobs to CSV
                live_df = pd.DataFrame(live_jobs)
                live_df.to_csv('../database/live_jobs.csv', index=False)

                # Learn new skills from job descriptions
                job_descriptions = [job.get('description', '') for job in live_jobs]
                self.skill_learner.learn_skills_from_job_postings(job_descriptions)

                # Update skills from external sources
                self.skill_learner.update_skills_from_external_sources()

                # Save learned skills
                self.skill_learner.save_learned_skills()

                # Combine with existing jobs if any
                if self.job_data is not None:
                    combined_df = pd.concat([self.job_data, live_df], ignore_index=True)
                    # Remove duplicates based on title and company
                    combined_df = combined_df.drop_duplicates(subset=['title', 'company'], keep='last')
                    self.job_data = combined_df
                else:
                    self.job_data = live_df

                self.last_update = datetime.now()
                print(f"✅ Updated with {len(live_jobs)} live jobs")

                # Save updated timestamp
                with open('../database/last_update.txt', 'w') as f:
                    f.write(self.last_update.isoformat())

        except Exception as e:
            print(f"⚠️ Error updating live job data: {e}")
            print("Continuing with existing data...")

    def get_dynamic_skills(self):
        """Get all skills including dynamically learned ones"""
        return self.skill_learner.get_all_skills()

    def get_trending_skills(self, top_n=20):
        """Get trending skills based on job market data"""
        return self.skill_learner.get_trending_skills(top_n)

    def force_update_live_data(self):
        """Force update live data regardless of time interval"""
        self.last_update = None
        self.update_live_job_data()

# Test function
if __name__ == "__main__":
    matcher = JobMatcher()

    # Test with live data
    print("🚀 Testing Job Matcher with live data...")
    matcher.load_job_data(use_live_data=True)

    # Show trending skills
    print("\n📈 Trending skills:")
    for skill, count in matcher.get_trending_skills(10):
        print(f"  {skill}: {count} mentions")

    print("✅ Job Matcher with live data initialized successfully!")
