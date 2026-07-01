from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import threading
import webbrowser
import uvicorn
import random
import time
import subprocess

import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# アプリの状態を管理するオブジェクト
from state import state

# quizzes.jsonから読み込まれたクイズ一覧
from quiz_service import quiz_list


app = FastAPI()

# ✅ 先に定義
templates = Jinja2Templates(directory=resource_path("templates"))

app.mount(
    "/static",
    StaticFiles(directory=resource_path("static")),
    name="static"
)


# ブラウザ起動
def open_browser():
    import time
    time.sleep(2)

    subprocess.Popen(["start", "msedge", "--new-window", "http://127.0.0.1:8000/display"], shell=True)
    time.sleep(1)
    subprocess.Popen(["start", "msedge", "--new-window", "http://127.0.0.1:8000/controller"], shell=True)


# 表示画面
@app.get("/display")
async def display(request: Request):
    return templates.TemplateResponse(
        name="display.html",
        request=request
    )


# 操作画面
@app.get("/controller")
async def controller(request: Request):
    return templates.TemplateResponse(
        name="controller.html",
        request=request
    )


# 数字を抽選する
@app.get("/draw")
async def draw():

    # 抽選除外番号
    excluded_numbers = {
        quiz["number"]
        for quiz in quiz_list
        if quiz.get("exclude") is True
    }

    # 現在表示中が数字なら履歴へ追加
    if state.current_type == "number":
        state.add_to_history(state.current_number)

    # 未抽選の数字一覧
    available_numbers = [
        number
        for number in range(1, 76)
        if number not in state.drawn_numbers
        and number not in excluded_numbers
    ]

    # 全て抽選済みなら終了
    if not available_numbers:
        return {"success": False}

    # ランダムに1つ選ぶ
    number = random.choice(available_numbers)

    # 現在表示中の数字として保存
    state.current_number = number
    state.current_item = number
    state.current_type = "number"

    # 回答表示をリセット
    state.show_answer = False

    # フィーバー解除
    state.fever = False

    return {
        "success": True,
        "number": number
    }


# 指定したクイズを出題
@app.get("/quiz/{quiz_id}")
async def quiz_with_id(quiz_id: int):

    # 現在表示中が数字なら履歴へ追加
    if state.current_type == "number":
        state.add_to_history(state.current_number)

    # 存在しないクイズ番号なら失敗
    if quiz_id < 0 or quiz_id >= len(quiz_list):
        return {"success": False}

    # 対象クイズ取得
    quiz = quiz_list[quiz_id]

    # 問題文
    state.current_item = quiz["text"]

    # 回答
    state.current_answer = quiz["answer"]

    # 解説
    state.current_explanation = quiz.get("explanation")

    # 問題画像
    state.current_image_q = quiz.get("image_q")

    # 回答画像
    state.current_image_a = quiz.get("image_a")

    # 表示モード
    state.current_type = "quiz"

    # 回答非表示
    state.show_answer = False

    # フィーバー設定
    state.fever = quiz.get("fever", False)

    # 出題時にカウントダウン開始
    state.start_timer(12)

    return {
        "success": True,
        "type": "quiz",
        "message": quiz["text"],
        "answer": quiz["answer"],
        "image_q": quiz.get("image_q")
    }


# クイズ一覧取得
@app.get("/quiz-list")
async def get_quiz_list():

    return {
        "quizzes": quiz_list
    }


# 回答表示ON
@app.get("/show-answer")
async def show_answer_api():

    state.show_answer = True

    return {"success": True}


# 回答表示OFF
@app.get("/hide-answer")
async def hide_answer_api():

    state.show_answer = False

    return {"success": True}


# 現在の状態取得
@app.get("/state")
async def get_state():

    return {

        # 現在表示中の内容（数字または問題文）
        "current": state.current_item,

        # クイズの回答
        "answer": state.current_answer,

        # クイズの解説
        "explanation": state.current_explanation,

        # 回答表示フラグ
        "show_answer": state.show_answer,

        # number または quiz
        "type": state.current_type,

        # 抽選済み数字一覧
        "history": state.drawn_numbers,

        # 問題画像
        "image_q": state.current_image_q,

        # 回答画像
        "image_a": state.current_image_a,

        # フィーバータイム
        "fever": state.fever,

        # クイズ残り時間
        "remaining": state.get_remaining()
    }


# 起動処理
if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)