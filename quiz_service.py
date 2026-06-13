import json


# クイズデータ読込
with open("quizzes.json", encoding="utf-8") as f:
    quiz_list = json.load(f)