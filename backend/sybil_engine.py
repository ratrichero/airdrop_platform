def classify_sybil(data):

    if data["sybil_strength"] >= 4:
        return "Hard"

    if data["effort_level"] <= 2 and data["capital_required"] < 10:
        return "Farmable"

    return "Medium"