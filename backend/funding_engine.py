import requests

def fetch_defillama_projects(limit=20):
    url = "https://api.llama.fi/protocols"
    r = requests.get(url, timeout=10)
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