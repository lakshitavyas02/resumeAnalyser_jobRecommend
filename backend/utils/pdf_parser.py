import fitz  # PyMuPDF
import re
from typing import Dict, List, Optional

class PDFParser:
    """Utility class for parsing PDF files and extracting structured information"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text(self, file_path: str) -> str:
        """Extract raw text from PDF file"""
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_with_formatting(self, file_path: str) -> Dict:
        """Extract text with basic formatting information"""
        try:
            doc = fitz.open(file_path)
            pages_data = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get text blocks with position information
                blocks = page.get_text("dict")
                
                page_data = {
                    'page_number': page_num + 1,
                    'text': page.get_text(),
                    'blocks': []
                }
                
                for block in blocks["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                page_data['blocks'].append({
                                    'text': span["text"],
                                    'font': span["font"],
                                    'size': span["size"],
                                    'bbox': span["bbox"]
                                })
                
                pages_data.append(page_data)
            
            doc.close()
            
            return {
                'total_pages': len(pages_data),
                'pages': pages_data,
                'full_text': '\n'.join([page['text'] for page in pages_data])
            }
        
        except Exception as e:
            raise Exception(f"Error extracting formatted text from PDF: {str(e)}")
    
    def extract_metadata(self, file_path: str) -> Dict:
        """Extract metadata from PDF file"""
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            
            doc.close()
            
            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': len(doc)
            }
        
        except Exception as e:
            raise Exception(f"Error extracting PDF metadata: {str(e)}")
    
    def find_sections(self, text: str) -> Dict[str, str]:
        """Identify common resume sections in the text"""
        sections = {}
        
        # Common section headers
        section_patterns = {
            'contact': r'(contact|personal\s+information|contact\s+information)',
            'summary': r'(summary|profile|objective|about)',
            'experience': r'(experience|work\s+experience|employment|professional\s+experience)',
            'education': r'(education|academic|qualifications)',
            'skills': r'(skills|technical\s+skills|competencies|expertise)',
            'projects': r'(projects|portfolio)',
            'certifications': r'(certifications|certificates|licenses)',
            'awards': r'(awards|achievements|honors)',
            'references': r'(references)'
        }
        
        text_lines = text.split('\n')
        current_section = None
        section_content = {}
        
        for line in text_lines:
            line_lower = line.lower().strip()
            
            # Check if line matches any section header
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line_lower) and len(line_lower) < 50:
                    current_section = section_name
                    section_content[section_name] = []
                    break
            else:
                # Add content to current section
                if current_section and line.strip():
                    section_content[current_section].append(line.strip())
        
        # Convert lists to strings
        for section, content in section_content.items():
            sections[section] = '\n'.join(content)
        
        return sections
    
    def extract_tables(self, file_path: str) -> List[List[str]]:
        """Extract tables from PDF (basic implementation)"""
        try:
            doc = fitz.open(file_path)
            tables = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Try to find table-like structures
                # This is a basic implementation - for complex tables, consider using tabula-py
                page_tables = page.find_tables()
                
                for table in page_tables:
                    table_data = table.extract()
                    if table_data:
                        tables.append(table_data)
            
            doc.close()
            return tables
        
        except Exception as e:
            print(f"Warning: Could not extract tables: {str(e)}")
            return []
    
    def is_valid_pdf(self, file_path: str) -> bool:
        """Check if the file is a valid PDF"""
        try:
            doc = fitz.open(file_path)
            doc.close()
            return True
        except:
            return False

# Test function
if __name__ == "__main__":
    parser = PDFParser()
    print("PDF Parser utility initialized successfully!")
    print(f"Supported formats: {parser.supported_formats}")
