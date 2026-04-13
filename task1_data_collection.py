import requests
import time
import json
import os
from datetime import datetime

def assign_category(title):
    if not title:
        return "other"
    
    t = title.lower()

    if any(word in t for word in ["ai", "tech", "software", "code", "computer", "data", "cloud", "api", "gpu", "llm","startup","app"]):
        return "technology"
    elif any(word in t for word in ["war", "government","country", "president", "election", "climate", "attack","policy"]):
        return "worldnews"
    elif any(word in t for word in ["nfl", "nba", "fifa", "sport", "game", "team", "player","match"]):
        return "sports"
    elif any(word in t for word in ["research", "study", "space", "physics", "biology", "nasa","experiment"]):
        return "science"
    elif any(word in t for word in ["movie", "film", "music", "netflix", "show", "award","series"]):
        return "entertainment"
    else:
        return "technology"
url = "https://hacker-news.firebaseio.com/v0/topstories.json"
headers = {"User-Agent": "TrendPulse/1.0"}

response = requests.get(url, headers=headers)
story_ids = response.json()[:500]
results = []

category_limit = {
    "technology": 0,
    "worldnews": 0,
    "sports": 0,
    "science": 0,
    "entertainment": 0,
    "other":0
}

MAX_PER_CATEGORY = 40

for sid in story_ids:
    try:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
        res = requests.get(item_url, headers=headers)
        story = res.json()

        if not story or "title" not in story:
            continue

        category = assign_category(story["title"])

        if category not in category_limit:
            continue

        if category_limit[category] >= MAX_PER_CATEGORY:
            continue

        data = {
            "post_id": story.get("id"),
            "title": story.get("title"),
            "category": category,
            "score": story.get("score", 0),
            "num_comments": story.get("descendants", 0),
            "author": story.get("by", "unknown"),
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        results.append(data)
        category_limit[category] += 1

        
        if sum(category_limit.values()) >= 125:
            break

    except Exception as e:
        print("Error fetching story:", sid)

if not os.path.exists("data"):
    os.makedirs("data")
filename = f"data/trends_{datetime.now().strftime('%Y%m%d')}.json"

with open(filename, "w") as f:
    json.dump(results, f, indent=4)

print(f"Collected {len(results)} stories. Saved to {filename}")
