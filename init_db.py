from bingo.database import get_connection
from bingo.models import CREATE_QUIZZES_TABLE


def init_db():
    conn = get_connection()

    conn.execute(CREATE_QUIZZES_TABLE)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("DBを作成しました")