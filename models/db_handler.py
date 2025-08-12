from .db_schema import DB_PATH, connect_db, create_table, insert_all
import sqlite3
from typing import List, Dict, Optional

class DBHandler:
    def __init__(self, DB_PATH: Optional[str] = None):
        self.conn: sqlite3.Connection = connect_db(DB_PATH)
        create_table(self.conn) # ensures table exits once

    def save_to_db(self, clean_data: List[Dict]) -> int:
        if not clean_data:
            print("Nothing to save.")
            return 0
        
        try:
            print(f"Number of items to save: {len(clean_data)}")
            insert_all(self.conn, clean_data)
            self.conn.commit()
            print("SAVE SUCCESSFUL")
            return len(clean_data)
        except Exception as e:
            self.conn.rollback()
            print(f"SAVE FAILED - rolled back. Error: {e}")
            return 0
        
    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
