import requests

def fetch_defillama(limit=20):
    r = requests.get("https://api.llama.fi/protocols", timeout=10)
    data = r.json()

    projects = []

    for item in data[:limit]:
        projects.append({
            "name": item.get("name"),
            "chain": item.get("chain", "Unknown"),
            "funding": item.get("tvl", 0),
            "has_token": bool(item.get("symbol"))
        })

    return projects

def is_candidate(project):

    name = project["name"].lower()

    # Skip CEX
    if any(x in name for x in ["binance", "okx", "bitfinex", "bybit", "robinhood"]):
        return False

    # Skip giant protocols
    if project["funding"] > 5_000_000_000:
        return False

    return True