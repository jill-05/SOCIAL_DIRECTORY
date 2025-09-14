# matcher/llm_utils.py

import os
import json
import re
import time
import sys

# --- Import API libraries ---
from openai import OpenAI, RateLimitError, AuthenticationError
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
from google.auth.exceptions import DefaultCredentialsError

# --- Initialize BOTH clients (globally, with error handling) ---
openai_client = None
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
        print("✅ OpenAI client initialized successfully (globally).")
    else:
        print("⚠️ OPENAI_API_KEY not found. OpenAI client will not be available.")
except AuthenticationError:
    print("🚨 Failed to initialize OpenAI client globally: OPENAI_API_KEY is missing or invalid.")
except Exception as e:
    print(f"🚨 Failed to initialize OpenAI client globally: {type(e).__name__} - {e}")

GEMINI_MODEL = None
try:
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        GEMINI_MODEL = genai.GenerativeModel("gemini-1.5-flash")
        print("✅ Gemini client initialized successfully (globally).")
    else:
        print("⚠️ GOOGLE_API_KEY not found. Gemini client will not be available.")
except DefaultCredentialsError:
    print("🚨 Failed to initialize Gemini client globally: GOOGLE_API_KEY is missing or invalid.")
except Exception as e:
    print(f"🚨 Failed to initialize Gemini client globally: {type(e).__name__} - {e}")

# --- Models ---
OPENAI_MODEL_NAME = "gpt-3.5-turbo"


# --- Utility Functions ---
def _optimize_prompt(prompt: str) -> str:
    """Optimize prompt for faster processing."""
    if len(prompt) > 500:
        prompt = prompt[:450] + "... Please provide a concise response."
    return prompt


def is_available(provider: str) -> bool:
    """Check if a specific LLM provider is available."""
    if provider.lower() == 'openai':
        return openai_client is not None
    if provider.lower() == 'gemini':
        return GEMINI_MODEL is not None
    return False


def clean_json_response(content: str) -> str:
    """Remove ```json ... ``` fences if the model returns them."""
    if content.startswith("```"):
        content = re.sub(r"^```(json)?|```$", "", content, flags=re.MULTILINE).strip()
    return content


# ==============================================================================
# --- DYNAMIC EXTRACTION FUNCTIONS (THESE ARE THE CHANGES) ---
# ==============================================================================

def extract_job_info_from_text(text: str, fields_to_extract: list) -> dict:
    """
    Tries to extract job info with OpenAI, falls back to Gemini on failure.
    Dynamically builds the prompt based on the fields_to_extract list.
    """
    # Use a default set of fields if the user provides none, ensuring scoring can work.
    if not fields_to_extract:
        fields_to_extract = ["hiring_creator_name", "location_pref", "job_types", "relevant_skills",
                             "personality_traits", "budget_monthly", "content_verticals"]

    if is_available('openai'):
        try:
            print("-> Extracting job info with OpenAI...")
            return _openai_extract_job_info(text, fields_to_extract)
        except (RateLimitError, Exception) as e:
            print(f"⚠️ OpenAI failed ({type(e).__name__}). Switching to Gemini fallback.")

    if is_available('gemini'):
        try:
            print("-> Extracting job info with Gemini...")
            return _gemini_extract_job_info(text, fields_to_extract)
        except Exception as e2:
            print(f"🚨 Fallback API (Gemini) also failed: {e2}")

    print("🚨 All LLM providers failed. Cannot extract job info.")
    return {}


def _openai_extract_job_info(text: str, fields_to_extract: list) -> dict:
    """Dynamically creates a prompt for OpenAI based on user-defined fields."""
    # Convert the list of fields into a formatted string for the prompt
    fields_str = "\n- ".join(fields_to_extract)

    system_prompt = "You are an AI assistant that extracts structured talent profile information into a valid JSON object. Extract only the fields the user requests."
    user_prompt = f"From the job description below, please extract the following fields:\n- {fields_str}\n\nJob Description:\n\"\"\" \n{text}\n\"\"\""

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)


def _gemini_extract_job_info(text: str, fields_to_extract: list) -> dict:
    """Dynamically creates a prompt for Gemini based on user-defined fields."""
    # Convert the list of fields into a formatted string for the prompt
    fields_str = "\n- ".join(fields_to_extract)

    prompt = f"You are an AI assistant. From the job description below, extract the following fields into a valid JSON object:\n- {fields_str}\n\nJob Description:\n\"\"\" \n{text}\n\"\"\""

    response = GEMINI_MODEL.generate_content(prompt)
    content = clean_json_response(response.text.strip())
    return json.loads(content)


