import sqlite3
import threading

class Database:
    def __init__(self, db_name="system_data.db"):
        self.db_name = db_name
        self.lock = threading.Lock()  # Lock for transactional updates
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.initialize_tables()

    def initialize_tables(self):
        with self.lock:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS taxis (
                    id INTEGER PRIMARY KEY,
                    position TEXT,
                    status TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    services_successful INTEGER,
                    services_rejected INTEGER
                )
            """)
            self.conn.commit()

    def update_taxi(self, taxi_id, position, status):
        with self.lock:
            self.cursor.execute("""
                INSERT OR REPLACE INTO taxis (id, position, status)
                VALUES (?, ?, ?)
            """, (taxi_id, position, status))
            self.conn.commit()

    def update_metrics(self, successful, rejected):
        with self.lock:
            self.cursor.execute("""
                INSERT INTO metrics (services_successful, services_rejected)
                VALUES (?, ?)
            """, (successful, rejected))
            self.conn.commit()

    def get_taxis(self):
        with self.lock:
            self.cursor.execute("SELECT * FROM taxis")
            return self.cursor.fetchall()

    def get_metrics(self):
        with self.lock:
            self.cursor.execute("SELECT * FROM metrics")
            return self.cursor.fetchall()

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = Database()
    db.update_taxi(1, "(5,5)", "available")
    db.update_metrics(10, 2)
    print(db.get_taxis())
    print(db.get_metrics())
