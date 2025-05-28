import os
import re
import fitz  # PyMuPDF
import docx2txt
from docx import Document
import spacy
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import json
from dynamic_skill_learner import DynamicSkillLearner

class ResumeParser:
    def __init__(self):
        """Initialize the resume parser with NLP models and skill database"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️  spaCy model not found. Please run: python -m spacy download en_core_web_sm")
            self.nlp = None

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

        # Comprehensive skill database
        self.skills_database = {
            'programming_languages': [
                'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'typescript',
                'perl', 'shell', 'bash', 'powershell', 'vba', 'assembly'
            ],
            'frameworks_libraries': [
                'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
                'laravel', 'rails', 'asp.net', 'jquery', 'bootstrap', 'tensorflow', 'pytorch',
                'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'opencv'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'sql server', 'redis',
                'cassandra', 'elasticsearch', 'dynamodb', 'firebase', 'neo4j'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'digitalocean', 'linode',
                'cloudflare', 'vercel', 'netlify'
            ],
            'tools_technologies': [
                'git', 'github', 'gitlab', 'bitbucket', 'docker', 'kubernetes', 'jenkins',
                'travis ci', 'circleci', 'ansible', 'terraform', 'vagrant', 'webpack',
                'gulp', 'grunt', 'npm', 'yarn', 'pip', 'maven', 'gradle'
            ],
            'soft_skills': [
                'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
                'creative', 'adaptable', 'organized', 'detail oriented', 'time management',
                'project management', 'critical thinking', 'collaboration', 'mentoring'
            ],
            'certifications': [
                'aws certified', 'azure certified', 'google certified', 'cisco certified',
                'microsoft certified', 'oracle certified', 'comptia', 'cissp', 'ceh',
                'pmp', 'scrum master', 'agile', 'itil'
            ]
        }

        # Initialize dynamic skill learner
        self.skill_learner = DynamicSkillLearner()

        # Flatten skills for easier matching (combine static + dynamic)
        self.all_skills = []
        for category, skills in self.skills_database.items():
            self.all_skills.extend(skills)

        # Add dynamically learned skills
        dynamic_skills = self.skill_learner.get_all_skills()
        for category, skills in dynamic_skills.items():
            self.all_skills.extend(list(skills))

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            # Try with docx2txt first (simpler)
            text = docx2txt.process(file_path)
            if text.strip():
                return text.strip()

            # Fallback to python-docx
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")

    def extract_text(self, file_path):
        """Extract text from resume file based on extension"""
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        else:
            raise Exception(f"Unsupported file format: {file_extension}")

    def clean_text(self, text):
        """Clean and preprocess text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def extract_contact_info(self, text):
        """Extract contact information from resume text"""
        contact_info = {}

        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info['emails'] = emails

        # Phone number extraction
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        contact_info['phones'] = [phone[0] + phone[1] if isinstance(phone, tuple) else phone for phone in phones]

        # LinkedIn profile
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        contact_info['linkedin'] = linkedin

        return contact_info

    def extract_skills(self, text):
        """Extract skills from resume text using multiple approaches"""
        text_lower = text.lower()
        found_skills = []

        # Method 1: Direct skill matching
        for skill in self.all_skills:
            if skill.lower() in text_lower:
                # Check if it's a whole word match
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)

        # Method 2: NLP-based extraction using spaCy
        if self.nlp:
            doc = self.nlp(text)

            # Extract noun phrases that might be skills
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()
                if len(chunk_text) > 2 and chunk_text in [skill.lower() for skill in self.all_skills]:
                    found_skills.append(chunk_text)

        # Remove duplicates and return
        return list(set(found_skills))

    def extract_experience(self, text):
        """Extract work experience information"""
        experience = []

        # Look for common experience patterns
        experience_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|\w+)\s*[:\-]?\s*([^\n]+)',
            r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|\w+)\s*[:\-]?\s*([^\n]+)',
        ]

        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 3:
                    experience.append({
                        'start_date': match[0],
                        'end_date': match[1],
                        'description': match[2].strip()
                    })

        # Look for job titles and companies
        job_title_patterns = [
            r'(software engineer|developer|analyst|manager|director|consultant|specialist|coordinator)',
            r'(senior|junior|lead|principal|associate)\s+(engineer|developer|analyst|manager)',
        ]

        job_titles = []
        for pattern in job_title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            job_titles.extend([' '.join(match) if isinstance(match, tuple) else match for match in matches])

        return {
            'timeline': experience,
            'job_titles': list(set(job_titles))
        }

    def extract_education(self, text):
        """Extract education information"""
        education = []

        # Degree patterns
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|associate|diploma|certificate)\s*(of|in|degree)?\s*([^\n,]+)',
            r'(b\.?s\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?|b\.?a\.?)\s*(in)?\s*([^\n,]+)',
        ]

        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 3:
                    education.append({
                        'degree_type': match[0],
                        'field': match[2].strip()
                    })

        # University/Institution patterns
        university_pattern = r'(university|college|institute|school)\s+of\s+([^\n,]+)|([^\n,]+)\s+(university|college|institute)'
        universities = re.findall(university_pattern, text, re.IGNORECASE)

        institutions = []
        for match in universities:
            if match[1]:  # "University of X" format
                institutions.append(f"University of {match[1]}")
            elif match[2]:  # "X University" format
                institutions.append(f"{match[2]} {match[3]}")

        return {
            'degrees': education,
            'institutions': list(set(institutions))
        }

    def parse_resume(self, file_path):
        """Main method to parse resume and extract all information"""
        try:
            # Extract text from file
            text = self.extract_text(file_path)

            if not text or len(text.strip()) < 50:
                return {
                    'success': False,
                    'error': 'Could not extract sufficient text from the resume. Please ensure the file is not corrupted.'
                }

            # Clean the text
            cleaned_text = self.clean_text(text)

            # Extract different components
            contact_info = self.extract_contact_info(cleaned_text)
            skills = self.extract_skills(cleaned_text)
            experience = self.extract_experience(cleaned_text)
            education = self.extract_education(cleaned_text)

            # Calculate some basic statistics
            word_count = len(cleaned_text.split())
            sentence_count = len(sent_tokenize(cleaned_text))

            return {
                'success': True,
                'text': cleaned_text,
                'contact_info': contact_info,
                'skills': skills,
                'experience': experience,
                'education': education,
                'statistics': {
                    'word_count': word_count,
                    'sentence_count': sentence_count,
                    'skills_count': len(skills)
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Test function
if __name__ == "__main__":
    parser = ResumeParser()
    print("Resume Parser initialized successfully!")
    print(f"Loaded {len(parser.all_skills)} skills in database")
