#!/usr/bin/env python3
"""
Live Job Data Fetcher - Fetches real-time job data from free sources
"""

import requests
import json
import time
import os
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LiveJobFetcher:
    def __init__(self):
        """Initialize the live job fetcher"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.job_sources = {
            'remoteok': 'https://remoteok.io/api',
            'indeed': 'https://indeed-com.p.rapidapi.com/search',
            'usajobs': 'https://data.usajobs.gov/api/search'
        }

        # API Keys - Set these with your actual keys
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', None)
        self.rapidapi_host = 'indeed-com.p.rapidapi.com'

    def fetch_indeed_jobs(self, search_term="python", location="United States"):
        """Fetch jobs from Indeed via RapidAPI"""
        try:
            # Skip if no API key is configured
            if not self.rapidapi_key:
                print("⚠️ RapidAPI key not configured, skipping Indeed...")
                return []

            url = "https://indeed-com.p.rapidapi.com/search"

            # Set up headers for RapidAPI
            headers = {
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': self.rapidapi_host,
                'User-Agent': self.headers['User-Agent']
            }

            params = {
                'query': search_term,
                'location': location,
                'page_id': '1',
                'locality': 'us',
                'fromage': '14',  # Jobs from last 14 days
                'limit': '20'
            }

            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                jobs_data = data.get('hits', [])
                processed_jobs = []

                for job in jobs_data:
                    # Extract salary information
                    salary_info = job.get('salary', {})
                    salary_range = 'Not specified'
                    if salary_info:
                        min_sal = salary_info.get('min')
                        max_sal = salary_info.get('max')
                        if min_sal and max_sal:
                            salary_range = f"${min_sal:,} - ${max_sal:,}"
                        elif min_sal:
                            salary_range = f"${min_sal:,}+"

                    processed_job = {
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', ''),
                        'description': self.clean_html(job.get('description', '')),
                        'requirements': self.extract_requirements(job.get('description', '')),
                        'salary_range': salary_range,
                        'job_type': job.get('type', 'Full-time'),
                        'experience_level': self.extract_experience_level(job.get('description', '')),
                        'url': job.get('url', ''),
                        'source': 'Indeed',
                        'posted_date': job.get('date', datetime.now().isoformat())
                    }
                    processed_jobs.append(processed_job)

                return processed_jobs
            else:
                print(f"Indeed API returned status code: {response.status_code}")
                if response.status_code == 429:
                    print("⚠️ Rate limit exceeded. Consider upgrading your RapidAPI plan.")
                elif response.status_code == 401:
                    print("⚠️ Invalid API key. Please check your RapidAPI key.")
                return []

        except Exception as e:
            print(f"Error fetching Indeed jobs: {e}")
            return []

    def fetch_remoteok_jobs(self, search_term="python"):
        """Fetch jobs from RemoteOK API (Free)"""
        try:
            url = "https://remoteok.io/api"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                jobs_data = response.json()
                processed_jobs = []

                # Skip first item (it's metadata)
                for job in jobs_data[1:21]:  # Limit to 20 jobs
                    if search_term.lower() in job.get('description', '').lower():
                        processed_job = {
                            'title': job.get('position', ''),
                            'company': job.get('company', ''),
                            'location': 'Remote',
                            'description': job.get('description', ''),
                            'requirements': self.extract_requirements(job.get('description', '')),
                            'salary_range': f"${job.get('salary_min', 'N/A')} - ${job.get('salary_max', 'N/A')}",
                            'job_type': 'Remote',
                            'experience_level': self.extract_experience_level(job.get('description', '')),
                            'url': f"https://remoteok.io/remote-jobs/{job.get('id', '')}",
                            'source': 'RemoteOK',
                            'posted_date': datetime.now().isoformat()
                        }
                        processed_jobs.append(processed_job)

                return processed_jobs

        except Exception as e:
            print(f"Error fetching RemoteOK jobs: {e}")
            return []

    def fetch_usajobs(self, search_term="software developer"):
        """Fetch jobs from USAJobs API (Free, no API key for basic search)"""
        try:
            url = "https://data.usajobs.gov/api/search"
            params = {
                'Keyword': search_term,
                'ResultsPerPage': 20
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                jobs_data = data.get('SearchResult', {}).get('SearchResultItems', [])
                processed_jobs = []

                for item in jobs_data:
                    job = item.get('MatchedObjectDescriptor', {})
                    processed_job = {
                        'title': job.get('PositionTitle', ''),
                        'company': job.get('OrganizationName', 'US Government'),
                        'location': ', '.join([loc.get('CityName', '') + ', ' + loc.get('CountrySubDivisionCode', '')
                                             for loc in job.get('PositionLocation', [])]),
                        'description': job.get('UserArea', {}).get('Details', {}).get('JobSummary', ''),
                        'requirements': job.get('QualificationSummary', ''),
                        'salary_range': f"${job.get('PositionRemuneration', [{}])[0].get('MinimumRange', 'N/A')} - ${job.get('PositionRemuneration', [{}])[0].get('MaximumRange', 'N/A')}",
                        'job_type': 'Full-time',
                        'experience_level': self.extract_experience_level(job.get('QualificationSummary', '')),
                        'url': job.get('PositionURI', ''),
                        'source': 'USAJobs',
                        'posted_date': job.get('PublicationStartDate', datetime.now().isoformat())
                    }
                    processed_jobs.append(processed_job)

                return processed_jobs
            else:
                print(f"USAJobs API returned status code: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error fetching USAJobs: {e}")
            return []

    def scrape_stackoverflow_jobs(self, search_term="python"):
        """Scrape jobs from StackOverflow (Free)"""
        try:
            url = f"https://stackoverflow.com/jobs?q={search_term}"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('div', class_='listResults')
                processed_jobs = []

                for job_div in job_listings[:10]:  # Limit to 10 jobs
                    try:
                        title_elem = job_div.find('a', class_='s-link')
                        company_elem = job_div.find('span', class_='fc-black-700')
                        location_elem = job_div.find('span', class_='fc-black-500')

                        if title_elem and company_elem:
                            processed_job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': location_elem.get_text(strip=True) if location_elem else 'Not specified',
                                'description': f"Job posting from StackOverflow for {title_elem.get_text(strip=True)}",
                                'requirements': search_term,
                                'salary_range': 'Not specified',
                                'job_type': 'Full-time',
                                'experience_level': 'Mid-level',
                                'url': f"https://stackoverflow.com{title_elem.get('href', '')}",
                                'source': 'StackOverflow',
                                'posted_date': datetime.now().isoformat()
                            }
                            processed_jobs.append(processed_job)
                    except Exception as e:
                        continue

                return processed_jobs

        except Exception as e:
            print(f"Error scraping StackOverflow jobs: {e}")
            return []

    def fetch_all_jobs(self, search_terms=["python", "javascript", "data scientist"]):
        """Fetch jobs from all sources"""
        all_jobs = []

        for term in search_terms:
            print(f"🔍 Fetching jobs for: {term}")

            # Fetch from different sources
            remoteok_jobs = self.fetch_remoteok_jobs(term) or []
            indeed_jobs = self.fetch_indeed_jobs(term) or []  # Note: requires RapidAPI key
            usajobs = self.fetch_usajobs(term) or []

            all_jobs.extend(remoteok_jobs)
            all_jobs.extend(indeed_jobs)
            all_jobs.extend(usajobs)

            # Be respectful to APIs
            time.sleep(2)

        # Remove duplicates based on title and company
        unique_jobs = []
        seen = set()

        for job in all_jobs:
            key = (job['title'].lower(), job['company'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        print(f"✅ Fetched {len(unique_jobs)} unique jobs")

        # If no jobs were fetched, generate sample data
        if not unique_jobs:
            print("⚠️ No live jobs fetched, generating sample data...")
            unique_jobs = self.generate_sample_jobs()

        return unique_jobs

    def generate_sample_jobs(self):
        """Generate sample job data when APIs fail"""
        sample_jobs = [
            {
                'title': 'Senior Python Developer',
                'company': 'TechCorp Solutions',
                'location': 'Remote',
                'description': 'We are seeking a Senior Python Developer to join our growing team. You will work on building scalable web applications and APIs using Python, Django, and modern cloud technologies.',
                'requirements': 'Python, Django, Flask, PostgreSQL, AWS, Docker, 5+ years experience',
                'salary_range': '$120,000 - $160,000',
                'job_type': 'Full-time',
                'experience_level': 'Senior',
                'url': 'https://example.com/job1',
                'source': 'Sample Data',
                'posted_date': datetime.now().isoformat()
            },
            {
                'title': 'Data Scientist',
                'company': 'Analytics Pro Inc',
                'location': 'San Francisco, CA',
                'description': 'Join our data science team to build machine learning models and extract insights from large datasets. Work with cutting-edge technologies in AI and ML.',
                'requirements': 'Python, R, Machine Learning, TensorFlow, PyTorch, SQL, Statistics',
                'salary_range': '$110,000 - $150,000',
                'job_type': 'Full-time',
                'experience_level': 'Mid-level',
                'url': 'https://example.com/job2',
                'source': 'Sample Data',
                'posted_date': datetime.now().isoformat()
            },
            {
                'title': 'Full Stack JavaScript Developer',
                'company': 'WebDev Studios',
                'location': 'Austin, TX',
                'description': 'Build modern web applications using React, Node.js, and cloud technologies. Work in an agile environment with a collaborative team.',
                'requirements': 'JavaScript, React, Node.js, MongoDB, Express, Git, 3+ years experience',
                'salary_range': '$90,000 - $120,000',
                'job_type': 'Full-time',
                'experience_level': 'Mid-level',
                'url': 'https://example.com/job3',
                'source': 'Sample Data',
                'posted_date': datetime.now().isoformat()
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudFirst Tech',
                'location': 'Seattle, WA',
                'description': 'Manage cloud infrastructure and implement CI/CD pipelines. Work with containerization and orchestration technologies.',
                'requirements': 'AWS, Docker, Kubernetes, Jenkins, Terraform, Python, Linux',
                'salary_range': '$115,000 - $155,000',
                'job_type': 'Full-time',
                'experience_level': 'Senior',
                'url': 'https://example.com/job4',
                'source': 'Sample Data',
                'posted_date': datetime.now().isoformat()
            },
            {
                'title': 'Machine Learning Engineer',
                'company': 'AI Innovations',
                'location': 'Boston, MA',
                'description': 'Deploy machine learning models at scale. Work with MLOps, model monitoring, and production ML systems.',
                'requirements': 'Python, TensorFlow, PyTorch, Kubernetes, MLOps, Docker, Statistics',
                'salary_range': '$130,000 - $170,000',
                'job_type': 'Full-time',
                'experience_level': 'Senior',
                'url': 'https://example.com/job5',
                'source': 'Sample Data',
                'posted_date': datetime.now().isoformat()
            }
        ]
        print(f"📝 Generated {len(sample_jobs)} sample jobs")
        return sample_jobs

    def save_jobs_to_csv(self, jobs, filename="database/live_jobs.csv"):
        """Save fetched jobs to CSV file"""
        if jobs:
            df = pd.DataFrame(jobs)
            df.to_csv(filename, index=False)
            print(f"💾 Saved {len(jobs)} jobs to {filename}")
        else:
            print("❌ No jobs to save")

    def clean_html(self, html_text):
        """Remove HTML tags from text"""
        if html_text:
            soup = BeautifulSoup(html_text, 'html.parser')
            return soup.get_text(strip=True)
        return ""

    def extract_requirements(self, description):
        """Extract requirements from job description"""
        if not description:
            return ""

        # Look for common requirement patterns
        req_patterns = [
            r'requirements?:(.+?)(?:\n\n|\n[A-Z]|$)',
            r'qualifications?:(.+?)(?:\n\n|\n[A-Z]|$)',
            r'skills?:(.+?)(?:\n\n|\n[A-Z]|$)',
            r'experience:(.+?)(?:\n\n|\n[A-Z]|$)'
        ]

        for pattern in req_patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:200]  # Limit length

        # Fallback: return first 200 chars of description
        return description[:200] + "..." if len(description) > 200 else description

    def extract_experience_level(self, description):
        """Extract experience level from job description"""
        if not description:
            return "Mid-level"

        desc_lower = description.lower()

        if any(word in desc_lower for word in ['senior', 'lead', 'principal', '5+ years', '7+ years']):
            return "Senior"
        elif any(word in desc_lower for word in ['junior', 'entry', 'graduate', '0-2 years', 'new grad']):
            return "Junior"
        else:
            return "Mid-level"

# Test function
if __name__ == "__main__":
    fetcher = LiveJobFetcher()

    print("🚀 Fetching live job data...")
    jobs = fetcher.fetch_all_jobs(["python developer", "data scientist", "frontend developer"])

    if jobs:
        fetcher.save_jobs_to_csv(jobs)
        print(f"✅ Successfully fetched {len(jobs)} jobs!")

        # Show sample
        for i, job in enumerate(jobs[:3]):
            print(f"\n📋 Job {i+1}:")
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Source: {job['source']}")
    else:
        print("❌ No jobs fetched")
