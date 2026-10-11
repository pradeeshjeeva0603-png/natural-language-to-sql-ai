// ---------------- LOGIN ----------------

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const button = document.getElementById("loginButton");
        const errorElement = document.getElementById("loginError");

        button.disabled = true;
        button.textContent = "Signing in...";
        errorElement.textContent = "";

        try {

            const response = await fetch("/api/login", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    username: username,
                    password: password
                })

            });

            const data = await response.json();

            if (response.ok && data.success) {

                window.location.href = data.redirect;

            } else {

                errorElement.textContent =
                    data.error || "Unable to sign in.";

            }

        } catch (error) {

            errorElement.textContent =
                "Unable to connect to the server.";

        } finally {

            button.disabled = false;
            button.innerHTML = 'Sign In <span>→</span>';

        }

    });

}


// ---------------- DASHBOARD ----------------

const queryForm = document.getElementById("queryForm");

if (queryForm) {

    const questionInput = document.getElementById("questionInput");
    const chatMessages = document.getElementById("chatMessages");
    const welcomeSection = document.getElementById("welcomeSection");
    const sendButton = document.getElementById("sendButton");

    // Prevent HTML injection by treating all text as text
    function createElement(tag, className, text) {

        const element = document.createElement(tag);

        if (className) {
            element.className = className;
        }

        if (text !== undefined) {
            element.textContent = text;
        }

        return element;
    }


    // Add a message card
    function addMessage(label, content, isUser = false) {

        const card = createElement(
            "div",
            "chat-message" + (isUser ? " user-message" : "")
        );

        card.appendChild(
            createElement("div", "message-label", label)
        );

        card.appendChild(
            createElement("div", "message-content", content)
        );

        chatMessages.appendChild(card);

        return card;
    }


    // Create results table
    function createResultsTable(results) {

        const card = createElement("div", "result-card");

        const heading = createElement("div", "result-heading");

        heading.appendChild(
            createElement("span", "", "Query Results")
        );

        heading.appendChild(
            createElement(
                "span",
                "result-count",
                `${results.length} row(s)`
            )
        );

        card.appendChild(heading);

        const wrapper = createElement("div", "table-wrapper");
        const table = createElement("table", "result-table");

        const tbody = createElement("tbody");

        if (results.length > 0) {

            const columnCount = Math.max(
                ...results.map(row => row.length)
            );

            const thead = createElement("thead");
            const headerRow = createElement("tr");

            for (let i = 0; i < columnCount; i++) {

                const th = createElement("th", "", `Column ${i + 1}`);

                headerRow.appendChild(th);

            }

            thead.appendChild(headerRow);
            table.appendChild(thead);

            results.forEach(row => {

                const tr = createElement("tr");

                row.forEach(value => {

                    const td = createElement(
                        "td",
                        "",
                        value === null ? "NULL" : String(value)
                    );

                    tr.appendChild(td);

                });

                tbody.appendChild(tr);

            });

        } else {

            const row = createElement("tr");
            const cell = createElement(
                "td",
                "",
                "No rows returned."
            );

            row.appendChild(cell);
            tbody.appendChild(row);

        }

        table.appendChild(tbody);
        wrapper.appendChild(table);
        card.appendChild(wrapper);

        return card;
    }


    // Create SQL viewer
    function createSQLViewer(sql) {

        const details = createElement("details", "sql-details");

        const summary = createElement(
            "summary",
            "",
            "View Generated SQL"
        );

        const code = createElement("pre", "sql-code", sql);

        const copyButton = createElement(
            "button",
            "copy-button",
            "Copy SQL"
        );

        copyButton.type = "button";

        copyButton.addEventListener("click", async function () {

            try {

                await navigator.clipboard.writeText(sql);

                copyButton.textContent = "Copied!";

                setTimeout(() => {
                    copyButton.textContent = "Copy SQL";
                }, 1500);

            } catch {

                copyButton.textContent =
                    "Clipboard unavailable";

            }

        });

        details.appendChild(summary);
        details.appendChild(copyButton);
        details.appendChild(code);

        return details;
    }


    // Submit a question
    async function askQuestion(question) {

        if (!question.trim()) {
            return;
        }

        welcomeSection.style.display = "none";

        addMessage("YOU", question, true);

        const responseCard = addMessage(
            "AI DATABASE ASSISTANT",
            "Generating SQL and retrieving database results..."
        );

        responseCard.appendChild(
            createElement("div", "loading-message", "Please wait...")
        );

        sendButton.disabled = true;
        questionInput.disabled = true;

        try {

            const response = await fetch("/api/query", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })

            });

            const data = await response.json();

            // Clear the loading message
            responseCard.replaceChildren();

            responseCard.appendChild(
                createElement(
                    "div",
                    "message-label",
                    "AI DATABASE ASSISTANT"
                )
            );

            if (!response.ok || !data.success) {

                responseCard.appendChild(
                    createElement(
                        "div",
                        "error-card",
                        data.error || "Something went wrong."
                    )
                );

                if (data.sql) {

                    responseCard.appendChild(
                        createSQLViewer(data.sql)
                    );

                }

                return;
            }

            // Natural-language answer
            responseCard.appendChild(
                createElement(
                    "div",
                    "message-content",
                    data.answer
                )
            );

            // SQL validation status
            responseCard.appendChild(
                createElement(
                    "p",
                    "result-count",
                    "✓ " + data.validation
                )
            );

            // Results table
            responseCard.appendChild(
                createResultsTable(data.results)
            );

            // Generated SQL
            responseCard.appendChild(
                createSQLViewer(data.sql)
            );

        } catch (error) {

            responseCard.replaceChildren();

            responseCard.appendChild(
                createElement(
                    "div",
                    "message-label",
                    "CONNECTION ERROR"
                )
            );

            responseCard.appendChild(
                createElement(
                    "div",
                    "error-card",
                    "Unable to connect to the server. Make sure Flask is running."
                )
            );

        } finally {

            sendButton.disabled = false;
            questionInput.disabled = false;
            questionInput.focus();

        }

    }


    // Input form
    queryForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const question = questionInput.value.trim();

        if (!question) {
            return;
        }

        questionInput.value = "";

        await askQuestion(question);

    });


    // Quick questions
    document.querySelectorAll(".quick-question").forEach(button => {

        button.addEventListener("click", function () {

            const question = this.dataset.question;

            questionInput.value = question;

            questionInput.focus();

        });

    });


    // New conversation
    document.getElementById("newChatButton")
        .addEventListener("click", function () {

            chatMessages.replaceChildren();

            welcomeSection.style.display = "block";

            questionInput.value = "";
            questionInput.focus();

        });


    // Logout
    document.getElementById("logoutButton")
        .addEventListener("click", async function () {

            try {

                const response = await fetch("/api/logout", {
                    method: "POST"
                });

                const data = await response.json();

                if (data.redirect) {

                    window.location.href = data.redirect;

                }

            } catch {

                alert("Unable to log out. Please try again.");

            }

        });

}