const searchInput = document.getElementById("search-input");
const sortSelect = document.getElementById("sort-select");
const tableBody = document.getElementById("quiz-table-body");
const visibleCount = document.getElementById("visible-count");
const noResults = document.getElementById("no-results");

function filterRows() {
    const keyword = searchInput.value.toLowerCase().trim();
    const rows = document.querySelectorAll(".quiz-row");

    let count = 0;

    rows.forEach(function (row) {
        const searchText = row.dataset.search.toLowerCase();
        const isMatch = searchText.includes(keyword);

        row.style.display = isMatch ? "" : "none";

        if (isMatch) {
            count++;
        }
    });

    visibleCount.textContent = count;

    if (count === 0) {
        noResults.classList.remove("hidden");
    } else {
        noResults.classList.add("hidden");
    }
}

function sortRows() {
    const rows = Array.from(
        document.querySelectorAll(".quiz-row")
    );

    const sortType = sortSelect.value;

    rows.sort(function (a, b) {
        if (sortType === "id-asc") {
            return Number(a.dataset.id) - Number(b.dataset.id);
        }

        if (sortType === "number-asc") {
            return Number(a.dataset.number) - Number(b.dataset.number);
        }

        if (sortType === "question-asc") {
            return a.dataset.question.localeCompare(
                b.dataset.question,
                "ja"
            );
        }

        if (sortType === "status-asc") {
            return Number(a.dataset.status) - Number(b.dataset.status);
        }

        return 0;
    });

    rows.forEach(function (row) {
        tableBody.appendChild(row);
    });
}

searchInput.addEventListener("input", filterRows);
sortSelect.addEventListener("change", sortRows);

// 初期表示をID順にする
sortRows();
