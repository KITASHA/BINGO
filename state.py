class BingoState:
    def __init__(self):

        # 現在表示中の内容（数字または問題文）
        self.current_item = "-"

        # 回答表示フラグ
        self.show_answer = False

        # 表示中の種類（number / quiz）
        self.current_type = "number"

        # 現在表示中の数字
        self.current_number = None

        # 出題したクイズに対応する数字
        # 次回抽選時に履歴へ追加される
        self.pending_number = None

        # 現在表示中クイズの回答
        self.current_answer = ""

        # 抽選済み数字の履歴
        self.drawn_numbers = []

    # 履歴に数字を追加
    def add_to_history(self, number):

        # Noneや重複を除外
        if number is not None and number not in self.drawn_numbers:
            self.drawn_numbers.append(number)


# アプリ全体で共有する状態
state = BingoState()