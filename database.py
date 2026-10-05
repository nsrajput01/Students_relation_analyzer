import sqlite3

DATABASE = "students.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()

    # Students table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            branch TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)

    # Relations table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student1_id INTEGER NOT NULL,
            student2_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            FOREIGN KEY (student1_id) REFERENCES students(id),
            FOREIGN KEY (student2_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()