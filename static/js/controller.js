
// 数字を抽選する
async function drawNumber() {

    const res = await fetch("/draw");
    const data = await res.json();

    // 全て抽選済みなら終了
    if (!data.success) {
        alert("すべて抽選済みです");
        return;
    }

    // 操作画面に抽選結果を表示
    document.getElementById("result").textContent =
        data.number;
}


// クイズ一覧を取得してセレクトボックスへ設定する
async function loadQuizList() {

    const res = await fetch("/quiz-list");
    const data = await res.json();

    const select =
        document.getElementById("quiz-select");

    select.innerHTML = "";

    data.quizzes.forEach((quiz, index) => {

        const option =
            document.createElement("option");

        option.value = index;

        // number がある場合は「番号：問題文」で表示
        option.textContent =
            quiz.number
                ? `${quiz.number}：${quiz.text}`
                : quiz.text;

        select.appendChild(option);
    });
}


// 選択中のクイズを表示する
async function showQuiz() {

    const quizId = parseInt(
        document.getElementById("quiz-select").value
    );

    const res =
        await fetch(`/quiz/${quizId}`);

    const data =
        await res.json();

    console.log(data);

    // 操作画面に状態を表示
    document.getElementById("result").textContent =
        "問題表示中";
}


// 回答表示のON/OFFを切り替える
async function toggleAnswer() {

    const stateRes =
        await fetch("/state");

    const state =
        await stateRes.json();

    if (state.show_answer) {
        await fetch("/hide-answer");
    } else {
        await fetch("/show-answer");
    }
}


// 初期表示時にクイズ一覧を読み込む
loadQuizList();
