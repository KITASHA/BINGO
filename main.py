from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 現在表示中の内容
current_item = "-"
show_answer = False

# 表示タイプ
current_type = "number"

# 抽選済み履歴
current_number = None
pending_number = None
current_answer = ""
drawn_numbers = []

# クイズ一覧
quiz_list = [
    {"number": 7, "text": "ライト兄弟の兄弟の数",
        "answer": "実は7人兄弟"},
    {"number": 48, "text": "エベレストは標高88○○.86m",
        "answer": "8848.86m"},
    {"number": 42, "text": "千手観音の腕の本数",
        "answer": "42本"},
    {"number": 10, "text": "50円玉と10円玉のうち重い方",
        "answer": "実は10円のほうが重いんです"},
    {"number": 75, "text": "最大値ゲーム",
        "answer": "優勝した人の番号を全員空けれます"}
]


@app.get("/display")
async def display(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="display.html"
    )


@app.get("/controller")
async def controller(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="controller.html"
    )

@app.get("/draw")
async def draw():

    global pending_number
    global current_number
    global current_item
    global current_type

    # 問題の数字を履歴へ
    if pending_number is not None:

        if pending_number not in drawn_numbers:
            drawn_numbers.append(pending_number)

        pending_number = None

    # 前回の抽選数字を履歴へ
    if current_type == "number" and current_number is not None:

        if current_number not in drawn_numbers:
            drawn_numbers.append(current_number)

    available = [
        n for n in range(1, 76)
        if n not in drawn_numbers
    ]

    if not available:
        return {"success": False}

    number = random.choice(available)

    current_number = number
    current_item = number
    current_type = "number"

    return {
        "success": True,
        "number": number
    }

@app.get("/quiz/{quiz_id}")
async def quiz_with_id(quiz_id: int):

    global current_item
    global current_answer
    global current_type
    global pending_number
    global current_number
    global drawn_numbers

    # 表示中が数字なら履歴へ移動
    if current_type == "number" and current_number is not None:

        if current_number not in drawn_numbers:
            drawn_numbers.append(current_number)

    if quiz_id < 0 or quiz_id >= len(quiz_list):
        return {"success": False}

    quiz = quiz_list[quiz_id]

    current_item = quiz["text"]
    current_answer = quiz["answer"]
    current_type = "quiz"

    # 問題に対応する数字は次回抽選時に確定
    pending_number = quiz["number"]

    return {
        "success": True,
        "type": "quiz",
        "message": quiz["text"],
        "answer": quiz["answer"]
    }


@app.get("/quiz-list")
async def get_quiz_list():
    return {"quizzes": quiz_list}

@app.get("/show-answer")
async def show_answer_api():

    global show_answer

    show_answer = True

    return {"success": True}

@app.get("/hide-answer")
async def hide_answer_api():

    global show_answer

    show_answer = False

    return {"success": True}


@app.get("/state")
async def state():

    return {
        "current": current_item,
        "answer": current_answer,
        "show_answer": show_answer,
        "type": current_type,
        "history": drawn_numbers
    }