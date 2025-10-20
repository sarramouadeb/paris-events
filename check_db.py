import sqlite3
import sys

def main():
    try:
        # Connect to database
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()

        # Count rows
        cursor.execute("SELECT count(*) FROM events")
        count = cursor.fetchone()[0]
        print(f"Number of events: {count}")

        # Get table info
        cursor.execute("PRAGMA table_info(events)")
        columns = cursor.fetchall()
        print("Table columns:")
        for col in columns:
            print(col)

        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()