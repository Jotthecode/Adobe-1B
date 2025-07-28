import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from utils.parser import PDFParser
from utils.extractor import ContentExtractor
from utils.ranker import PersonaRanker

def load_input_config() -> Dict[str, Any]:
    """Load persona and job configuration from input directory"""
    config_path = Path("/app/input/config.json")
    
    # Default configuration if not provided
    default_config = {
        "persona": "Research Analyst",
        "job_to_be_done": "Extract key insights and findings from documents"
    }
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    else:
        return default_config

def main():
    """Main execution function"""
    start_time = time.time()
    
    # Initialize components
    parser = PDFParser()
    extractor = ContentExtractor()
    ranker = PersonaRanker()
    
    # Load configuration
    config = load_input_config()
    persona = config.get("persona", "Research Analyst")
    job_to_be_done = config.get("job_to_be_done", "Extract key insights")
    
    # Get all PDF files from input directory
    input_dir = Path("input")
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Processing {len(pdf_files)} PDF files...")
    print(f"Persona: {persona}")
    print(f"Job: {job_to_be_done}")
    
    # Parse all PDFs
    all_sections = []
    document_names = []
    
    for pdf_file in pdf_files:
        print(f"Parsing {pdf_file.name}...")
        try:
            sections = parser.parse_pdf(str(pdf_file))
            for section in sections:
                section['document'] = pdf_file.name
            all_sections.extend(sections)
            document_names.append(pdf_file.name)
        except Exception as e:
            print(f"Error parsing {pdf_file.name}: {e}")
            continue
    
    if not all_sections:
        print("No sections extracted from PDFs")
        return
    
    print(f"Extracted {len(all_sections)} sections total")
    
    # Extract and rank relevant content
    extracted_sections = extractor.extract_relevant_sections(
        all_sections, persona, job_to_be_done
    )
    
    subsection_analysis = ranker.rank_subsections(
        all_sections, persona, job_to_be_done
    )
    
    # Prepare output
    result = {
        "metadata": {
            "documents": document_names,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections[:20],  # Top 20 sections
        "subsection_analysis": subsection_analysis[:30]  # Top 30 subsections
    }
    
    # Save result
    output_path = Path("output/result.json")
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    processing_time = time.time() - start_time
    print(f"Processing completed in {processing_time:.2f} seconds")
    print(f"Result saved to {output_path}")

if __name__ == "__main__":
    main()