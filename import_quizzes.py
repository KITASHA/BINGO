import json
import os
import sys

from database import get_connection


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def is_quiz_database_empty() -> bool:
    conn = get_connection()

    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM quizzes"
        ).fetchone()[0]

        return count == 0

    finally:
        conn.close()


def import_quizzes() -> int:
    json_path = resource_path("quizzes.json")

    with open(json_path, "r", encoding="utf-8") as file:
        quiz_list = json.load(file)

    conn = get_connection()
    imported_count = 0

    try:
        for quiz in quiz_list:
            question = quiz.get("question") or quiz.get("text")
            answer = quiz.get("answer")

            if not question or not answer:
                print("読み込み対象外:", quiz)
                continue

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
                    question,
                    answer,
                    quiz.get("explanation"),
                    quiz.get("image_q") or quiz.get("image"),
                    quiz.get("image_a"),
                    1 if quiz.get("fever") else 0,
                    1 if quiz.get("exclude") else 0,
                )
            )

            imported_count += 1

        conn.commit()
        return imported_count

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    count = import_quizzes()
    print(f"{count}問をSQLiteに取り込みました")