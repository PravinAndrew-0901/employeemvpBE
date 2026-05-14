import re

def extract_skills(text: str) -> list[str]:
    # Very basic skill extraction based on a predefined list
    skill_keywords = ['python', 'react', 'fastapi', 'java', 'c++', 'javascript', 'sql', 'mysql', 'aws', 'docker']
    text_lower = text.lower()
    found_skills = []
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill.capitalize())
    return found_skills

def parse_cv_file(file_bytes: bytes, filename: str) -> str:
    # MVP: Currently simulating extraction since we don't have pdfplumber or fitz imported
    # Real implementation would use PyMuPDF (fitz) or pdfplumber
    return "Dummy extracted text python react fastapi"

def parse_cv_and_get_skills(file_bytes: bytes, filename: str) -> list[str]:
    text = parse_cv_file(file_bytes, filename)
    return extract_skills(text)
