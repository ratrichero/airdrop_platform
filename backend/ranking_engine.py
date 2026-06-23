CHAIN_WEIGHT = {
    "Ethereum": 1.2,
    "Arbitrum": 1.1,
    "Base": 1.05,
    "Solana": 1.0,
    "Unknown": 1.0
}

def calculate_deep_score(data, funding, chain):

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

    chain_multiplier = CHAIN_WEIGHT.get(chain, 1.0)

    return round(score * chain_multiplier, 2)