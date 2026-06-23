from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import random

# アプリの状態を管理するオブジェクト
from state import state

# quizzes.jsonから読み込まれたクイズ一覧
from quiz_service import quiz_list

app = FastAPI()

# templatesフォルダ内のHTMLを利用する設定
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# 表示用画面
@app.get("/display")
async def display(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="display.html"
    )


# 操作用画面
@app.get("/controller")
async def controller(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="controller.html"
    )


# 数字を抽選する
@app.get("/draw")
async def draw():

    # 直前に出題したクイズの番号を履歴へ追加
    # state.add_to_history(state.pending_number)

    # クイズ番号の確定が終わったのでリセット
    state.pending_number = None

    # 現在表示中が数字なら履歴へ追加
    if state.current_type == "number":
        state.add_to_history(state.current_number)

    # 未抽選の数字一覧を作成
    available = [
        n
        for n in range(1, 76)
        if n not in state.drawn_numbers
    ]

    # 全て抽選済みなら終了
    if not available:
        return {"success": False}

    # ランダムに1つ選ぶ
    number = random.choice(available)

    # 現在表示中の数字として保存
    state.current_number = number
    state.current_item = number
    state.current_type = "number"
    state.current_image = None

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

    # 問題文を表示
    state.current_item = quiz["text"]

    # 回答を保存
    state.current_answer = quiz["answer"]

    # 画像を保存
    state.current_image = quiz.get("image")

    # 現在表示中はクイズ
    state.current_type = "quiz"
    
    # 出題時にカウントダウンスタート
    state.start_timer(10)


    # クイズに対応する数字
    # 次回draw時に履歴へ追加される
    # state.pending_number = quiz["number"]

    return {
        "success": True,
        "type": "quiz",
        "message": quiz["text"],
        "answer": quiz["answer"],
        "image": quiz.get("image")  
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

        # 回答表示フラグ
        "show_answer": state.show_answer,

        # number または quiz
        "type": state.current_type,

        # 抽選済み数字一覧
        "history": state.drawn_numbers,

        "image": state.current_image,

        "remaining": state.get_remaining()
    }