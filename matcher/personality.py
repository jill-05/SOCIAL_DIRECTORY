import re

PERSONALITY_KEYWORDS = {
    "collaborative": ["team player", "collaborate", "group work"],
    "detail-oriented": ["attention to detail", "meticulous", "organized"],
    "funny": ["humor", "funny", "entertaining"],
    "creative": ["creative", "original", "innovative"],
    "fast learner": ["quick learner", "adaptable", "flexible"],
}

def extract_traits(text: str):
    text = text.lower()
    traits = set()
    for trait, keywords in PERSONALITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                traits.add(trait)
    return list(traits)

def trait_score(candidate_traits, job_traits):
    if not job_traits:
        return 0.5  # neutral score
    return len(set(candidate_traits) & set(job_traits)) / max(1, len(job_traits))
