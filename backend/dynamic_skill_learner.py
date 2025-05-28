#!/usr/bin/env python3
"""
Dynamic Skill Learning System - Learns new skills from job postings and resumes
"""

import re
import json
import requests
from collections import Counter, defaultdict
from datetime import datetime
import pandas as pd
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pickle
import os

class DynamicSkillLearner:
    def __init__(self):
        """Initialize the dynamic skill learning system"""
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        
        # Base skill categories (starting point)
        self.base_skills = {
            'programming_languages': set(['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin']),
            'frameworks': set(['react', 'angular', 'vue', 'django', 'flask', 'spring', 'laravel', 'rails', 'express']),
            'databases': set(['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'cassandra']),
            'cloud_platforms': set(['aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean']),
            'tools': set(['git', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible'])
        }
        
        # Dynamic skills learned from data
        self.learned_skills = defaultdict(set)
        self.skill_frequency = Counter()
        self.skill_contexts = defaultdict(list)
        
        # Load existing learned skills
        self.load_learned_skills()
        
        # Patterns for identifying potential skills
        self.skill_patterns = [
            r'\b([A-Z][a-z]+(?:\.[a-z]+)*)\b',  # CamelCase or dotted (React.js, Node.js)
            r'\b([a-z]+(?:-[a-z]+)+)\b',        # hyphenated (scikit-learn, vue-cli)
            r'\b([A-Z]{2,})\b',                 # Acronyms (AWS, API, SQL)
            r'\b([a-z]+\+\+?)\b',               # Plus versions (C++, C+)
        ]
    
    def fetch_trending_skills_from_github(self):
        """Fetch trending technologies from GitHub API (Free)"""
        try:
            # GitHub trending repositories API
            url = "https://api.github.com/search/repositories"
            params = {
                'q': 'created:>2023-01-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                trending_skills = set()
                
                for repo in data.get('items', []):
                    # Extract skills from repository language and topics
                    language = repo.get('language', '')
                    if language:
                        trending_skills.add(language.lower())
                    
                    # Extract from topics
                    topics = repo.get('topics', [])
                    for topic in topics:
                        if len(topic) > 2 and topic.isalpha():
                            trending_skills.add(topic.lower())
                
                print(f"📈 Found {len(trending_skills)} trending skills from GitHub")
                return trending_skills
            
        except Exception as e:
            print(f"Error fetching GitHub trends: {e}")
            return set()
    
    def fetch_skills_from_stackoverflow(self):
        """Fetch popular tags from StackOverflow (Free)"""
        try:
            # StackOverflow tags API
            url = "https://api.stackexchange.com/2.3/tags"
            params = {
                'order': 'desc',
                'sort': 'popular',
                'site': 'stackoverflow',
                'pagesize': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                popular_skills = set()
                
                for tag in data.get('items', []):
                    tag_name = tag.get('name', '')
                    if len(tag_name) > 1:
                        popular_skills.add(tag_name.lower())
                
                print(f"📊 Found {len(popular_skills)} popular skills from StackOverflow")
                return popular_skills
            
        except Exception as e:
            print(f"Error fetching StackOverflow tags: {e}")
            return set()
    
    def learn_skills_from_job_postings(self, job_descriptions):
        """Learn new skills from job posting descriptions"""
        new_skills = set()
        
        for description in job_descriptions:
            if not description:
                continue
            
            # Extract potential skills using various methods
            potential_skills = self.extract_potential_skills(description)
            
            for skill in potential_skills:
                # Validate if it's likely a real skill
                if self.is_likely_skill(skill, description):
                    new_skills.add(skill.lower())
                    self.skill_frequency[skill.lower()] += 1
                    self.skill_contexts[skill.lower()].append(description[:100])
        
        # Categorize new skills
        categorized_skills = self.categorize_skills(new_skills)
        
        # Add to learned skills
        for category, skills in categorized_skills.items():
            self.learned_skills[category].update(skills)
        
        print(f"🧠 Learned {len(new_skills)} new skills from job postings")
        return new_skills
    
    def extract_potential_skills(self, text):
        """Extract potential skills from text using multiple patterns"""
        potential_skills = set()
        
        # Method 1: Pattern matching
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            potential_skills.update(matches)
        
        # Method 2: Common skill contexts
        skill_contexts = [
            r'experience (?:with|in|using) ([^,.]+)',
            r'proficient (?:with|in|using) ([^,.]+)',
            r'knowledge of ([^,.]+)',
            r'familiar with ([^,.]+)',
            r'skills?:?\s*([^.]+)',
            r'technologies?:?\s*([^.]+)',
            r'tools?:?\s*([^.]+)',
            r'frameworks?:?\s*([^.]+)',
            r'languages?:?\s*([^.]+)'
        ]
        
        for pattern in skill_contexts:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split by common separators
                skills = re.split(r'[,;/&\n\r]+', match)
                for skill in skills:
                    skill = skill.strip()
                    if len(skill) > 1 and len(skill) < 30:
                        potential_skills.add(skill)
        
        # Method 3: Noun phrases (requires TextBlob)
        try:
            blob = TextBlob(text)
            for phrase in blob.noun_phrases:
                if len(phrase.split()) <= 3:  # Max 3 words
                    potential_skills.add(phrase)
        except:
            pass
        
        return potential_skills
    
    def is_likely_skill(self, potential_skill, context):
        """Determine if a potential skill is likely a real technical skill"""
        skill_lower = potential_skill.lower().strip()
        
        # Skip if too short or too long
        if len(skill_lower) < 2 or len(skill_lower) > 25:
            return False
        
        # Skip common words
        if skill_lower in self.stop_words:
            return False
        
        # Skip common non-skill words
        non_skills = {
            'experience', 'years', 'work', 'team', 'project', 'development',
            'software', 'application', 'system', 'solution', 'business',
            'company', 'position', 'role', 'job', 'career', 'opportunity'
        }
        if skill_lower in non_skills:
            return False
        
        # Positive indicators
        positive_indicators = [
            # Already known skills
            any(skill_lower in category_skills for category_skills in self.base_skills.values()),
            # Technical patterns
            bool(re.search(r'\.(js|py|java|cpp|cs)$', skill_lower)),
            bool(re.search(r'^[a-z]+\+\+?$', skill_lower)),  # C++, C+
            # Common tech suffixes/prefixes
            any(skill_lower.endswith(suffix) for suffix in ['.js', '.py', 'sql', 'db']),
            any(skill_lower.startswith(prefix) for prefix in ['micro', 'web', 'api']),
            # Version numbers
            bool(re.search(r'\d+', skill_lower)),
            # Context clues
            any(keyword in context.lower() for keyword in [
                'programming', 'coding', 'development', 'framework', 'library',
                'database', 'cloud', 'devops', 'frontend', 'backend'
            ])
        ]
        
        return any(positive_indicators)
    
    def categorize_skills(self, skills):
        """Automatically categorize skills based on patterns and context"""
        categorized = defaultdict(set)
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Programming languages
            if any(pattern in skill_lower for pattern in [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php',
                'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', '.py', '.js'
            ]):
                categorized['programming_languages'].add(skill_lower)
            
            # Frameworks
            elif any(pattern in skill_lower for pattern in [
                'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
                'laravel', 'rails', 'framework', '.js', 'js'
            ]):
                categorized['frameworks'].add(skill_lower)
            
            # Databases
            elif any(pattern in skill_lower for pattern in [
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'database',
                'db', 'oracle', 'cassandra', 'elasticsearch'
            ]):
                categorized['databases'].add(skill_lower)
            
            # Cloud platforms
            elif any(pattern in skill_lower for pattern in [
                'aws', 'azure', 'gcp', 'google cloud', 'cloud', 'heroku',
                'digitalocean', 'vercel', 'netlify'
            ]):
                categorized['cloud_platforms'].add(skill_lower)
            
            # Tools
            elif any(pattern in skill_lower for pattern in [
                'git', 'docker', 'kubernetes', 'jenkins', 'terraform',
                'ansible', 'webpack', 'npm', 'yarn'
            ]):
                categorized['tools'].add(skill_lower)
            
            # Default to general skills
            else:
                categorized['general'].add(skill_lower)
        
        return categorized
    
    def update_skills_from_external_sources(self):
        """Update skills from external free sources"""
        print("🌐 Updating skills from external sources...")
        
        # Fetch from GitHub and StackOverflow
        github_skills = self.fetch_trending_skills_from_github()
        stackoverflow_skills = self.fetch_skills_from_stackoverflow()
        
        # Combine and categorize
        all_external_skills = github_skills | stackoverflow_skills
        categorized = self.categorize_skills(all_external_skills)
        
        # Add to learned skills
        for category, skills in categorized.items():
            self.learned_skills[category].update(skills)
            for skill in skills:
                self.skill_frequency[skill] += 1
        
        print(f"✅ Added {len(all_external_skills)} skills from external sources")
    
    def get_all_skills(self):
        """Get all skills (base + learned)"""
        all_skills = {}
        
        # Combine base and learned skills
        for category in self.base_skills:
            all_skills[category] = self.base_skills[category] | self.learned_skills[category]
        
        # Add learned-only categories
        for category in self.learned_skills:
            if category not in all_skills:
                all_skills[category] = self.learned_skills[category]
        
        return all_skills
    
    def get_trending_skills(self, top_n=20):
        """Get most frequently mentioned skills"""
        return self.skill_frequency.most_common(top_n)
    
    def save_learned_skills(self, filename="database/learned_skills.pkl"):
        """Save learned skills to file"""
        data = {
            'learned_skills': dict(self.learned_skills),
            'skill_frequency': dict(self.skill_frequency),
            'skill_contexts': dict(self.skill_contexts),
            'last_updated': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"💾 Saved learned skills to {filename}")
    
    def load_learned_skills(self, filename="database/learned_skills.pkl"):
        """Load previously learned skills"""
        try:
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                
                self.learned_skills = defaultdict(set, {k: set(v) for k, v in data.get('learned_skills', {}).items()})
                self.skill_frequency = Counter(data.get('skill_frequency', {}))
                self.skill_contexts = defaultdict(list, data.get('skill_contexts', {}))
                
                print(f"📚 Loaded {sum(len(skills) for skills in self.learned_skills.values())} learned skills")
        except Exception as e:
            print(f"Warning: Could not load learned skills: {e}")

# Test function
if __name__ == "__main__":
    learner = DynamicSkillLearner()
    
    # Test with sample job descriptions
    sample_jobs = [
        "We need a developer with React, TypeScript, and GraphQL experience",
        "Looking for someone proficient in Kubernetes, Terraform, and AWS",
        "Required skills: Vue.js, Nuxt.js, and Tailwind CSS"
    ]
    
    print("🧠 Learning skills from sample job descriptions...")
    new_skills = learner.learn_skills_from_job_postings(sample_jobs)
    
    print("🌐 Updating from external sources...")
    learner.update_skills_from_external_sources()
    
    print("📊 Top trending skills:")
    for skill, count in learner.get_trending_skills(10):
        print(f"  {skill}: {count} mentions")
    
    learner.save_learned_skills()
    print("✅ Dynamic skill learning complete!")
