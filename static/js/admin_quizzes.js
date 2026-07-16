document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("search-input");
    const sortSelect = document.getElementById("sort-select");
    const sortOrderSelect = document.getElementById("sort-order");
    const tableBody = document.getElementById("quiz-table-body");
    const visibleCount = document.getElementById("visible-count");
    const noResults = document.getElementById("no-results");
    const selectAllCheckbox = document.getElementById("select-all");
    const bulkDeleteButton = document.getElementById("bulk-delete-button");

    function getQuizCheckboxes() {
        return Array.from(
            tableBody.querySelectorAll(".quiz-checkbox")
        );
    }

    function getSelectedQuizIds() {
        return getQuizCheckboxes()
            .filter(function (checkbox) {
                return checkbox.checked;
            })
            .map(function (checkbox) {
                return Number(checkbox.value);
            });
    }

    function updateBulkDeleteButton() {
        const selectedIds = getSelectedQuizIds();
        const selectedCount = selectedIds.length;

        bulkDeleteButton.disabled = selectedCount === 0;

        if (selectedCount === 0) {
            bulkDeleteButton.textContent = "選択削除";
        } else {
            bulkDeleteButton.textContent =
                `${selectedCount}件を削除`;
        }
    }

    function updateSelectAllCheckbox() {
        const visibleCheckboxes = getQuizCheckboxes()
            .filter(function (checkbox) {
                const row = checkbox.closest(".quiz-row");

                return row.style.display !== "none";
            });

        const checkedCount = visibleCheckboxes
            .filter(function (checkbox) {
                return checkbox.checked;
            })
            .length;

        selectAllCheckbox.checked =
            visibleCheckboxes.length > 0 &&
            checkedCount === visibleCheckboxes.length;

        selectAllCheckbox.indeterminate =
            checkedCount > 0 &&
            checkedCount < visibleCheckboxes.length;
    }

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

        updateSelectAllCheckbox();
        updateBulkDeleteButton();
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

    selectAllCheckbox.addEventListener("change", function () {
        getQuizCheckboxes().forEach(function (checkbox) {
            const row = checkbox.closest(".quiz-row");

            if (row.style.display !== "none") {
                checkbox.checked = selectAllCheckbox.checked;
            }
        });

        updateBulkDeleteButton();
        updateSelectAllCheckbox();
    });

    tableBody.addEventListener("change", function (event) {
        if (!event.target.classList.contains("quiz-checkbox")) {
            return;
        }

        updateBulkDeleteButton();
        updateSelectAllCheckbox();
    });

    tableBody.addEventListener("click", function (event) {
        const row = event.target.closest(".quiz-row");

        if (!row) {
            return;
        }

        if (event.target.closest("input[type='checkbox']")) {
            return;
        }

        window.location.href = row.dataset.editUrl;
    });

    bulkDeleteButton.addEventListener("click", async function () {
        const selectedIds = getSelectedQuizIds();

        if (selectedIds.length === 0) {
            return;
        }

        const isConfirmed = confirm(
            `選択した${selectedIds.length}件のクイズを削除しますか？`
        );

        if (!isConfirmed) {
            return;
        }

        bulkDeleteButton.disabled = true;
        bulkDeleteButton.textContent = "削除中...";

        try {
            const response = await fetch(
                "/admin/quizzes/bulk-delete",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        quiz_ids: selectedIds
                    })
                }
            );

            if (!response.ok) {
                throw new Error("一括削除に失敗しました");
            }

            window.location.reload();

        } catch (error) {
            console.error(error);

            alert("一括削除に失敗しました");

            updateBulkDeleteButton();
        }
    });

    sortRows();
    filterRows();
    updateBulkDeleteButton();
    updateSelectAllCheckbox();
});