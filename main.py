import os
import sys
import time
import random
import threading
import subprocess

from pathlib import Path
from uuid import uuid4

import uvicorn

from fastapi import (
    FastAPI,
    Request,
    Form,
    File,
    UploadFile,
    HTTPException,
)

from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import get_connection
from state import state
from init_db import init_db
from import_quizzes import import_quizzes, is_quiz_database_empty
from pydantic import BaseModel


class BulkDeleteRequest(BaseModel):
    quiz_ids: list[int]


# =========================
# パス設定
# =========================

def resource_path(relative_path: str) -> str:
    """
    templatesや同梱staticなど、
    PyInstallerに含めた読み取り用ファイルのパスを返す。
    """

    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def writable_path(relative_path: str) -> Path:
    """
    DBやアップロード画像など、
    実行後に書き込むファイルのパスを返す。
    """

    if getattr(sys, "frozen", False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path


# =========================
# 画像保存用設定
# =========================

UPLOAD_DIR = writable_path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
}


# =========================
# 画像保存用関数
# =========================

async def save_uploaded_image(
    upload_file: UploadFile | None,
    current_path: str = "",
) -> str:
    """
    新しい画像が選択されていれば保存する。
    選択されていなければ現在の画像パスを返す。
    """

    if upload_file is None or not upload_file.filename:
        return current_path

    extension = Path(upload_file.filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        await upload_file.close()

        raise HTTPException(
            status_code=400,
            detail="使用できる画像形式はjpg、jpeg、png、gif、webpです。",
        )

    filename = f"{uuid4().hex}{extension}"
    save_path = UPLOAD_DIR / filename

    try:
        contents = await upload_file.read()
        save_path.write_bytes(contents)
    finally:
        await upload_file.close()

    return f"/uploads/{filename}"

init_db()

# =========================
# クイズデータ読み込み
# =========================

def load_quizzes():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT *
            FROM quizzes
            ORDER BY id ASC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


quiz_list = load_quizzes()


def refresh_quiz_list():
    new_quizzes = load_quizzes()

    quiz_list.clear()
    quiz_list.extend(new_quizzes)



# =========================
# FastAPI設定
# =========================

app = FastAPI()

templates = Jinja2Templates(
    directory=resource_path("templates")
)

# 最初から同梱されている画像・CSS・JavaScript
app.mount(
    "/static",
    StaticFiles(directory=resource_path("static")),
    name="static",
)

# 管理画面からアップロードした画像
app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_DIR)),
    name="uploads",
)


# =========================
# 初期クイズ読み込み
# =========================
@app.post("/admin/quizzes/import-default")
async def import_default_quizzes_api():
    try:
        if not is_quiz_database_empty():
            return {
                "success": False,
                "message": "すでにクイズが登録されています。"
            }

        imported_count = import_quizzes()

        refresh_quiz_list()


        return {
            "success": True,
            "imported_count": imported_count
        }

    except Exception as error:
        print("初期クイズ読み込みエラー:", repr(error))

        return {
            "success": False,
            "message": f"{type(error).__name__}: {error}"
        }


# =========================
# 共通処理
# =========================

def add_current_number_to_history() -> None:
    """現在表示中の内容が数字なら履歴に追加する。"""

    if state.current_type == "number":
        state.add_to_history(state.current_number)


def reset_answer_state() -> None:
    """回答表示状態をリセットする。"""

    state.show_answer = False


def get_excluded_numbers() -> set[int]:
    """通常抽選から除外するクイズ番号を取得する。"""

    return {
        quiz["number"]
        for quiz in quiz_list
        if quiz.get("exclude") == 1
        and quiz.get("number") is not None
    }


def open_browser() -> None:
    """起動時に表示画面と操作画面をEdgeで開く。"""

    time.sleep(2)

    subprocess.Popen(
        [
            "start",
            "msedge",
            "--new-window",
            "http://127.0.0.1:8000/display",
        ],
        shell=True,
    )

    time.sleep(1)

    subprocess.Popen(
        [
            "start",
            "msedge",
            "--new-window",
            "http://127.0.0.1:8000/controller",
        ],
        shell=True,
    )


