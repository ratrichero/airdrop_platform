TIER1 = ["a16z", "paradigm", "binance", "sequoia"]
TIER2 = ["dragonfly", "multicoin", "framework"]

def estimate_funding_tier(project_name):

    name_lower = project_name.lower()

    for vc in TIER1:
        if vc in name_lower:
            return 5

    for vc in TIER2:
        if vc in name_lower:
            return 4

    return 3