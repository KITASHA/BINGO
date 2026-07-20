import json

from database import get_connection


QUIZ_FIELDS = (
    "number",
    "question",
    "answer",
    "explanation",
    "image_q",
    "image_a",
    "fever",
    "exclude",
)


INSERT_QUIZ_SQL = """
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
"""


def validate_quiz_data(quiz: dict, index: int) -> dict:
    """
    JSON内の1件のクイズを検証し、
    DB登録用の形に整える。
    """

    if not isinstance(quiz, dict):
        raise ValueError(
            f"{index + 1}件目のクイズ形式が正しくありません。"
        )

    question = str(
        quiz.get("question") or ""
    ).strip()

    answer = str(
        quiz.get("answer") or ""
    ).strip()

    if not question:
        raise ValueError(
            f"{index + 1}件目の問題文が空です。"
        )

    if not answer:
        raise ValueError(
            f"{index + 1}件目の答えが空です。"
        )

    number = quiz.get("number")

    if number in ("", None):
        number = None
    else:
        try:
            number = int(number)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{index + 1}件目の番号が正しくありません。"
            ) from error

    fever = 1 if quiz.get("fever") in (
        1,
        "1",
        True,
        "true",
        "True",
    ) else 0

    exclude = 1 if quiz.get("exclude") in (
        1,
        "1",
        True,
        "true",
        "True",
    ) else 0

    return {
        "number": number,
        "question": question,
        "answer": answer,
        "explanation": quiz.get("explanation") or None,
        "image_q": quiz.get("image_q") or None,
        "image_a": quiz.get("image_a") or None,
        "fever": fever,
        "exclude": exclude,
    }


def load_quizzes_from_json(
    json_bytes: bytes,
) -> int:
    """
    アップロードされたJSONを読み込み、
    クイズを既存データへ追加登録する。
    """

    try:
        text = json_bytes.decode("utf-8-sig")

    except UnicodeDecodeError as error:
        raise ValueError(
            "JSONファイルをUTF-8形式で保存してください。"
        ) from error

    try:
        data = json.loads(text)

    except json.JSONDecodeError as error:
        raise ValueError(
            "JSONの形式が正しくありません。"
            f" 行: {error.lineno}"
        ) from error

    # エクスポート形式
    # {"app": "...", "quizzes": [...]}
    if isinstance(data, dict):
        quizzes = data.get("quizzes")

    # 以前の初期クイズ形式
    # [{...}, {...}]
    elif isinstance(data, list):
        quizzes = data

    else:
        raise ValueError(
            "JSONの内容がクイズ一覧ではありません。"
        )

    if not isinstance(quizzes, list):
        raise ValueError(
            "quizzesが配列になっていません。"
        )

    if not quizzes:
        raise ValueError(
            "読み込めるクイズがありません。"
        )

    validated_quizzes = [
        validate_quiz_data(quiz, index)
        for index, quiz in enumerate(quizzes)
    ]

    quiz_values = [
        tuple(
            quiz[field]
            for field in QUIZ_FIELDS
        )
        for quiz in validated_quizzes
    ]

    conn = get_connection()

    try:
        conn.executemany(
            INSERT_QUIZ_SQL,
            quiz_values,
        )

        conn.commit()

        return len(validated_quizzes)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()