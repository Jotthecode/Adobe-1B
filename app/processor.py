from PyPDF2 import PdfReader
from util import extract_sections, rank_sections

def process_documents(doc_paths, persona_data):
    extracted = []
    refined = []

    for path in doc_paths:
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            sections = extract_sections(text)
            ranked = rank_sections(sections, persona_data)

            for idx, sec in enumerate(ranked):
                extracted.append({
                    "document": path.split("/")[-1],
                    "page_number": i + 1,
                    "section_title": sec,
                    "importance_rank": idx + 1
                })
                refined.append({
                    "document": path.split("/")[-1],
                    "refined_text": sec,
                    "page_number": i + 1
                })

    return {
        "metadata": {
            "documents": [d.split("/")[-1] for d in doc_paths],
            "persona": persona_data["persona"],
            "job_to_be_done": persona_data["job_to_be_done"]
        },
        "extracted_sections": extracted,
        "subsection_analysis": refined
    }
