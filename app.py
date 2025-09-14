# app.py

from flask import Flask, request, jsonify, render_template
import pandas as pd
from waitress import serve
import sys

# --- Import your matcher logic ---
from matcher.preprocessing import load_and_clean_dataset
from matcher.features import pre_filter_score
from matcher.scoring import rank_candidates
from matcher.llm_utils import extract_job_info_from_text, is_available
from matcher.llm_utils import get_friendly_chat_response, extract_job_info_from_text, is_available

# --- Initialize Flask App ---
app = Flask(__name__)

# --- Global Initialization ---
CANDIDATES_TO_SCORE_WITH_AI = 30
TOP_N_RESULTS = 10

df_candidates = None
try:
    df_candidates = load_and_clean_dataset("data/Talent Profiles.csv")
    print(f"✅ Successfully loaded {len(df_candidates)} candidate profiles.")
except Exception as e:
    print(f"🚨 CRITICAL ERROR: Failed to load candidate data: {e}")
    sys.exit(1)

if not is_available('openai') and not is_available('gemini'):
    print("🚨 CRITICAL ERROR: No LLM providers are available.")
    sys.exit(1)


# ==============================================================================
# --- Frontend Route ---
# ==============================================================================
@app.route('/')
def home():
    """Renders the main dashboard HTML page."""
    return render_template('index.html')


# ==============================================================================
# --- Backend API Route ---
# ==============================================================================
@app.route('/api/find_matches', methods=['POST'])
def find_matches_api():
    """Receives a job description, processes it, and returns top candidates."""
    try:
        data = request.get_json()
        job_prompt = data.get('job_description')

        if not job_prompt:
            return jsonify({"error": "Job description cannot be empty."}), 400

        # Step 1: Parse job description
        # This uses the simplified extract_job_info_from_text which has a fixed set of fields
        job_details = extract_job_info_from_text(job_prompt)
        if not job_details:
            return jsonify({"error": "Could not parse job description."}), 500

        # Step 2 & 3: Filter and Score
        df_candidates["pre_score"] = df_candidates.apply(lambda row: pre_filter_score(row, job_details), axis=1)
        top_prospects_df = df_candidates.sort_values(by="pre_score", ascending=False).head(CANDIDATES_TO_SCORE_WITH_AI)
        top_candidates_df = rank_candidates(top_prospects_df, job_details, top_n=TOP_N_RESULTS)

        # Step 4: Format and return results
        results = top_candidates_df.to_dict(orient='records')
        return jsonify(results)

    except Exception as e:
        print(f"🚨 An error occurred in /api/find_matches: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500


@app.route('/api/ai_chat', methods=['POST'])
def ai_chat_api():
    """Handles messages for the friendly AI assistant."""
    try:
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "Message cannot be empty."}), 400

        # Call our new LLM function to get a friendly reply
        ai_reply = get_friendly_chat_response(user_message)

        return jsonify({"reply": ai_reply})

    except Exception as e:
        print(f"🚨 An error occurred in /api/ai_chat: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

# ==============================================================================
# --- Run the Server ---
# ==============================================================================
if __name__ == '__main__':
    print("🚀 Starting AI Talent Dashboard server...")
    serve(app, host='0.0.0.0', port=8080)