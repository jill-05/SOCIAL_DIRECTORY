# matcher/features.py

from matcher.similarity import embedding_similarity
import re

HOBBY_KEYWORDS = ["animals", "dogs", "cats", "gaming", "music", "sports", "fashion", "travel", "art", "photography"]


def extract_hobbies(text):
    return [h for h in HOBBY_KEYWORDS if h in text.lower()]


def location_score(candidate_country: str, job_pref: str) -> float:
    if not candidate_country or not job_pref:
        return 0.0
    candidate_country, job_pref = candidate_country.lower(), job_pref.lower()
    if job_pref in candidate_country:
        return 1.0
    asia_countries = ["india", "china", "japan", "philippines", "indonesia", "thailand", "pakistan", "bangladesh"]
    if job_pref == "asia" and candidate_country in asia_countries:
        return 0.7
    return 0.3


def budget_score(candidate_rate: float, job_budget: float) -> float:
    if job_budget == float("inf"):
        return 1.0
    if candidate_rate <= job_budget:
        return 1.0
    return max(0.0, 1 - (candidate_rate - job_budget) / job_budget)


def vertical_score(candidate_verticals, job_verticals):
    cand_text = " ".join(candidate_verticals or [])
    job_text = " ".join(job_verticals or [])
    return embedding_similarity(cand_text, job_text)


def job_type_score(candidate_types, job_types):
    return embedding_similarity(" ".join(candidate_types or []), " ".join(job_types or []))


def creator_history_score(past_creators, target_creator):
    if not target_creator or not past_creators:
        return 0.0
    return 1.0 if target_creator.lower() in [c.lower() for c in past_creators] else 0.0


# --- Pre-filtering Function ---
def pre_filter_score(candidate: dict, job: dict) -> float:
    """
    Calculates a simple, fast, non-LLM score for initial filtering.
    """
    score = 0

    # Must have at least one matching skill
    job_skills = set(job.get("relevant_skills", []))
    candidate_skills = set(candidate.get("Skills_list", []))
    if job_skills and candidate_skills.intersection(job_skills):
        score += 1

    # Must have at least one matching job type
    job_types = set(job.get("job_types", []))
    candidate_job_types = set(candidate.get("JobTypes_list", []))
    if job_types and candidate_job_types.intersection(job_types):
        score += 1

    return score