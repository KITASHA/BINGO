from database import get_connection

conn = get_connection()

rows = conn.execute(
    "SELECT * FROM quizzes"
).fetchall()

for row in rows[:5]:
    print(dict(row))

print(f"\n件数: {len(rows)}件")

conn.close()