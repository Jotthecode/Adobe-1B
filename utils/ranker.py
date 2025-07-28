from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize
import re

class PersonaRanker:
    """Rank subsections based on persona-specific importance"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
    
    def rank_subsections(self, sections: List[Dict[str, Any]], 
                        persona: str, job_to_be_done: str) -> List[Dict[str, Any]]:
        """Extract and rank relevant subsections"""
        
        subsections = []
        
        # Create persona-job query
        query = f"{persona} working on {job_to_be_done}"
        query_embedding = self.model.encode([query])
        
        for section in sections:
            content = section.get('content', '')
            
            if len(content.strip()) < 50:
                continue
            
            # Split content into sentences/subsections
            sentences = sent_tokenize(content)
            
            # Process longer subsections (combine 2-3 sentences)
            for i in range(0, len(sentences), 2):
                subsection_text = ' '.join(sentences[i:i+3])
                
                if len(subsection_text.strip()) < 30:
                    continue
                
                # Clean and refine text
                refined_text = self._refine_text(subsection_text)
                
                # Calculate relevance score
                text_embedding = self.model.encode([refined_text])
                similarity = cosine_similarity(query_embedding, text_embedding)[0][0]
                
                # Apply persona-specific boosts
                boost = self._calculate_persona_boost(refined_text, persona, job_to_be_done)
                final_score = similarity * boost
                
                subsections.append({
                    "document": section.get("document", "unknown.pdf"),
                    "page": section.get("page", 1),
                    "refined_text": refined_text,
                    "importance_rank": final_score
                })
        
        # Sort by importance and assign final ranks
        subsections.sort(key=lambda x: x["importance_rank"], reverse=True)
        
        for i, subsection in enumerate(subsections):
            subsection["importance_rank"] = i + 1
        
        return subsections
    
    def _refine_text(self, text: str) -> str:
        """Clean and refine text for better readability"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        
        # Capitalize first letter
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
        
        # Limit length
        if len(text) > 500:
            text = text[:497] + "..."
        
        return text
    
    def _calculate_persona_boost(self, text: str, persona: str, job: str) -> float:
        """Calculate persona-specific importance boost"""
        text_lower = text.lower()
        boost = 1.0
        
        # Define persona-specific keywords
        persona_keywords = {
            'researcher': ['study', 'analysis', 'method', 'result', 'conclusion', 'hypothesis'],
            'analyst': ['data', 'trend', 'performance', 'metric', 'analysis', 'insight'],
            'student': ['concept', 'definition', 'example', 'theory', 'principle', 'understand'],
            'investor': ['revenue', 'profit', 'growth', 'risk', 'market', 'financial'],
            'manager': ['strategy', 'objective', 'plan', 'goal', 'implementation', 'process']
        }
        
        # Apply keyword boosts
        for persona_type, keywords in persona_keywords.items():
            if persona_type.lower() in persona.lower():
                keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
                boost += keyword_count * 0.1
        
        # Boost for quantitative content (numbers, percentages)
        if re.search(r'\d+\.?\d*%|\$\d+|\d+\.\d+', text):
            boost += 0.2
        
        # Boost for structured content (lists, bullet points)
        if re.search(r'[•\-\*]\s|^\d+\.|first|second|third', text_lower):
            boost += 0.15
        
        return boost