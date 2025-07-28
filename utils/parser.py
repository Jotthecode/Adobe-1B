import fitz  # PyMuPDF
import re
from typing import List, Dict, Any
from pathlib import Path

class PDFParser:
    """PDF parser that extracts structured content from PDFs"""
    
    def __init__(self):
        self.heading_patterns = [
            r'^\d+\.\s+',  # 1. 2. 3.
            r'^\d+\.\d+\s+',  # 1.1 1.2
            r'^\d+\.\d+\.\d+\s+',  # 1.1.1
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS HEADINGS
            r'^[A-Z][a-z\s]+:',  # Title Case with colon
        ]
    
    def parse_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Parse PDF and extract structured sections"""
        sections = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text blocks with formatting info
                blocks = page.get_text("dict")
                
                for block in blocks["blocks"]:
                    if "lines" not in block:
                        continue
                    
                    for line in block["lines"]:
                        line_text = ""
                        avg_font_size = 0
                        font_flags = 0
                        
                        for span in line["spans"]:
                            line_text += span["text"]
                            avg_font_size += span["size"]
                            font_flags |= span["flags"]
                        
                        if line["spans"]:
                            avg_font_size /= len(line["spans"])
                        
                        line_text = line_text.strip()
                        
                        if len(line_text) > 10:  # Filter out very short text
                            section = {
                                "text": line_text,
                                "page": page_num + 1,
                                "font_size": avg_font_size,
                                "is_bold": bool(font_flags & 2**4),
                                "bbox": line["bbox"]
                            }
                            
                            # Classify as heading or content
                            section["is_heading"] = self._is_heading(line_text, avg_font_size, font_flags)
                            sections.append(section)
            
            doc.close()
            
        except Exception as e:
            print(f"Error parsing PDF {pdf_path}: {e}")
            return []
        
        return self._post_process_sections(sections)
    
    def _is_heading(self, text: str, font_size: float, font_flags: int) -> bool:
        """Determine if text is likely a heading"""
        # Check font formatting
        is_bold = bool(font_flags & 2**4)
        is_large = font_size > 12
        
        # Check text patterns
        matches_pattern = any(re.match(pattern, text) for pattern in self.heading_patterns)
        
        # Short and formatted text is likely a heading
        is_short_formatted = len(text) < 100 and (is_bold or is_large)
        
        return matches_pattern or is_short_formatted
    
    def _post_process_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Post-process sections to create coherent content blocks"""
        processed = []
        current_section = None
        
        for section in sections:
            if section["is_heading"]:
                # Save previous section if exists
                if current_section:
                    processed.append(current_section)
                
                # Start new section
                current_section = {
                    "section_title": section["text"],
                    "page": section["page"],
                    "content": "",
                    "font_size": section["font_size"]
                }
            else:
                # Add content to current section
                if current_section:
                    current_section["content"] += " " + section["text"]
                else:
                    # Create section for orphaned content
                    current_section = {
                        "section_title": "Content",
                        "page": section["page"],
                        "content": section["text"],
                        "font_size": section["font_size"]
                    }
        
        # Add final section
        if current_section:
            processed.append(current_section)
        
        return processed