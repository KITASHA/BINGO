let lastValue = null;
let isAnimating = false;
let lastShowAnswer = false;


// サーバーから現在の状態を取得して画面に反映する
async function refresh() {

    try {

        const response = await fetch("/state");
        const data = await response.json();

        const current =
            document.getElementById("current-number");

        const timerEl =
            document.getElementById("timer");

        const quizImage =
            document.getElementById("quiz-image");

        const title =
            document.getElementById("result-title");

        // クイズ中はタイトル非表示
        if (data.type === "quiz") {
            title.classList.add("hidden");
        } else {
            title.classList.remove("hidden");
        }

        // 通常表示時の文字サイズ
        if (!isAnimating) {

            if (data.type === "quiz") {
                current.className =
                    "text-5xl md:text-7xl font-black break-words transition-transform duration-300";
            } else {
                current.className =
                    "text-[12rem] md:text-[16rem] font-black leading-none transition-transform duration-300";
            }

        }

        // 表示内容が変わったときだけルーレット演出を開始する
        if (
            data.current !== lastValue &&
            !isAnimating
        ) {
            isAnimating = true;
            lastValue = data.current;

            // ルーレット中は常に大きい文字
            current.className =
                "text-[12rem] md:text-[16rem] font-black leading-none transition-transform duration-300";
            timerEl.textContent = "";
            quizImage.src = "";
            quizImage.classList.add("hidden");

            let count = 0;

            // ドラムロール開始
            const drumrollSound =
                document.getElementById("drumroll-sound");

            drumrollSound.currentTime = 0;
            drumrollSound.play();

            const roulette = setInterval(() => {

                // ルーレット中のランダム数字
                current.textContent =
                    Math.floor(Math.random() * 75) + 1;

                count++;

                // ルーレット終了
                if (count >= 20) {

                    clearInterval(roulette);

                    // ドラムロール停止
                    drumrollSound.pause();
                    drumrollSound.currentTime = 0;

                    // 確定した数字または問題文を表示
                    current.textContent = data.current;

                    // 数字抽選時はシンバル
                    if (data.type === "number") {

                        const cymbalSound =
                            document.getElementById("cymbal-sound");

                        cymbalSound.currentTime = 0;
                        cymbalSound.play();
                    }

                    // クイズ出題時は出題音とタイマー音
                    if (data.type === "quiz") {
                        
                        current.className =
                                "text-5xl md:text-7xl font-black break-words transition-transform duration-300";


                        const questionSound =
                            document.getElementById("question-sound");

                        questionSound.currentTime = 0;
                        questionSound.play();

                        // フィーバータイムではタイマー音を鳴らさない
                        if (!data.fever) {

                            const timerSound =
                                document.getElementById("timer-sound");

                            timerSound.currentTime = 0;
                            timerSound.play();
                        }

                        // 出題と同時に問題画像を表示
                        if (data.image_q) {
                            quizImage.src = data.image_q;
                            quizImage.classList.remove("hidden");
                        }
                    }

                    // 確定時の「ドン」演出
                    current.classList.add("scale-125");

                    setTimeout(() => {
                        current.classList.remove("scale-125");
                        isAnimating = false;
                    }, 300);
                }

            }, 50);

            return;
        }

        // 演出中でなければ通常表示
        if (!isAnimating) {
            current.textContent = data.current;
        }

        // 回答テキスト
        document.getElementById("answer-text").textContent =
            data.type === "quiz"
                ? (data.answer || "")
                : "";

        // 回答解説
        document.getElementById("answer-explanation").textContent =
            data.type === "quiz"
                ? (data.explanation || "")
                : "";

        // 抽選履歴を表示
        const historyDiv =
            document.getElementById("history");

        historyDiv.innerHTML = "";

        for (const number of data.history.slice().reverse()) {

            const item =
                document.createElement("div");

            item.className =
                "bg-slate-800 px-4 py-2 rounded-xl text-xl font-bold";

            item.textContent = number;

            historyDiv.appendChild(item);
        }

        // 回答モーダル表示切り替え
        const modal =
            document.getElementById("answer-modal");

        if (data.show_answer) {
            modal.classList.remove("hidden");
            modal.classList.add("flex");
        } else {
            modal.classList.remove("flex");
            modal.classList.add("hidden");
        }

        // 回答表示時にシンバルを鳴らす
        if (
            data.show_answer &&
            !lastShowAnswer
        ) {
            const cymbalSound =
                document.getElementById("cymbal-sound");

            cymbalSound.currentTime = 0;
            cymbalSound.play();
        }

        lastShowAnswer = data.show_answer;

        // 問題画像
        if (
            data.type === "quiz" &&
            data.image_q &&
            !isAnimating
        ) {
            quizImage.src = data.image_q;
            quizImage.classList.remove("hidden");
        } else if (data.type !== "quiz") {
            quizImage.src = "";
            quizImage.classList.add("hidden");
        }

        // 回答画像
        const answerImage =
            document.getElementById("answer-image");

        if (data.type === "quiz" && data.image_a) {
            answerImage.src = data.image_a;
            answerImage.classList.remove("hidden");
        } else {
            answerImage.src = "";
            answerImage.classList.add("hidden");
        }

        // カウントダウン表示
        if (
            data.type === "quiz" &&
            data.remaining !== null &&
            !data.fever &&
            !isAnimating
        ) {
            timerEl.textContent =
                `残り ${data.remaining} 秒`;

            if (data.remaining <= 3) {
                timerEl.classList.add("text-red-600");
                timerEl.classList.remove("text-red-500");
            } else {
                timerEl.classList.add("text-red-500");
                timerEl.classList.remove("text-red-600");
            }
        } else {
            timerEl.textContent = "";
        }

        // フィーバー表示
        if (data.fever) {
            title.textContent =
                "✨ フィーバータイム！！ ✨";

            title.classList.add("fever-mode");
        } else {
            title.textContent =
                "抽選結果";

            title.classList.remove("fever-mode");
        }

    } catch (error) {
        console.error(error);
    }
}


// 定期更新
setInterval(refresh, 500);

// 初回表示
refresh();