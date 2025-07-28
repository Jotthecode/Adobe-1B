from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize

class ContentExtractor:
    """Extract relevant sections based on persona and job requirements"""
    
    def __init__(self):
        # Download NLTK data if not present
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        # Load lightweight sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def extract_relevant_sections(self, sections: List[Dict[str, Any]], 
                                persona: str, job_to_be_done: str) -> List[Dict[str, Any]]:
        """Extract sections most relevant to persona and job"""
        
        if not sections:
            return []
        
        # Create query embedding
        query = f"{persona} needs to {job_to_be_done}"
        query_embedding = self.model.encode([query])
        
        # Score sections
        scored_sections = []
        
        for section in sections:
            # Combine title and content for scoring
            text = f"{section.get('section_title', '')} {section.get('content', '')}"
            
            if len(text.strip()) < 20:  # Skip very short sections
                continue
            
            # Get section embedding
            section_embedding = self.model.encode([text])
            
            # Calculate similarity score
            similarity = cosine_similarity(query_embedding, section_embedding)[0][0]
            
            # Boost score for headings and structured content
            boost = 1.0
            if section.get('section_title'):
                boost += 0.2
            if self._contains_keywords(text, persona, job_to_be_done):
                boost += 0.3
            
            score = similarity * boost
            
            scored_sections.append({
                "document": section.get("document", "unknown.pdf"),
                "page": section.get("page", 1),
                "section_title": section.get("section_title", "Untitled"),
                "importance_rank": score
            })
        
        # Sort by score and assign ranks
        scored_sections.sort(key=lambda x: x["importance_rank"], reverse=True)
        
        for i, section in enumerate(scored_sections):
            section["importance_rank"] = i + 1
        
        return scored_sections
    
    def _contains_keywords(self, text: str, persona: str, job: str) -> bool:
        """Check if text contains relevant keywords from persona/job"""
        text_lower = text.lower()
        
        # Extract key terms from persona and job
        persona_terms = persona.lower().split()
        job_terms = job.lower().split()
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        key_terms = [term for term in persona_terms + job_terms 
                    if term not in stop_words and len(term) > 2]
        
        # Check for keyword presence
        return any(term in text_lower for term in key_terms)