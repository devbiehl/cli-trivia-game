import sqlite3
from .db_schema import DB_PATH, connect_db


def connect_db_default() -> sqlite3.Connection:
    return connect_db(DB_PATH)

def get_categories(conn):
    sql = "SELECT cat_id, name FROM Category ORDER BY name;"
    return conn.execute(sql).fetchall()

def get_difficulties_for_category(conn, cat_name):
    sql = """
    SELECT DISTINCT q.difficulty
    FROM Question q
    JOIN Category c on q.cat_id = c.cat_id
    WHERE c.name = ?
    ORDER BY CASE LOWER(q.difficulty)
        WHEN 'easy' THEN 1 WHEN 'medium' THEN 2 WHEN 'hard' THEN 3 ELSE 99 END;
    """
    return [r["difficulty"] for r in conn.execute(sql, (cat_name,)).fetchall()]

def get_questions(conn, cat_name=None, difficulty=None, limit=None):
    params, where = [], []
    if cat_name:
        where.append("c.name = ?")
        params.append(cat_name)
    if difficulty:
        where.append("LOWER(q.difficulty) = LOWER(?)")
        params.append(difficulty)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
    SELECT q.q_id, q.question, q.q_type, q.difficulty, c.name AS category
    FROM Question q
    LEFT JOIN Category c ON q.cat_id = c.cat_id
    {where_sql}
    ORDER BY RANDOM()
    """
    if limit:
        sql += f"LIMIT {int(limit)}"


    rows = conn.execute(sql, params).fetchall()

    result = []
    for r in rows:
        # fetch choices
        choices = conn.execute(
            "SELECT choice_id, choice, is_correct FROM Choices WHERE q_id = ? ORDER BY RANDOM();",
            (r["q_id"],)
        ).fetchall()

        result.append({
            "q_id": r["q_id"],
            "question": r["question"],
            "q_type": r["q_type"],
            "difficulty": r["difficulty"],
            "category": r["category"],
            "choices": [{"text": c["choice"], "is_correct": c["is_correct"]} for c in choices]
        })
    return result

def category_counts(conn):
    sql = """
    SELECT c.name AS category,
            COUNT(*) AS num_questions,
            SUM(CASE WHEN LOWER(q.difficulty)='easy' THEN 1 ELSE 0 END) AS easy_count,
            SUM(CASE WHEN LOWER(q.difficulty)='medium' THEN 1 ELSE 0 END) AS med_count,
            SUM(CASE WHEN LOWER(q.difficulty)='hard' THEN 1 ELSE 0 END) AS hard_count
    FROM Question q
    JOIN Category c ON q.cat_id = c.cat_id
    GROUP BY c.name
    ORDER BY num_questions DESC, c.name;
    """
    return conn.execute(sql).fetchall()