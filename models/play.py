import string, random
from .query import get_categories, get_difficulties_for_category, get_questions, category_counts


def pick_categories(conn):
    categories = get_categories(conn)
    print("\nAvailable Categories:\n")
    for idx, row in enumerate(categories, start=1):
        print(f"{idx}. {row['name']}")

    choice = input("\nPick a category number (or press Enter for random): ").strip()
    if choice == "":
        return None # random category
    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(categories):
            return categories[choice_idx]['name']
    except ValueError:
        pass
    print("Invalid selection.")
    return pick_categories(conn) # retry
      

def ask_questions(conn, cat=None, diff=None, limit=None):
    questions = get_questions(conn, cat, diff, limit)
    if not questions:
        print("No question found for that filter.")
        return 0, 0
    
    score = 0
    total = len(questions)

    for q in questions:
        print(f"\n[{q['category']} | {q['difficulty']}]: {q['question']}")
        labels = list(string.ascii_uppercase)[:len(q['choices'])]
        labeled = list(zip(labels, q['choices']))
        for lab, ch in labeled:
            print(f"    {lab}. {ch['text']}")

        ans = input("Your answer: ").strip()

        picked = None
        letter_map = {lab: ch for lab, ch in labeled}
        if len(ans) == 1 and ans.upper() in letter_map:
            picked = letter_map[ans.upper()]
        else:
            target = ans.strip().lower()
            for _, ch in labeled:
                if ch["text"].strip().lower() == target:
                    picked = ch
                    break
        if not picked:
            print("Couldn't understand your answer.")
            continue
        if picked['is_correct']:
            print("CORRECT!")
            score += 1
        else:
            correct_ans = next(ch["text"] for ch in q["choices"] if ch['is_correct'])
            print(f"INCORRECT! (Correct: {correct_ans})")
    return score, total