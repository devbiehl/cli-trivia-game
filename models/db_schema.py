import sqlite3
import random
import os

DB_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'trivia.db'))

def connect_db(path: str | None = None) -> sqlite3.Connection:
    db_file = path or DB_PATH
    if not isinstance(db_file, (str, bytes, os.PathLike)):
        raise TypeError(f"Invalid DB path: {db_file!r}")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_table(conn):
    cur = conn.cursor()
    cur.executescript('''
                CREATE TABLE IF NOT EXISTS Category(
                    cat_id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name      TEXT NOT NULL
                    );      
                
                CREATE TABLE IF NOT EXISTS Question(
                    q_id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    question      TEXT NOT NULL,
                    q_type        TEXT NOT NULL,
                    difficulty    TEXT NOT NULL,
                    cat_id        INTEGER,
                    FOREIGN KEY (cat_id) REFERENCES Category(cat_id)
                    UNIQUE (question, difficulty, cat_id)
                    );
                      
                    
                CREATE TABLE IF NOT EXISTS Choices(
                    choice_id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    q_id          INTEGER NOT NULL,
                    choice       VARCHAR NOT NULL,
                    is_correct      INTEGER NOT NULL CHECK(is_correct IN (0,1)),
                    
                    FOREIGN KEY (q_id) REFERENCES Question(q_id) ON DELETE CASCADE
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_question_category ON Question(cat_id);
                    CREATE INDEX IF NOT EXISTS idx_choices_question ON Choices(q_id)
                    ''')

def insert_question(conn, question, q_type, difficulty, cat_id):
    cur = conn.cursor()
    question = question.strip()
    q_type = q_type.strip()
    difficulty = difficulty.strip().title()
    cur.execute("SELECT q_id FROM Question WHERE (question, difficulty) = (?, ?)",
                (question, difficulty))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO Question (question, q_type, difficulty, cat_id) VALUES (?, ?, ?, ?)",
                (question, q_type, difficulty, cat_id))
    q_id = cur.lastrowid
    return q_id

def insert_cat(conn, name):
    cur = conn.cursor()
    name = name.strip().title()
    cur.execute("SELECT cat_id FROM Category WHERE name = ?",
                (name, ))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO Category (name) VALUES (?)",
                (name, ))
    cat_id = cur.lastrowid
    return cat_id

def insert_choices(conn, q_id, incorrect, correct):
    cur = conn.cursor()
    cur.execute("SELECT choice_id FROM Choices WHERE q_id = ?",
                (q_id, ))
    row = cur.fetchone()
    if row and row[0] >= 4:
        return # skip if already inserted
    
    choices = incorrect + [correct]
    random.shuffle(choices)

    for choice in choices:
        is_correct = 1 if choice == correct else 0
        cur.execute("INSERT INTO Choices (q_id, choice, is_correct) VALUES (?, ?, ?)",
                (q_id, choice, is_correct))
    choice_id = cur.lastrowid
    return choice_id

def insert_all(conn, clean_data):
    try:
        for v in clean_data:
            question = v.get('question')
            category = v.get('category')
            difficulty = v.get('difficulty')
            q_type = v.get('q_type')
            incorrect = v.get('incorrect', [])
            correct = v.get('correct')

            cat_id = insert_cat(conn, category)
            q_id = insert_question(conn, question, q_type, difficulty, cat_id)
            
            insert_choices(conn, q_id, incorrect, correct)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Insert Error: {e}")