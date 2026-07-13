document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("search-input");
    const sortSelect = document.getElementById("sort-select");
    const sortOrderSelect = document.getElementById("sort-order");
    const tableBody = document.getElementById("quiz-table-body");
    const visibleCount = document.getElementById("visible-count");
    const noResults = document.getElementById("no-results");

    function filterRows() {
        const keyword = searchInput.value.toLowerCase().trim();
        const rows = tableBody.querySelectorAll(".quiz-row");

        let count = 0;

        rows.forEach(function (row) {
            const searchText =
                (row.dataset.search || "").toLowerCase();

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
            tableBody.querySelectorAll(".quiz-row")
        );

        const sortType = sortSelect.value;
        const sortOrder = sortOrderSelect.value;
        const direction = sortOrder === "asc" ? 1 : -1;

        rows.sort(function (a, b) {
            let result = 0;

            if (sortType === "id") {
                result =
                    Number(a.dataset.id) -
                    Number(b.dataset.id);

            } else if (sortType === "number") {
                result =
                    Number(a.dataset.number) -
                    Number(b.dataset.number);

            } else if (sortType === "question") {
                result =
                    (a.dataset.question || "").localeCompare(
                        b.dataset.question || "",
                        "ja"
                    );

            } else if (sortType === "status") {
                result =
                    Number(a.dataset.status) -
                    Number(b.dataset.status);
            }

            return result * direction;
        });

        rows.forEach(function (row) {
            tableBody.appendChild(row);
        });
    }

    searchInput.addEventListener("input", filterRows);
    sortSelect.addEventListener("change", sortRows);
    sortOrderSelect.addEventListener("change", sortRows);

    sortRows();
    filterRows();
});