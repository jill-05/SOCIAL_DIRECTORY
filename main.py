import pandas as pd
from matcher.preprocessing import load_and_clean_dataset
from matcher.features import extract_hobbies, pre_filter_score
from matcher.scoring import rank_candidates
from matcher.llm_utils import extract_job_info_from_text
import os


# Load and preprocess candidate profiles
df = load_and_clean_dataset("data/Talent Profiles.csv")
df["hobbies"] = df["Profile_clean"].apply(extract_hobbies)

# Parse job description using LLM
job_prompt = """
●	https://www.youtube.com/@aliabdaal is hiring a Chief Operation Officer to run their channel in productivity. They welcome anyone with a background in Strategy & Consulting, Business operations or Development. This person needs to have high energy and a lot of passion for educational content. They don’t have any budget limitation and are willing to hire the best talent for the role.
"""
job = extract_job_info_from_text(job_prompt)

# Score and rank
top_candidates = rank_candidates(df, job, top_n=10)

# Display top matches
print(top_candidates)