def refresh_quiz_list() -> None:
    """データベースからクイズ一覧を再読み込みする。"""

    global quiz_list
    quiz_list = load_quizzes()


def checkbox_to_int(value: str | None) -> int:
    """チェックボックスの値を0または1へ変換する。"""

    return 1 if value is not None else 0


def parse_optional_number(value: str) -> int | None:
    """空文字はNone、入力値は0以上の整数へ変換する。"""

    value = value.strip()

    if not value:
        return None

    try:
        number = int(value)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="番号には整数を入力してください。",
        )

    if number < 0:
        raise HTTPException(
            status_code=400,
            detail="番号は0以上にしてください。",
        )

    return number

# =========================
# 画面表示
# =========================

@app.get("/display")
async def display(request: Request):
    return templates.TemplateResponse(
        name="display.html",
        request=request
    )


@app.get("/controller")
async def controller(request: Request):
    return templates.TemplateResponse(
        name="controller.html",
        request=request
    )


# =========================
# 数字抽選
# =========================

@app.get("/draw")
async def draw():

    add_current_number_to_history()

    excluded_numbers = get_excluded_numbers()

    available_numbers = [
        number
        for number in range(1, 76)
        if number not in state.drawn_numbers
        and number not in excluded_numbers
    ]

    if not available_numbers:
        return {"success": False}

    number = random.choice(available_numbers)

    state.current_number = number
    state.current_item = number
    state.current_type = "number"
    state.fever = False

    reset_answer_state()

    return {
        "success": True,
        "number": number
    }


# =========================
# クイズ
# =========================

@app.get("/quiz/{quiz_id}")
async def quiz_with_id(quiz_id: int):

    add_current_number_to_history()

    if quiz_id < 0 or quiz_id >= len(quiz_list):
        return {"success": False}

    quiz = quiz_list[quiz_id]

    state.current_item = quiz["question"]
    state.current_answer = quiz["answer"]
    state.current_explanation = quiz.get("explanation")

    state.current_image_q = quiz.get("image_q")
    state.current_image_a = quiz.get("image_a")

    state.current_type = "quiz"
    state.fever = quiz.get("fever", False)

    reset_answer_state()

    state.start_timer(12)

    return {
        "success": True,
        "type": "quiz",
        "message": quiz["question"],
        "answer": quiz["answer"],
        "image_q": quiz.get("image_q")
    }


@app.get("/quiz-list")
async def get_quiz_list():
    return {
        "quizzes": quiz_list
    }


# =========================
# 回答表示
# =========================

@app.get("/show-answer")
async def show_answer_api():
    state.show_answer = True
    return {"success": True}


@app.get("/hide-answer")
async def hide_answer_api():
    state.show_answer = False
    return {"success": True}


# =========================
# 状態取得
# =========================

@app.get("/state")
async def get_state():
    return {
        "current": state.current_item,
        "answer": state.current_answer,
        "explanation": state.current_explanation,
        "show_answer": state.show_answer,
        "type": state.current_type,
        "history": state.drawn_numbers,
        "image_q": state.current_image_q,
        "image_a": state.current_image_a,
        "fever": state.fever,
        "remaining": state.get_remaining()
    }


# =========================
# クイズ新規登録処理
# =========================
@app.post("/admin/quizzes")
async def create_quiz(
    number: str = Form(""),
    question: str = Form(...),
    answer: str = Form(...),
    explanation: str = Form(""),
    fever: str | None = Form(None),
    exclude: str | None = Form(None),
    image_q_file: UploadFile | None = File(None),
    image_a_file: UploadFile | None = File(None),
):
    image_q = await save_uploaded_image(image_q_file)
    image_a = await save_uploaded_image(image_a_file)

    number_value = parse_optional_number(number)
    fever_value = checkbox_to_int(fever)
    exclude_value = checkbox_to_int(exclude)

    conn = get_connection()

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
            number_value,
            question.strip(),
            answer.strip(),
            explanation.strip(),
            image_q,
            image_a,
            fever_value,
            exclude_value,
        )
    )

    conn.commit()
    conn.close()
    refresh_quiz_list()

    return RedirectResponse(
        url="/admin/quizzes",
        status_code=303
    )


