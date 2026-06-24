import time

class BingoState:
    def __init__(self):

        # 現在表示中
        self.current_item = "-"

        # 回答表示フラグ
        self.show_answer = False

        # 表示タイプ
        self.current_type = "number"

        # 現在の数字
        self.current_number = None
        self.pending_number = None
        self.current_answer = ""
        self.current_explanation = None

        # 履歴
        self.drawn_numbers = []

        self.current_image = None

        # タイマー終了時刻
        self.timer_end = None

    # 履歴追加
    def add_to_history(self, number):
        if number is not None and number not in self.drawn_numbers:
            self.drawn_numbers.append(number)

    # タイマー開始
    def start_timer(self, seconds: int):
        self.timer_end = time.time() + seconds

    # 残り秒数
    def get_remaining(self):
        if self.timer_end is None:
            return None

        remaining = int(self.timer_end - time.time())

        return max(0, remaining)

state = BingoState()