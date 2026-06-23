def calculate_score(legitimacy, complexity, capital):
    base = legitimacy * 2
    penalty = complexity + (capital / 20)
    return round(base - penalty, 2)

def is_low_cost(legitimacy, complexity, capital, risk):
    if legitimacy < 3:
        return False
    if complexity > 3:
        return False
    if capital > 50:
        return False
    if risk == "high":
        return False
    return True