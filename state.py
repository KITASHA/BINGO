import time


class BingoState:

    def __init__(self):

        # 現在表示中の内容
        self.current_item = "-"
        self.current_type = "number"

        # 抽選数字
        self.current_number = None
        self.drawn_numbers = []

        # クイズ回答
        self.show_answer = False
        self.current_answer = ""
        self.current_explanation = None

        # クイズ画像
        self.current_image_q = None
        self.current_image_a = None

        # カウントダウン終了時刻
        self.timer_end = None

        # フィーバータイム
        self.fever = False

    # 抽選履歴へ追加
    def add_to_history(self, number):

        if (
            number is not None and
            number not in self.drawn_numbers
        ):
            self.drawn_numbers.append(number)

    # タイマー開始
    def start_timer(self, seconds: int):

        self.timer_end = time.time() + seconds

    # 残り秒数取得
    def get_remaining(self):

        if self.timer_end is None:
            return None

        return max(
            0,
            int(self.timer_end - time.time())
        )


state = BingoState()