# =========================
# クイズ一覧画面表示
# =========================
@app.get("/admin/quizzes")
async def admin_quizzes(request: Request):
    conn = get_connection()

    rows = conn.execute(
        "SELECT * FROM quizzes ORDER BY id DESC"
    ).fetchall()

    conn.close()

    quizzes = [dict(row) for row in rows]

    return templates.TemplateResponse(
        request=request,
        name="admin_quizzes.html",
        context={
            "quizzes": quizzes,
            "show_initial_quiz_dialog": is_quiz_database_empty()
        }
    )


# =========================
# クイズ新規作成画面表示
# =========================
@app.get("/admin/quizzes/new")
async def new_quiz(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="new_quiz.html"
    )

# =========================
# クイズ一括削除処理
# =========================

@app.post("/admin/quizzes/bulk-delete")
async def bulk_delete_quizzes(
    request_data: BulkDeleteRequest
):
    quiz_ids = request_data.quiz_ids

    if not quiz_ids:
        return {
            "success": False,
            "message": "削除対象が選択されていません。"
        }

    placeholders = ",".join(
        "?" for _ in quiz_ids
    )

    conn = get_connection()

    try:
        cursor = conn.execute(
            f"""
            DELETE FROM quizzes
            WHERE id IN ({placeholders})
            """,
            quiz_ids
        )

        conn.commit()
        deleted_count = cursor.rowcount

    finally:
        conn.close()

    refresh_quiz_list()

    return {
        "success": True,
        "deleted_count": deleted_count
    }

# =========================
# クイズ個別削除処理
# =========================
@app.post("/admin/quizzes/{quiz_id}/delete")
async def delete_quiz(quiz_id: int):
    conn = get_connection()

    conn.execute(
        "DELETE FROM quizzes WHERE id = ?",
        (quiz_id,)
    )

    conn.commit()
    conn.close()
    refresh_quiz_list()

    return RedirectResponse(
        url="/admin/quizzes",
        status_code=303
    )

# =========================
# クイズ編集画面表示
# =========================
@app.get("/admin/quizzes/{quiz_id}/edit")
async def edit_quiz(request: Request, quiz_id: int):
    conn = get_connection()

    try:
        row = conn.execute(
            "SELECT * FROM quizzes WHERE id = ?",
            (quiz_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="クイズが見つかりません"
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_quiz.html",
        context={
            "quiz": dict(row)
        }
    )

# =========================
# クイズ更新処理
# =========================
@app.post("/admin/quizzes/{quiz_id}/edit")
async def update_quiz(
    quiz_id: int,
    number: str = Form(""),
    question: str = Form(...),
    answer: str = Form(...),
    explanation: str = Form(""),
    current_image_q: str = Form(""),
    current_image_a: str = Form(""),
    fever: str | None = Form(None),
    exclude: str | None = Form(None),
    image_q_file: UploadFile | None = File(None),
    image_a_file: UploadFile | None = File(None),
):
    number_value = parse_optional_number(number)
    fever_value = checkbox_to_int(fever)
    exclude_value = checkbox_to_int(exclude)

    image_q = await save_uploaded_image(
        image_q_file,
        current_image_q
    )

    image_a = await save_uploaded_image(
        image_a_file,
        current_image_a
    )

    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            UPDATE quizzes
            SET
                number = ?,
                question = ?,
                answer = ?,
                explanation = ?,
                image_q = ?,
                image_a = ?,
                fever = ?,
                exclude = ?
            WHERE id = ?
            """,
            (
                number_value,
                question.strip(),
                answer.strip(),
                explanation.strip(),
                image_q,
                image_a,
                fever_value,
                exclude_value,
                quiz_id,
            )
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="クイズが見つかりません"
            )

        conn.commit()

    finally:
        conn.close()

    refresh_quiz_list()

    return RedirectResponse(
        url="/admin/quizzes",
        status_code=303
    )

# =========================
# 起動
# =========================

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_config=None
    )
