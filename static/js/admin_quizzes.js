document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("search-input");

    const sortSelect =
        document.getElementById("sort-select");

    const sortOrderSelect =
        document.getElementById("sort-order");

    const tableBody =
        document.getElementById("quiz-table-body");

    const visibleCount =
        document.getElementById("visible-count");

    const noResults =
        document.getElementById("no-results");

    const selectAllCheckbox =
        document.getElementById("select-all");

    const bulkDeleteButton =
        document.getElementById("bulk-delete-button");

    const importButton =
        document.getElementById("import-button");

    const importFileInput =
        document.getElementById("quiz-import-file");

    console.log(importButton);
    console.log(importFileInput);


    /*
     * クイズのチェックボックス一覧を取得
     */
    function getQuizCheckboxes() {
        if (!tableBody) {
            return [];
        }

        return Array.from(
            tableBody.querySelectorAll(".quiz-checkbox")
        );
    }

    /*
     * 選択中のクイズID一覧を取得
     */
    function getSelectedQuizIds() {
        return getQuizCheckboxes()
            .filter(function (checkbox) {
                return checkbox.checked;
            })
            .map(function (checkbox) {
                return Number(checkbox.value);
            })
            .filter(function (quizId) {
                return Number.isInteger(quizId);
            });
    }

    /*
     * 一括削除ボタンの状態を更新
     */
    function updateBulkDeleteButton() {
        if (!bulkDeleteButton) {
            return;
        }

        const selectedCount = getSelectedQuizIds().length;

        bulkDeleteButton.disabled = selectedCount === 0;

        if (selectedCount === 0) {
            bulkDeleteButton.textContent = "選択削除";
        } else {
            bulkDeleteButton.textContent =
                `${selectedCount}件を削除`;
        }
    }

    /*
     * 全選択チェックボックスの状態を更新
     */
    function updateSelectAllCheckbox() {
        if (!selectAllCheckbox) {
            return;
        }

        const visibleCheckboxes = getQuizCheckboxes()
            .filter(function (checkbox) {
                const row = checkbox.closest(".quiz-row");

                return row && row.style.display !== "none";
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

    /*
     * クイズ一覧を検索文字で絞り込む
     */
    function filterRows() {
        if (!tableBody || !searchInput) {
            return;
        }

        const keyword = searchInput.value
            .toLowerCase()
            .trim();

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

        if (visibleCount) {
            visibleCount.textContent = count;
        }

        if (noResults) {
            if (count === 0) {
                noResults.classList.remove("hidden");
            } else {
                noResults.classList.add("hidden");
            }
        }

        updateSelectAllCheckbox();
        updateBulkDeleteButton();
    }

    /*
     * クイズ一覧を並び替える
     */
    function sortRows() {
        if (
            !tableBody ||
            !sortSelect ||
            !sortOrderSelect
        ) {
            return;
        }

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
                    Number(a.dataset.id || 0) -
                    Number(b.dataset.id || 0);

            } else if (sortType === "number") {
                const numberA =
                    a.dataset.number === ""
                        ? Number.MAX_SAFE_INTEGER
                        : Number(a.dataset.number);

                const numberB =
                    b.dataset.number === ""
                        ? Number.MAX_SAFE_INTEGER
                        : Number(b.dataset.number);

                result = numberA - numberB;

            } else if (sortType === "question") {
                result =
                    (a.dataset.question || "").localeCompare(
                        b.dataset.question || "",
                        "ja"
                    );

            } else if (sortType === "status") {
                result =
                    Number(a.dataset.status || 0) -
                    Number(b.dataset.status || 0);
            }

            return result * direction;
        });

        rows.forEach(function (row) {
            tableBody.appendChild(row);
        });
    }

    /*
     * 検索
     */
    if (searchInput) {
        searchInput.addEventListener(
            "input",
            filterRows
        );
    }

    /*
     * 並び替え項目変更
     */
    if (sortSelect) {
        sortSelect.addEventListener(
            "change",
            sortRows
        );
    }

    /*
     * 昇順・降順変更
     */
    if (sortOrderSelect) {
        sortOrderSelect.addEventListener(
            "change",
            sortRows
        );
    }

    /*
     * 表示中のクイズを全選択・全解除
     */
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener(
            "change",
            function () {
                getQuizCheckboxes().forEach(
                    function (checkbox) {
                        const row =
                            checkbox.closest(".quiz-row");

                        if (
                            row &&
                            row.style.display !== "none"
                        ) {
                            checkbox.checked =
                                selectAllCheckbox.checked;
                        }
                    }
                );

                updateBulkDeleteButton();
                updateSelectAllCheckbox();
            }
        );
    }

    /*
     * 個別チェックボックス変更
     */
    if (tableBody) {
        tableBody.addEventListener(
            "change",
            function (event) {
                if (
                    !event.target.classList.contains(
                        "quiz-checkbox"
                    )
                ) {
                    return;
                }

                updateBulkDeleteButton();
                updateSelectAllCheckbox();
            }
        );
    }

    /*
     * 行をクリックして編集画面へ移動
     */
    if (tableBody) {
        tableBody.addEventListener(
            "click",
            function (event) {
                const row =
                    event.target.closest(".quiz-row");

                if (!row) {
                    return;
                }

                if (
                    event.target.closest(
                        "input[type='checkbox']"
                    )
                ) {
                    return;
                }

                const editUrl = row.dataset.editUrl;

                if (editUrl) {
                    window.location.href = editUrl;
                }
            }
        );
    }

    /*
     * 選択したクイズを一括削除
     */
    if (bulkDeleteButton) {
        bulkDeleteButton.addEventListener(
            "click",
            async function () {
                const selectedIds =
                    getSelectedQuizIds();

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
                bulkDeleteButton.textContent =
                    "削除中...";

                try {
                    const response = await fetch(
                        "/admin/quizzes/bulk-delete",
                        {
                            method: "POST",
                            headers: {
                                "Content-Type":
                                    "application/json"
                            },
                            body: JSON.stringify({
                                quiz_ids: selectedIds
                            })
                        }
                    );

                    const data =
                        await response.json();

                    if (
                        !response.ok ||
                        !data.success
                    ) {
                        throw new Error(
                            data.message ||
                            "一括削除に失敗しました"
                        );
                    }

                    alert(
                        `${data.deleted_count}件を削除しました。`
                    );

                    window.location.reload();

                } catch (error) {
                    console.error(error);

                    alert(
                        error.message ||
                        "一括削除に失敗しました"
                    );

                    updateBulkDeleteButton();
                }
            }
        );
    }

