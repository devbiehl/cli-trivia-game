import requests
import html
import time
from models.db_handler import DBHandler
from typing import List, Dict

difficulties = ['easy', 'medium', 'hard']
categories = range(9, 33)
buffers = [1.0, 2.0, 5.0] # buffers for 429 errors

def fetch_batch(sess: requests.Session, cat: int, diff: str, amount: int = 20) -> List[Dict]:
    url = f"https://opentdb.com/api.php?amount=20&category={cat}&difficulty={diff}"
    for i, wait in enumerate([0.0] + buffers):
        if wait:
            time.sleep(wait)
        try:
            resp = sess.get(url, timeout=15)
        except requests.RequestException as e:
            if i == len(buffers):
                print(f"Network error for cat {cat}, diff {diff}: {e}")
                return []
            continue

        if resp.status_code == 429:
            # rate limit hit; try next buffer
            if i == len(buffers):
                print(f"429 Too Many Requests (cat {cat}, diff {diff}) - giving up.")
                return []
            continue

        if resp.status_code != 200:
            print(f"HTTP {resp.status_code} - cat {cat}, diff {diff}")
            return []
        
        payload = resp.json()
        if payload.get("response_code") != 0:
            # 0=Success, 1=NoResult, other=error
            print(f"No data - cat {cat}, diff {diff}, code={payload.get('response_code')}")
            return
        
        return payload.get("results", [])
    return [] # shouldnt hit this

def clean_records(raw: List[Dict]) -> List[Dict]:
    cleaned = []
    for entry in raw:
        correct = html.unescape(entry.get('correct_answer', 'Unknown'))
        incorrect = [html.unescape(ans) for ans in entry.get('incorrect_answers', [])]
        cleaned.append({
            'q_type': entry.get('type', 'Unknown'),
            'difficulty': entry.get('difficulty', 'Unknown'),
            'category': entry.get('category', 'Unknown'),
            'question': html.unescape(entry.get('question', 'Unknown')),
            'correct': correct,
            'incorrect': incorrect
            })
    return cleaned

def main():
    # One session + one DB handle for whole run
    sess = requests.Session()
    db = DBHandler()

    seen = set()
    total_saved = 0

    for cat in categories:
        for diff in difficulties:
            print(f"\nFetching category {cat}, difficulty: {diff}")
            raw = fetch_batch(sess, cat, diff, amount=20)
            if not raw:
                continue

            clean_data = clean_records(raw)

            batch = []
            for r in clean_data:
                key = (r["question"].lower(), r["difficulty"].lower(), r["category"].lower())
                if key in seen:
                    continue
                seen.add(key)
                batch.append(r)

            if not batch:
                print("Nothing new to save (all duplicates)")
                continue

            print(f"Number of items to save: {len(batch)}")
            try:
                db.save_to_db(batch)
                total_saved += len(batch)
                print("SAVE SUCCESSFUL")
            except Exception as e:
                print(f"DB save error: {e}")

            time.sleep(1.5) # baseline pace buffer for 429 errors

    print(f"\nDone. Total saved this run: {total_saved}")

if __name__ == "__main__":
        main()