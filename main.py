import os
import sys
import time
import random
import threading
import subprocess

import uvicorn
from fastapi import FastAPI, Request
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import get_connection
from fastapi.responses import RedirectResponse
 

from state import state


# =========================
# パス設定
# =========================

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# =========================
# クイズデータ読込
# =========================
def load_quizzes():
    conn = get_connection()

    rows = conn.execute(
        "SELECT * FROM quizzes"
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]

quiz_list = load_quizzes()


# =========================
# FastAPI設定
# =========================

app = FastAPI()

templates = Jinja2Templates(
    directory=resource_path("templates")
)

app.mount(
    "/static",
    StaticFiles(directory=resource_path("static")),
    name="static"
)


# =========================
# 共通処理
# =========================

def add_current_number_to_history():
    """現在表示中が数字なら履歴に追加する"""
    if state.current_type == "number":
        state.add_to_history(state.current_number)


def reset_answer_state():
    """回答表示をリセットする"""
    state.show_answer = False


def get_excluded_numbers():
    """クイズで除外指定された番号を取得する"""
    return {
        quiz["number"]
        for quiz in quiz_list
        if quiz.get("exclude") is True
    }


def open_browser():
    """起動時に表示画面と操作画面を開く"""
    time.sleep(2)

    subprocess.Popen(
        ["start", "msedge", "--new-window", "http://127.0.0.1:8000/display"],
        shell=True
    )

    time.sleep(1)

    subprocess.Popen(
        ["start", "msedge", "--new-window", "http://127.0.0.1:8000/controller"],
        shell=True
    )


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


@app.post("/admin/quizzes")
async def create_quiz(
    number: int | None = Form(None),
    question: str = Form(...),
    answer: str = Form(...),
    explanation: str = Form(""),
    image_q: str = Form(""),
    image_a: str = Form(""),
    fever: str | None = Form(None),
    exclude: str | None = Form(None),
):
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
            number,
            question,
            answer,
            explanation,
            image_q,
            image_a,
            1 if fever else 0,
            1 if exclude else 0
        )
    )

    conn.commit()
    conn.close()

    global quiz_list
    quiz_list = load_quizzes()

    return RedirectResponse(
    url="/admin/quizzes",
    status_code=303
)

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
            "quizzes": quizzes
        }
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