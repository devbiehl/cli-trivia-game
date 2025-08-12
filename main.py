from models.play import pick_categories, ask_questions
from models.query import connect_db_default

def main():
    conn = connect_db_default()

    
    print("=== TRIVIA GAME ===")
    while True:
        cat_name = pick_categories(conn)
        difficulty = input("Difficulty (easy, medium, hard) or press Enter for random: ").strip().lower() or None
        num_qs = input("Number of Questions (blank for 1): ").strip()
        limit = int(num_qs) if num_qs else 1

        score, total = ask_questions(conn, cat=cat_name, diff=difficulty, limit=limit)
        print(f"\nFinal Score: {score}/{total}")
        rerun = input("Enter 'Y' to continue OR 'EXIT' to quit: ").strip().upper()
        if rerun == 'Y':
            continue
        elif rerun == 'EXIT':
            break
        else:
            print("ERROR: Invalid entry... Exiting.")
            break
                


if __name__ == "__main__":
    main()