
def extract_sections(text):
    """Splits page text into candidate sections."""
    return [s.strip() for s in text.split("\n") if 20 < len(s.strip()) < 300]


def rank_sections(sections, persona_data):
    """Ranks sections based on persona expertise and job needs."""
    keywords = []

    # Collect keywords from multiple persona areas
    keywords += persona_data["persona"]["role"].lower().split()
    keywords += persona_data["persona"]["domain"].lower().split()
    keywords += [kw.lower() for kw in persona_data["persona"].get("expertise", [])]
    keywords += [kw.lower() for kw in persona_data["persona"].get("information_needs", [])]
    keywords += persona_data["job_to_be_done"]["task_description"].lower().split()
    keywords += [kw.lower() for kw in persona_data["job_to_be_done"].get("expected_output", [])]

    # Flatten to words only
    keyword_set = set()
    for phrase in keywords:
        keyword_set.update(phrase.split())

    def score(section):
        return sum(kw in section.lower() for kw in keyword_set)

    return sorted(sections, key=score, reverse=True)[:5]
