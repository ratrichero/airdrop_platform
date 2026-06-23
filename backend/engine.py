import requests
from datetime import datetime
from llm import deep_analyze

CHAIN_WEIGHT = {
    "Ethereum": 1.2,
    "Arbitrum": 1.1,
    "Base": 1.05,
    "Solana": 1.0,
    "Unknown": 1.0
}

def fetch_defillama(limit=20):
    r = requests.get("https://api.llama.fi/protocols", timeout=10)
    data = r.json()
    return data[:limit]

def calculate_score(data, funding, chain):

    score = 0
    score += data["retro_probability"] * 40
    score += data["snapshot_likelihood"] * 20
    score += data["funding_tier"] * 5
    score -= data["effort_level"] * 5
    score -= data["sybil_strength"] * 3

    if data["capital_required"] < 30:
        score += 5

    if funding > 20_000_000:
        score += 10

    multiplier = CHAIN_WEIGHT.get(chain, 1.0)

    return round(score * multiplier, 2)

def apply_decay(score, created_at):
    days = (datetime.utcnow() - created_at).days
    decay = 1 - (days * 0.02)
    if decay < 0.5:
        decay = 0.5
    return round(score * decay, 2)

def classify_sybil(data):
    if data["sybil_strength"] >= 4:
        return "Hard"
    if data["effort_level"] <= 2 and data["capital_required"] < 10:
        return "Farmable"
    return "Medium"