# ==============================================================================
# --- SCORING FUNCTIONS (NO CHANGES NEEDED HERE) ---
# ==============================================================================

def llm_score_candidate_aspects(candidate: dict, job: dict) -> dict:
    """
    Tries to score aspects with OpenAI, falls back to Gemini on failure.
    This function remains fixed to ensure consistent scoring.
    """
    if is_available('openai'):
        try:
            print("-> Scoring with OpenAI...")
            return _openai_score_candidate_aspects(candidate, job)
        except (RateLimitError, Exception) as e:
            print(f"⚠️ OpenAI failed ({type(e).__name__}). Switching to Gemini fallback.")

    if is_available('gemini'):
        try:
            print("-> Scoring with Gemini...")
            return _gemini_score_candidate_aspects(candidate, job)
        except Exception as e2:
            print(f"🚨 Fallback API (Gemini) also failed: {e2}")

    print("🚨 All LLM providers failed. Returning zero scores.")
    return {"skills_score": 0.0, "jobtype_score": 0.0, "trait_score": 0.0}


def _openai_score_candidate_aspects(candidate: dict, job: dict) -> dict:
    # This function is unchanged.
    if not openai_client:
        raise RuntimeError("OpenAI client not initialized.")
    system_prompt = "You are an expert talent evaluator. Return a valid JSON with keys 'skills_score', 'jobtype_score', 'trait_score' (floats from 0.0 to 1.0)."
    user_prompt = f"Candidate Skills: {candidate.get('Skills_list', [])}\nJob Skills: {job.get('relevant_skills', [])}\n\nCandidate Job Types: {candidate.get('JobTypes_list', [])}\nJob Types: {job.get('job_types', [])}\n\nCandidate Profile: {candidate.get('Profile_clean', '')}\nJob Traits: {job.get('personality_traits', [])}"

    optimized_user_prompt = _optimize_prompt(user_prompt)

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": optimized_user_prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)


def _gemini_score_candidate_aspects(candidate: dict, job: dict) -> dict:
    # This function is unchanged.
    if not GEMINI_MODEL:
        raise RuntimeError("Gemini model not initialized.")
    prompt = f"You are an expert talent evaluator. On a scale of 0.0 to 1.0, provide scores for Skill Match, Job Type Match, and Personality Alignment. Return a valid JSON with keys 'skills_score', 'jobtype_score', 'trait_score'.\n\nCandidate Skills: {candidate.get('Skills_list', [])}\nJob Skills: {job.get('relevant_skills', [])}\n\nCandidate Job Types: {candidate.get('JobTypes_list', [])}\nJob Types: {job.get('job_types', [])}\n\nCandidate Profile: {candidate.get('Profile_clean', '')}\nJob Traits: {job.get('personality_traits', [])}"

    optimized_prompt = _optimize_prompt(prompt)

    response = GEMINI_MODEL.generate_content(optimized_prompt)
    content = clean_json_response(response.text.strip())
    return json.loads(content)


def get_friendly_chat_response(user_message: str) -> str:
    """
    Gets a friendly response from an LLM for the chat agent.
    Tries OpenAI first, then falls back to Gemini.
    """
    if is_available('openai'):
        try:
            return _openai_get_chat_response(user_message)
        except Exception as e:
            print(f"⚠️ OpenAI chat failed ({type(e).__name__}). Switching to Gemini fallback.")

    if is_available('gemini'):
        try:
            return _gemini_get_chat_response(user_message)
        except Exception as e2:
            print(f"🚨 Fallback API (Gemini) for chat also failed: {e2}")

    return "I'm sorry, I'm having trouble connecting right now. Please try again later."


def _openai_get_chat_response(user_message: str) -> str:
    """Gets a chat response from OpenAI."""
    system_prompt = "You are a friendly and helpful AI assistant for a talent dashboard. Your name is Eva. Keep your answers concise and cheerful."

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}])
    return response.choices[0].message.content


def _gemini_get_chat_response(user_message: str) -> str:
    """Gets a chat response from Gemini."""
    # Gemini works better with the instruction integrated into the prompt
    prompt = f"You are a friendly and helpful AI assistant for a talent dashboard named Eva. Keep your answer concise and cheerful.\n\nUSER: {user_message}\nEVA:"

    response = GEMINI_MODEL.generate_content(prompt)
    return response.text