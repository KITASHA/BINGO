import time


class BingoState:

    def __init__(self):

        # 表示中の内容
        self.current_item = "-"
        self.current_type = "number"

        # 抽選数字
        self.current_number = None
        self.drawn_numbers = []

        # クイズ情報
        self.show_answer = False
        self.current_answer = ""
        self.current_explanation = None

        # クイズ画像
        self.current_image_q = None
        self.current_image_a = None

        # タイマー終了時刻
        self.timer_end = None

        # フィーバータイム
        self.fever = False

    def add_to_history(self, number):
        """抽選履歴へ追加"""

        if number is None:
            return

        if number in self.drawn_numbers:
            return

        self.drawn_numbers.append(number)

    def start_timer(self, seconds):
        """タイマー開始"""

        self.timer_end = time.time() + seconds

    def stop_timer(self):
        """タイマー停止"""

        self.timer_end = None

    def get_remaining(self):
        """残り秒数取得"""

        if self.timer_end is None:
            return None

        remaining = int(
            self.timer_end - time.time()
        )

        return max(0, remaining)


state = BingoState()