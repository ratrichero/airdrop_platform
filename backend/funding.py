import requests

def fetch_defillama_protocols():
    url = "https://api.llama.fi/protocols"
    r = requests.get(url)
    data = r.json()

    projects = []
    for item in data[:20]:
        if not item.get("symbol"):
            projects.append({
                "name": item.get("name"),
                "chain": item.get("chain"),
                "url": item.get("url"),
                "funding": item.get("tvl", 0)
            })

    return projects