document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("chatInput");
    const sendBtn = document.getElementById("chatSend");
    const panel = document.getElementById("chatPanel");
    const closeBtn = document.getElementById("chatClose");
    const answerEl = document.getElementById("chatAnswer");
    const citationsEl = document.getElementById("chatCitations");
    const loadingEl = document.getElementById("chatLoading");

    function showPanel() {
        panel.classList.add("visible");
    }

    function hidePanel() {
        panel.classList.remove("visible");
        answerEl.textContent = "";
        citationsEl.innerHTML = "";
        citationsEl.classList.remove("has-items");
        loadingEl.classList.remove("active");
    }

    function showLoading() {
        answerEl.textContent = "";
        citationsEl.innerHTML = "";
        citationsEl.classList.remove("has-items");
        loadingEl.classList.add("active");
        showPanel();
    }

    function showAnswer(answer, citations) {
        loadingEl.classList.remove("active");
        answerEl.textContent = answer;

        if (citations && citations.length > 0) {
            citationsEl.innerHTML = `<div class="chat-citation-label">Sources</div>`;
            citations.forEach(function (c) {
                const a = document.createElement("a");
                a.className = "chat-citation-item";
                a.href = "/email/" + c.id;
                a.textContent = c.sender + " — " + c.subject;
                citationsEl.appendChild(a);
            });
            citationsEl.classList.add("has-items");
        }
    }

    async function sendQuestion() {
        const question = input.value.trim();
        if (!question) return;

        sendBtn.disabled = true;
        showLoading();

        try {
            // POST the form via fetch so we stay on the page
            const formData = new FormData();
            formData.append("chat_question", question);

            const response = await fetch(window.location.pathname, {
                method: "POST",
                body: formData,
            });

            const html = await response.text();

            // Parse the returned page to extract synthesis data
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");

            // Look for the injected __synthesis script
            const scripts = doc.querySelectorAll("script");
            let synthesis = null;
            scripts.forEach(function (s) {
                if (s.textContent.includes("__synthesis")) {
                    try {
                        const match = s.textContent.match(/window\.__synthesis\s*=\s*(\{[\s\S]*?\});/);
                        if (match) {
                            synthesis = eval("(" + match[1] + ")");
                        }
                    } catch (e) {
                        console.error("Parse error", e);
                    }
                }
            });

            if (synthesis) {
                showAnswer(synthesis.answer, synthesis.citations);
            } else {
                showAnswer("Sorry, I couldn't get a response. Please try again.", []);
            }

        } catch (err) {
            showAnswer("Network error — please try again.", []);
        }

        sendBtn.disabled = false;
    }

    // Send on button click
    sendBtn.addEventListener("click", sendQuestion);

    // Send on Enter key
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") sendQuestion();
    });

    // Close panel
    closeBtn.addEventListener("click", function () {
        hidePanel();
        input.value = "";
    });

    // If page was server-rendered with a synthesis result, show it
    if (window.__synthesis) {
        input.value = window.__synthesis.question || "";
        showAnswer(window.__synthesis.answer, window.__synthesis.citations);
    }
});
