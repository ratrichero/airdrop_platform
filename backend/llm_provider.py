import os
import requests
import json

GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def call_groq(prompt):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_KEY}",
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
        params={"key": GEMINI_KEY},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=20
    )
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

def analyze_text(text):
    prompt = f"""
Return ONLY valid JSON:

{{
 "legitimacy": 1-5,
 "complexity": 1-5,
 "capital": number,
 "risk": "low/medium/high",
 "strategy": "short suggestion"
}}

{text[:4000]}
"""
    try:
        output = call_groq(prompt)
    except:
        output = call_gemini(prompt)

    return json.loads(output)