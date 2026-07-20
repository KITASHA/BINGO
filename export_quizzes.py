from database import get_connection


def get_export_quizzes() -> list[dict]:
    """
    DBに登録されているクイズを、
    JSONへ変換できる辞書の一覧として取得する。
    """

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                number,
                question,
                answer,
                explanation,
                image_q,
                image_a,
                fever,
                exclude
            FROM quizzes
            ORDER BY id ASC
            """
        ).fetchall()

        quizzes = []

        for row in rows:
            quizzes.append(
                {
                    "number": row["number"],
                    "question": row["question"],
                    "answer": row["answer"],
                    "explanation": row["explanation"],
                    "image_q": row["image_q"],
                    "image_a": row["image_a"],
                    "fever": row["fever"],
                    "exclude": row["exclude"],
                }
            )

        return quizzes

    finally:
        conn.close()