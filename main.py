from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 現在表示中の内容
current_item = "-"

# 表示タイプ
current_type = "number"

# 抽選済み履歴
drawn_numbers = []

# クイズ一覧
quiz_list = [
    "ライト兄弟は何人兄弟？",
    "五輪の輪は何色？",
    "世界で最も面積が大きい国は？",
    "1年は何日？",
    "日本の県はいくつある？",
    "富士山の標高は何m？"
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

    global current_item
    global current_type

    available = [
        n for n in range(1, 76)
        if n not in drawn_numbers
    ]

    if not available:
        return {"success": False}

    number = random.choice(available)

    drawn_numbers.append(number)

    current_item = number
    current_type = "number"

    return {
        "success": True,
        "type": "number",
        "number": number
    }


@app.get("/quiz/{quiz_id}")
async def quiz_with_id(quiz_id: int):

    global current_item
    global current_type

    if quiz_id < 0 or quiz_id >= len(quiz_list):
        return {"success": False}

    question = quiz_list[quiz_id]

    current_item = question
    current_type = "quiz"

    return {
        "success": True,
        "type": "quiz",
        "message": question
    }


@app.get("/state")
async def state():

    return {
        "current": current_item,
        "type": current_type,
        "history": drawn_numbers
    }