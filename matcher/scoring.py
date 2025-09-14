# matcher/scoring.py

import re
from matcher.features import (
    location_score,
    budget_score,
    vertical_score, # This will call embedding_similarity from features
    creator_history_score
)
from matcher.llm_utils import llm_score_candidate_aspects


def score_candidate(candidate: dict, job: dict) -> float:
    """Compute weighted candidate-job compatibility score with LLM + features."""

    # --- LLM scores (Calls directly) ---
    llm_scores = llm_score_candidate_aspects(candidate, job)

    skills_sim = llm_scores.get("skills_score", 0.0)
    jobtype_sim = llm_scores.get("jobtype_score", 0.0)
    trait_sim = llm_scores.get("trait_score", 0.0)

    # --- Feature scores ---
    loc_sim = location_score(candidate.get("Country", ""), job.get("location_pref", "anywhere"))

    job_budget_str = str(job.get("budget_monthly", "inf"))
    job_budget_monthly = float("inf")
    if re.search(r'\d', job_budget_str):
        job_budget_monthly = float(re.search(r'\d+', job_budget_str).group())

    budget_sim = budget_score(candidate.get("Monthly Rate", float("inf")), job_budget_monthly)

    # vertical_score and creator_history_score are imported from features.py
    # features.py will import embedding_similarity from similarity.py
    vertical_sim = vertical_score(candidate.get("Content Verticals", []), job.get("content_verticals", []))
    creator_sim = creator_history_score(candidate.get("Creators Worked With", []), job.get("hiring_creator_name", ""))

    # --- Weighted final score ---
    final_score = (
            0.25 * skills_sim +
            0.15 * jobtype_sim +
            0.15 * trait_sim +
            0.10 * vertical_sim +
            0.10 * budget_sim +
            0.05 * loc_sim +
            0.05 * creator_sim
    )

    return round(final_score, 4)


def rank_candidates(df, job, top_n=10):
    """Score all candidates and return top N."""
    df = df.copy()
    df["match_score"] = df.apply(lambda row: score_candidate(row, job), axis=1)
    return df.sort_values(by="match_score", ascending=False).head(top_n)