import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
import re
from typing import List, Dict, Tuple
import math

class SimilarityCalculator:
    """Advanced similarity calculation utility for resume-job matching"""
    
    def __init__(self):
        """Initialize similarity calculator with various vectorizers"""
        
        # TF-IDF Vectorizer for semantic similarity
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            lowercase=True,
            min_df=1,
            max_df=0.95
        )
        
        # Count Vectorizer for frequency-based similarity
        self.count_vectorizer = CountVectorizer(
            max_features=3000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        # Skill weights for different categories
        self.skill_weights = {
            'programming_languages': 1.5,
            'frameworks_libraries': 1.3,
            'databases': 1.2,
            'cloud_platforms': 1.4,
            'devops_tools': 1.3,
            'soft_skills': 0.8,
            'certifications': 1.6,
            'methodologies': 1.0
        }
    
    def cosine_similarity_tfidf(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity using TF-IDF vectors"""
        try:
            # Fit and transform both texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        
        except Exception as e:
            print(f"Error in TF-IDF similarity calculation: {str(e)}")
            return 0.0
    
    def jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts"""
        try:
            # Tokenize and convert to sets
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
        
        except Exception as e:
            print(f"Error in Jaccard similarity calculation: {str(e)}")
            return 0.0
    
    def skill_based_similarity(self, resume_skills: List[str], job_skills: List[str], 
                             skill_categories: Dict[str, List[str]] = None) -> Dict[str, float]:
        """Calculate similarity based on skill matching with category weights"""
        
        if not resume_skills or not job_skills:
            return {'overall_similarity': 0.0, 'category_similarities': {}}
        
        # Convert to lowercase for comparison
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Calculate basic skill overlap
        matching_skills = set(resume_skills_lower).intersection(set(job_skills_lower))
        total_job_skills = len(set(job_skills_lower))
        
        if total_job_skills == 0:
            return {'overall_similarity': 0.0, 'category_similarities': {}}
        
        basic_similarity = len(matching_skills) / total_job_skills
        
        # Calculate category-wise similarities if categories provided
        category_similarities = {}
        weighted_similarity = 0.0
        total_weight = 0.0
        
        if skill_categories:
            for category, skills in skill_categories.items():
                if skills:  # Only process non-empty categories
                    category_skills_lower = [skill.lower() for skill in skills]
                    category_job_skills = [skill for skill in job_skills_lower if skill in category_skills_lower]
                    category_resume_skills = [skill for skill in resume_skills_lower if skill in category_skills_lower]
                    
                    if category_job_skills:
                        category_matches = set(category_resume_skills).intersection(set(category_job_skills))
                        category_similarity = len(category_matches) / len(set(category_job_skills))
                        category_similarities[category] = category_similarity
                        
                        # Apply weight
                        weight = self.skill_weights.get(category, 1.0)
                        weighted_similarity += category_similarity * weight
                        total_weight += weight
        
        # Calculate overall weighted similarity
        if total_weight > 0:
            overall_similarity = weighted_similarity / total_weight
        else:
            overall_similarity = basic_similarity
        
        return {
            'overall_similarity': overall_similarity,
            'basic_similarity': basic_similarity,
            'category_similarities': category_similarities,
            'matching_skills': list(matching_skills),
            'total_matching_skills': len(matching_skills),
            'total_job_skills': total_job_skills
        }
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using TextBlob sentiment and polarity"""
        try:
            blob1 = TextBlob(text1)
            blob2 = TextBlob(text2)
            
            # Extract key phrases and compare
            phrases1 = set([phrase.lower() for phrase in blob1.noun_phrases])
            phrases2 = set([phrase.lower() for phrase in blob2.noun_phrases])
            
            if not phrases1 or not phrases2:
                return 0.0
            
            # Calculate phrase overlap
            common_phrases = phrases1.intersection(phrases2)
            total_phrases = phrases1.union(phrases2)
            
            if len(total_phrases) == 0:
                return 0.0
            
            return len(common_phrases) / len(total_phrases)
        
        except Exception as e:
            print(f"Error in semantic similarity calculation: {str(e)}")
            return 0.0
    
    def experience_similarity(self, resume_experience: Dict, job_requirements: str) -> float:
        """Calculate similarity based on experience level and job titles"""
        try:
            similarity_score = 0.0
            factors = 0
            
            # Extract years of experience from job requirements
            job_years = self.extract_years_experience(job_requirements)
            
            # Calculate experience timeline similarity
            if 'timeline' in resume_experience and resume_experience['timeline']:
                resume_years = self.calculate_total_experience(resume_experience['timeline'])
                
                if job_years > 0 and resume_years > 0:
                    # Calculate experience match (closer to required years = higher score)
                    exp_ratio = min(resume_years / job_years, 2.0)  # Cap at 2x required experience
                    exp_similarity = min(exp_ratio, 1.0)  # Max score of 1.0
                    similarity_score += exp_similarity
                    factors += 1
            
            # Calculate job title similarity
            if 'job_titles' in resume_experience and resume_experience['job_titles']:
                job_title_similarity = self.calculate_job_title_similarity(
                    resume_experience['job_titles'], 
                    job_requirements
                )
                similarity_score += job_title_similarity
                factors += 1
            
            return similarity_score / factors if factors > 0 else 0.0
        
        except Exception as e:
            print(f"Error in experience similarity calculation: {str(e)}")
            return 0.0
    
    def extract_years_experience(self, text: str) -> int:
        """Extract required years of experience from job description"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:relevant\s*)?experience',
            r'minimum\s*(?:of\s*)?(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0
    
    def calculate_total_experience(self, timeline: List[Dict]) -> float:
        """Calculate total years of experience from timeline"""
        total_years = 0.0
        
        for exp in timeline:
            if 'start_date' in exp and 'end_date' in exp:
                years = self.parse_date_range(exp['start_date'], exp['end_date'])
                total_years += years
        
        return total_years
    
    def parse_date_range(self, start_date: str, end_date: str) -> float:
        """Parse date range and return years of experience"""
        try:
            # Simple year extraction (can be enhanced for more complex date parsing)
            start_year = re.search(r'\d{4}', start_date)
            end_year = re.search(r'\d{4}', end_date)
            
            if start_year and end_year:
                return int(end_year.group()) - int(start_year.group())
            elif start_year and 'present' in end_date.lower():
                from datetime import datetime
                current_year = datetime.now().year
                return current_year - int(start_year.group())
        
        except Exception:
            pass
        
        return 1.0  # Default to 1 year if parsing fails
    
    def calculate_job_title_similarity(self, resume_titles: List[str], job_description: str) -> float:
        """Calculate similarity between resume job titles and job description"""
        if not resume_titles:
            return 0.0
        
        job_description_lower = job_description.lower()
        max_similarity = 0.0
        
        for title in resume_titles:
            title_lower = title.lower()
            
            # Check for exact matches or partial matches
            if title_lower in job_description_lower:
                max_similarity = max(max_similarity, 1.0)
            else:
                # Calculate word overlap
                title_words = set(title_lower.split())
                job_words = set(job_description_lower.split())
                
                if title_words and job_words:
                    overlap = len(title_words.intersection(job_words))
                    similarity = overlap / len(title_words)
                    max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def comprehensive_similarity(self, resume_data: Dict, job_data: Dict) -> Dict[str, float]:
        """Calculate comprehensive similarity using multiple methods"""
        
        # Prepare texts
        resume_text = self.prepare_resume_text(resume_data)
        job_text = self.prepare_job_text(job_data)
        
        # Calculate different similarity metrics
        similarities = {}
        
        # Text-based similarities
        similarities['tfidf_similarity'] = self.cosine_similarity_tfidf(resume_text, job_text)
        similarities['jaccard_similarity'] = self.jaccard_similarity(resume_text, job_text)
        similarities['semantic_similarity'] = self.semantic_similarity(resume_text, job_text)
        
        # Skill-based similarity
        resume_skills = resume_data.get('skills', [])
        job_skills = self.extract_skills_from_job(job_text)
        skill_sim = self.skill_based_similarity(resume_skills, job_skills)
        similarities['skill_similarity'] = skill_sim['overall_similarity']
        
        # Experience-based similarity
        resume_experience = resume_data.get('experience', {})
        similarities['experience_similarity'] = self.experience_similarity(resume_experience, job_text)
        
        # Calculate weighted overall similarity
        weights = {
            'tfidf_similarity': 0.25,
            'skill_similarity': 0.35,
            'experience_similarity': 0.25,
            'semantic_similarity': 0.15
        }
        
        overall_similarity = sum(
            similarities[metric] * weight 
            for metric, weight in weights.items() 
            if metric in similarities
        )
        
        similarities['overall_similarity'] = overall_similarity
        similarities['skill_details'] = skill_sim
        
        return similarities
    
    def prepare_resume_text(self, resume_data: Dict) -> str:
        """Prepare resume data as a single text string"""
        text_parts = []
        
        if 'skills' in resume_data:
            text_parts.append(' '.join(resume_data['skills']))
        
        if 'experience' in resume_data:
            exp = resume_data['experience']
            if 'job_titles' in exp:
                text_parts.append(' '.join(exp['job_titles']))
            if 'timeline' in exp:
                for item in exp['timeline']:
                    if 'description' in item:
                        text_parts.append(item['description'])
        
        if 'education' in resume_data:
            edu = resume_data['education']
            if 'degrees' in edu:
                for degree in edu['degrees']:
                    if 'field' in degree:
                        text_parts.append(degree['field'])
        
        if 'text' in resume_data:
            text_parts.append(resume_data['text'])
        
        return ' '.join(text_parts)
    
    def prepare_job_text(self, job_data: Dict) -> str:
        """Prepare job data as a single text string"""
        text_parts = []
        
        if 'title' in job_data:
            text_parts.append(job_data['title'])
        
        if 'description' in job_data:
            text_parts.append(job_data['description'])
        
        if 'requirements' in job_data:
            text_parts.append(job_data['requirements'])
        
        return ' '.join(text_parts)
    
    def extract_skills_from_job(self, job_text: str) -> List[str]:
        """Extract skills from job description text"""
        # This is a simplified version - in practice, you'd use the SkillExtractor
        common_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws',
            'docker', 'kubernetes', 'git', 'html', 'css', 'mongodb', 'postgresql'
        ]
        
        job_text_lower = job_text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in job_text_lower:
                found_skills.append(skill)
        
        return found_skills

# Test function
if __name__ == "__main__":
    calculator = SimilarityCalculator()
    print("Similarity Calculator initialized successfully!")
    
    # Test similarity calculation
    text1 = "Python developer with React experience"
    text2 = "Looking for Python and React developer"
    similarity = calculator.cosine_similarity_tfidf(text1, text2)
    print(f"Test similarity: {similarity:.3f}")
