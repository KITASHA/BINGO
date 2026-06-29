import json
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # exe実行時
    except Exception:
        base_path = os.path.abspath(".")  # 通常実行時
    return os.path.join(base_path, relative_path)

# クイズデータ読込
json_path = resource_path("quizzes.json")

with open(json_path, encoding="utf-8") as f:
    quiz_list = json.load(f)