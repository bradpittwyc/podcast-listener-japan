import requests, json
from concurrent.futures import ThreadPoolExecutor

def fetch_genre(g):
    try:
        url = f'https://itunes.apple.com/jp/rss/toppodcasts/limit=1/genre={g}/json'
        r = requests.get(url, timeout=4).json()
        label = r.get('feed', {}).get('title', {}).get('label', '')
        if label:
            # Format: iTunes Store: Top Podcasts in <Category> for Japan
            # Or in Japanese: iTunes Store: ポッドキャスト - <Category>
            clean = label.replace('iTunes Store: ', '').replace('iTunes Store：', '')
            return (g, clean)
    except Exception:
        pass
    return None

with ThreadPoolExecutor(max_workers=20) as ex:
    results = list(ex.map(fetch_genre, range(1300, 1550)))

genres = {k: v for res in results if res for k, v in [res]}
with open("jp_genres.json", "w", encoding="utf-8") as f:
    json.dump(genres, f, ensure_ascii=False, indent=2)

print(f"Scanned {len(genres)} Japanese categories.")
for k, v in sorted(genres.items()):
    print(f"ID {k}: {v}")
