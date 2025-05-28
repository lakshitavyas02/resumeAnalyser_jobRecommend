import re
import json
from typing import List, Dict, Set
import spacy
from textblob import TextBlob

class SkillExtractor:
    """Advanced skill extraction utility with multiple extraction methods"""
    
    def __init__(self):
        """Initialize the skill extractor with comprehensive skill databases"""
        
        # Load spaCy model if available
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Some features may be limited.")
            self.nlp = None
        
        # Comprehensive skill database organized by categories
        self.skill_database = {
            'programming_languages': {
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'php', 
                'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 
                'perl', 'shell', 'bash', 'powershell', 'vba', 'assembly', 'cobol',
                'fortran', 'haskell', 'erlang', 'clojure', 'dart', 'lua'
            },
            'web_technologies': {
                'html', 'css', 'sass', 'scss', 'less', 'bootstrap', 'tailwind css',
                'react', 'angular', 'vue.js', 'svelte', 'ember.js', 'backbone.js',
                'jquery', 'node.js', 'express.js', 'next.js', 'nuxt.js', 'gatsby',
                'webpack', 'gulp', 'grunt', 'parcel', 'vite'
            },
            'frameworks_libraries': {
                'django', 'flask', 'fastapi', 'spring', 'spring boot', 'laravel',
                'rails', 'asp.net', 'express', 'koa', 'nestjs', 'tensorflow',
                'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
                'seaborn', 'opencv', 'nltk', 'spacy', 'plotly', 'bokeh'
            },
            'databases': {
                'mysql', 'postgresql', 'sqlite', 'mongodb', 'redis', 'cassandra',
                'elasticsearch', 'oracle', 'sql server', 'mariadb', 'dynamodb',
                'firebase', 'neo4j', 'couchdb', 'influxdb', 'clickhouse'
            },
            'cloud_platforms': {
                'aws', 'amazon web services', 'azure', 'microsoft azure', 
                'google cloud', 'gcp', 'google cloud platform', 'heroku',
                'digitalocean', 'linode', 'vultr', 'cloudflare', 'vercel',
                'netlify', 'firebase hosting'
            },
            'devops_tools': {
                'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions',
                'travis ci', 'circleci', 'ansible', 'terraform', 'vagrant',
                'chef', 'puppet', 'saltstack', 'helm', 'istio', 'prometheus',
                'grafana', 'elk stack', 'nagios', 'zabbix'
            },
            'version_control': {
                'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial',
                'perforce', 'bazaar'
            },
            'mobile_development': {
                'android', 'ios', 'react native', 'flutter', 'xamarin',
                'ionic', 'cordova', 'phonegap', 'swift', 'objective-c',
                'kotlin', 'java android'
            },
            'data_science_ml': {
                'machine learning', 'deep learning', 'artificial intelligence',
                'data science', 'data analysis', 'statistics', 'big data',
                'hadoop', 'spark', 'kafka', 'airflow', 'jupyter', 'r studio',
                'tableau', 'power bi', 'qlik', 'looker', 'data mining',
                'predictive modeling', 'neural networks', 'computer vision',
                'natural language processing', 'nlp'
            },
            'soft_skills': {
                'leadership', 'communication', 'teamwork', 'problem solving',
                'analytical thinking', 'creative thinking', 'adaptability',
                'time management', 'project management', 'critical thinking',
                'collaboration', 'mentoring', 'public speaking', 'negotiation',
                'conflict resolution', 'emotional intelligence', 'decision making'
            },
            'methodologies': {
                'agile', 'scrum', 'kanban', 'lean', 'waterfall', 'devops',
                'ci/cd', 'tdd', 'test driven development', 'bdd', 
                'behavior driven development', 'pair programming', 'code review',
                'design patterns', 'microservices', 'monolithic', 'mvc',
                'rest api', 'graphql', 'soap'
            },
            'certifications': {
                'aws certified', 'azure certified', 'google certified',
                'cisco certified', 'microsoft certified', 'oracle certified',
                'comptia', 'cissp', 'ceh', 'pmp', 'scrum master', 'itil',
                'six sigma', 'prince2'
            }
        }
        
        # Create a flat list of all skills for quick lookup
        self.all_skills = set()
        for category, skills in self.skill_database.items():
            self.all_skills.update(skills)
        
        # Create skill variations and synonyms
        self.skill_variations = {
            'javascript': ['js', 'javascript', 'ecmascript'],
            'typescript': ['ts', 'typescript'],
            'python': ['python', 'python3', 'py'],
            'c++': ['cpp', 'c++', 'cplusplus'],
            'c#': ['csharp', 'c#', 'c sharp'],
            'node.js': ['nodejs', 'node.js', 'node js'],
            'react': ['reactjs', 'react.js', 'react js'],
            'vue.js': ['vuejs', 'vue.js', 'vue js'],
            'angular': ['angularjs', 'angular.js', 'angular js'],
            'machine learning': ['ml', 'machine learning'],
            'artificial intelligence': ['ai', 'artificial intelligence'],
            'natural language processing': ['nlp', 'natural language processing']
        }
    
    def extract_skills_basic(self, text: str) -> Set[str]:
        """Basic skill extraction using keyword matching"""
        text_lower = text.lower()
        found_skills = set()
        
        # Direct skill matching
        for skill in self.all_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        # Check skill variations
        for main_skill, variations in self.skill_variations.items():
            for variation in variations:
                pattern = r'\b' + re.escape(variation.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.add(main_skill)
        
        return found_skills
    
    def extract_skills_nlp(self, text: str) -> Set[str]:
        """NLP-based skill extraction using spaCy"""
        if not self.nlp:
            return set()
        
        found_skills = set()
        doc = self.nlp(text)
        
        # Extract noun phrases that might be skills
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            if chunk_text in self.all_skills:
                found_skills.add(chunk_text)
        
        # Extract named entities that might be technologies
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'LANGUAGE']:
                ent_text = ent.text.lower().strip()
                if ent_text in self.all_skills:
                    found_skills.add(ent_text)
        
        return found_skills
    
    def extract_skills_context(self, text: str) -> Set[str]:
        """Context-aware skill extraction"""
        found_skills = set()
        
        # Look for skills in specific contexts
        skill_contexts = [
            r'experience\s+(?:with|in|using)\s+([^.]+)',
            r'proficient\s+(?:with|in|using)\s+([^.]+)',
            r'skilled\s+(?:with|in|using)\s+([^.]+)',
            r'knowledge\s+(?:of|in)\s+([^.]+)',
            r'familiar\s+with\s+([^.]+)',
            r'expertise\s+in\s+([^.]+)',
            r'technologies:\s*([^.]+)',
            r'tools:\s*([^.]+)',
            r'languages:\s*([^.]+)',
            r'frameworks:\s*([^.]+)'
        ]
        
        for pattern in skill_contexts:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context_text = match.group(1).lower()
                
                # Extract skills from the context
                for skill in self.all_skills:
                    if skill.lower() in context_text:
                        found_skills.add(skill)
        
        return found_skills
    
    def extract_skills_comprehensive(self, text: str) -> Dict[str, any]:
        """Comprehensive skill extraction using multiple methods"""
        
        # Apply all extraction methods
        basic_skills = self.extract_skills_basic(text)
        nlp_skills = self.extract_skills_nlp(text)
        context_skills = self.extract_skills_context(text)
        
        # Combine all found skills
        all_found_skills = basic_skills | nlp_skills | context_skills
        
        # Categorize skills
        categorized_skills = {}
        for category, category_skills in self.skill_database.items():
            categorized_skills[category] = list(all_found_skills & category_skills)
        
        # Calculate confidence scores
        skill_confidence = {}
        for skill in all_found_skills:
            confidence = 0
            if skill in basic_skills:
                confidence += 0.4
            if skill in nlp_skills:
                confidence += 0.3
            if skill in context_skills:
                confidence += 0.3
            skill_confidence[skill] = min(confidence, 1.0)
        
        return {
            'all_skills': list(all_found_skills),
            'categorized_skills': categorized_skills,
            'skill_confidence': skill_confidence,
            'total_skills_found': len(all_found_skills),
            'extraction_methods': {
                'basic_count': len(basic_skills),
                'nlp_count': len(nlp_skills),
                'context_count': len(context_skills)
            }
        }
    
    def get_skill_suggestions(self, found_skills: List[str], job_description: str = None) -> List[str]:
        """Suggest related skills based on found skills"""
        suggestions = set()
        
        # Skill relationship mapping
        skill_relationships = {
            'python': ['django', 'flask', 'pandas', 'numpy', 'scikit-learn'],
            'javascript': ['react', 'node.js', 'express', 'vue.js', 'angular'],
            'react': ['redux', 'next.js', 'typescript', 'webpack'],
            'java': ['spring', 'spring boot', 'maven', 'gradle'],
            'aws': ['docker', 'kubernetes', 'terraform', 'jenkins'],
            'machine learning': ['python', 'tensorflow', 'pytorch', 'scikit-learn'],
            'data science': ['python', 'r', 'sql', 'tableau', 'jupyter']
        }
        
        for skill in found_skills:
            if skill.lower() in skill_relationships:
                suggestions.update(skill_relationships[skill.lower()])
        
        # Remove skills already found
        suggestions = suggestions - set([skill.lower() for skill in found_skills])
        
        return list(suggestions)
    
    def validate_skills(self, skills: List[str]) -> Dict[str, bool]:
        """Validate if the provided skills are recognized"""
        validation = {}
        for skill in skills:
            validation[skill] = skill.lower() in self.all_skills
        return validation

# Test function
if __name__ == "__main__":
    extractor = SkillExtractor()
    print("Skill Extractor initialized successfully!")
    print(f"Total skills in database: {len(extractor.all_skills)}")
    
