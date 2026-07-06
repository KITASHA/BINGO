import json

from database import get_connection
from main import resource_path


def import_quizzes():
    with open(
        resource_path("quizzes.json"),
        encoding="utf-8"
    ) as f:
        quiz_list = json.load(f)

    conn = get_connection()

    for quiz in quiz_list:
        conn.execute(
            """
            INSERT INTO quizzes (
                number,
                question,
                answer,
                explanation,
                image_q,
                image_a,
                fever,
                exclude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                quiz.get("number"),
                quiz["question"],
                quiz["answer"],
                quiz.get("explanation"),
                quiz.get("image_q"),
                quiz.get("image_a"),
                1 if quiz.get("fever") else 0,
                1 if quiz.get("exclude") else 0
            )
        )

    conn.commit()
    conn.close()

    print("quizzes.json を SQLite に取り込みました")


if __name__ == "__main__":
    import_quizzes()