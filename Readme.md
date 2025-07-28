This system extracts and ranks the most relevant sections from PDF documents based on a specific persona and their job-to-be-done. Built for Adobe's "Connecting the Dots" Hackathon Round 1B.

## Features
- **PDF Parsing**: Extracts structured content from PDFs using layout-aware parsing
- **Semantic Matching**: Uses sentence embeddings to match content with persona requirements
- **Intelligent Ranking**: Ranks sections and subsections by relevance and importance
- **Offline Operation**: Runs completely offline with no internet dependencies
- **Fast Processing**: Processes 3-5 documents in under 60 seconds

## Architecture
- `main.py`: Main execution logic
- `utils/parser.py`: PDF parsing and structure extraction
- `utils/extractor.py`: Section extraction and relevance scoring
- `utils/ranker.py`: Subsection analysis and ranking

## Input Format
Place PDF files and configuration in `/app/input/`:

```json
{
  "persona": "PhD Researcher in Computational Biology",
  "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
}
```

## Output Format
Results are saved to `/app/output/result.json`:

```json
{
  "metadata": {
    "documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Prepare literature review...",
    "timestamp": "2025-07-28T17:00:00Z"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page": 5,
      "section_title": "GNN Methodologies Overview",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "page": 5,
      "refined_text": "This section discusses various GNN architectures...",
      "importance_rank": 1
    }
  ]
}
```

## Usage

### Build Docker Image
```bash
docker build --platform linux/amd64 -t persona-doc-intelligence:latest .
```

### Run Container
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  persona-doc-intelligence:latest
```

## Technical Specifications
- **Model Size**: <1GB (uses all-MiniLM-L6-v2, ~90MB)
- **Processing Time**: <60 seconds for 3-5 documents
- **CPU Only**: Compatible with AMD64 architecture
- **Offline**: No internet access required

## Dependencies
- sentence-transformers: Semantic similarity computation
- PyMuPDF: PDF parsing and text extraction
- scikit-learn: Cosine similarity calculations
- nltk: Text tokenization
- numpy: Numerical computations

## Example Use Cases

### Academic Research
- **Persona**: PhD Researcher in Computational Biology
- **Job**: Literature review on GNN methodologies
- **Documents**: Research papers on graph neural networks

### Business Analysis
- **Persona**: Investment Analyst
- **Job**: Analyze R&D trends and revenue shifts
- **Documents**: Company annual reports (2022-2024)

### Educational Content
- **Persona**: Undergraduate Chemistry Student
- **Job**: Exam preparation on reaction kinetics  
- **Documents**: Organic chemistry textbook chapters