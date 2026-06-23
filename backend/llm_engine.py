import requests
import json
from .config import GROQ_API_KEY, GEMINI_API_KEY

PROMPT = """
You are a professional retroactive airdrop analyst.

Return ONLY valid JSON:

{
  "retro_probability": 0-1,
  "snapshot_likelihood": 0-1,
  "funding_tier": 1-5,
  "effort_level": 1-5,
  "sybil_strength": 1-5,
  "capital_required": number,
  "strategy": "short actionable strategy"
}

Project info:
"""

def call_groq(prompt):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        },
        timeout=20
    )
    return r.json()["choices"][0]["message"]["content"]

def call_gemini(prompt):
    r = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        params={"key": GEMINI_API_KEY},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=20
    )
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

def deep_analyze(text):

    full_prompt = PROMPT + text[:3000]

    try:
        output = call_groq(full_prompt)
    except:
        output = call_gemini(full_prompt)

    return json.loads(output)