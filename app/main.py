import json
import os
from datetime import datetime
from processor import process_documents



def main():
    input_dir = "/app/input"
    output_dir = "/app/output"

    # You may load the persona and job-to-be-done from a config or hardcode for now
    with open("/app/app/persona_config.json", "r") as f:
        persona_input = json.load(f)

    documents = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".pdf")]
    output = process_documents(documents, persona_input)

    output['metadata']['timestamp'] = datetime.utcnow().isoformat()

    with open(os.path.join(output_dir, "output.json"), "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
