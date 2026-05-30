import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'reviewer.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            # Check if column exists
            cursor.execute("PRAGMA table_info(reports)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'CorrectedCode' not in columns:
                cursor.execute("ALTER TABLE reports ADD COLUMN CorrectedCode TEXT")
                print("Successfully added CorrectedCode column.")
            else:
                print("Column Already exists.")
            conn.commit()
        except Exception as e:
            print(f"Migration error: {e}")
        finally:
            conn.close()
    else:
        print("Database doesn't exist yet, it will be mapped cleanly on creation.")

if __name__ == '__main__':
    migrate()