if (importButton && importFileInput) {

    importButton.addEventListener("click", () => {
        importFileInput.value = "";
        importFileInput.click();
    });


    importFileInput.addEventListener(
    "change",
    async function () {

        console.log("changeイベント");

        const file = importFileInput.files[0];

        console.log(file);

        if (!file) {
            console.log("ファイルなし");
            return;
        }

        console.log("ここまで来た");


            const confirmed = confirm(
                `${file.name} を読み込みます。\n\n` +
                "現在のクイズに追加しますか？"
            );

            if (!confirmed) {
                importFileInput.value = "";
                return;
            }

            const formData = new FormData();

            formData.append("file", file);
            importButton.disabled = true;
            importButton.textContent = "読み込み中...";

            try {
                const response = await fetch(
                    "/admin/quizzes/import",
                    {
                        method: "POST",
                        body: formData,
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data.detail ||
                        "インポートに失敗しました。"
                    );
                }

                alert(
                    `${data.imported_count}問を読み込みました。`
                );

                window.location.reload();

            } catch (error) {
                console.error(error);

                alert(
                    error.message ||
                    "インポートに失敗しました。"
                );

                importButton.disabled = false;
                importButton.textContent = "インポート";
            }
        }
    );
}

    /*
     * 初期表示
     */
    sortRows();
    filterRows();
    updateBulkDeleteButton();
    updateSelectAllCheckbox();
});

