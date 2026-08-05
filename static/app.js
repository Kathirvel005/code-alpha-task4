/**
 * app.js - Real-time Interactive Controller for Nova AI Chatbot
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const messagesContainer = document.getElementById("messagesContainer");
    const charCount = document.getElementById("charCount");
    const liveSentimentBadge = document.getElementById("liveSentimentBadge");
    const statUserName = document.getElementById("statUserName");
    const statTotalTurns = document.getElementById("statTotalTurns");
    const statDuration = document.getElementById("statDuration");
    const fillPos = document.getElementById("fillPos");
    const fillNeu = document.getElementById("fillNeu");
    const fillNeg = document.getElementById("fillNeg");
    const cntPos = document.getElementById("cntPos");
    const cntNeu = document.getElementById("cntNeu");
    const cntNeg = document.getElementById("cntNeg");
    
    // Sidebar & Modals
    const chatSidebar = document.getElementById("chatSidebar");
    const menuToggleBtn = document.getElementById("menuToggleBtn");
    const closeSidebarBtn = document.getElementById("closeSidebarBtn");
    const helpModalBtn = document.getElementById("helpModalBtn");
    const helpModal = document.getElementById("helpModal");
    const closeHelpModal = document.getElementById("closeHelpModal");
    
    // Action Buttons
    const soundToggleBtn = document.getElementById("soundToggleBtn");
    const quickClearBtn = document.getElementById("quickClearBtn");
    const clearChatBtn = document.getElementById("clearChatBtn");
    const exportMdBtn = document.getElementById("exportMdBtn");
    const exportJsonBtn = document.getElementById("exportJsonBtn");
    const quickChips = document.querySelectorAll(".chip");

    let soundEnabled = true;
    let audioCtx = null;

    // Web Audio Synthesizer for UI sound effects
    function playBeep(type = "bot") {
        if (!soundEnabled) return;
        try {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            if (type === "user") {
                osc.frequency.setValueAtTime(440, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.1);
                gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.1);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.1);
            } else {
                osc.frequency.setValueAtTime(659.25, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(523.25, audioCtx.currentTime + 0.15);
                gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.15);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.15);
            }
        } catch (e) {
            // Audio context not allowed or unsupported
        }
    }

    // Toggle Sound Button
    soundToggleBtn.addEventListener("click", () => {
        soundEnabled = !soundEnabled;
        soundToggleBtn.textContent = soundEnabled ? "🔊" : "🔇";
        soundToggleBtn.title = soundEnabled ? "Sound Enabled" : "Sound Muted";
    });

    // Auto-resize textarea
    userInput.addEventListener("input", () => {
        userInput.style.height = "auto";
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
        charCount.textContent = `${userInput.value.length}/1000`;
    });

    // Keyboard Shortcuts (Enter to send, Shift+Enter for new line)
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event("submit"));
        }
    });

    // Quick Chips Click Handling
    quickChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const prompt = chip.getAttribute("data-prompt");
            userInput.value = prompt;
            userInput.dispatchEvent(new Event("input"));
            chatForm.dispatchEvent(new Event("submit"));
        });
    });

    // Sidebar Toggle
    if (menuToggleBtn && chatSidebar) {
        menuToggleBtn.addEventListener("click", () => chatSidebar.classList.toggle("open"));
    }
    if (closeSidebarBtn && chatSidebar) {
        closeSidebarBtn.addEventListener("click", () => chatSidebar.classList.remove("open"));
    }

    // Help Modal
    if (helpModalBtn && helpModal) {
        helpModalBtn.addEventListener("click", () => helpModal.style.display = "flex");
    }
    if (closeHelpModal && helpModal) {
        closeHelpModal.addEventListener("click", () => helpModal.style.display = "none");
    }
    window.addEventListener("click", (e) => {
        if (e.target === helpModal) helpModal.style.display = "none";
    });

    // Format text with basic markdown styling
    function formatMessageText(text) {
        if (!text) return "";
        let formatted = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Format bold **text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        // Format italic *text*
        formatted = formatted.replace(/\*(.*?)\*/g, "<em>$1</em>");
        // Format inline `code`
        formatted = formatted.replace(/`(.*?)`/g, "<code>$1</code>");
        // Format spoiler/answers ||spoiler||
        formatted = formatted.replace(/\|\|(.*?)\|\|/g, "<span class='spoiler'>$1</span>");
        // Format bullet points
        formatted = formatted.replace(/^[•\-]\s*(.*)$/gm, "<li>$1</li>");
        if (formatted.includes("<li>")) {
            formatted = formatted.replace(/(<li>.*<\/li>)/s, "<ul style='margin-left: 16px; margin-top: 4px;'>$1</ul>");
        }
        // Format newlines to paragraphs / line breaks
        formatted = formatted.replace(/\n\n/g, "</p><p>").replace(/\n/g, "<br>");
        return `<p>${formatted}</p>`;
    }

    // Append Message to UI
    function appendMessage(sender, text, timeStr = null, meta = {}) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender === "user" ? "user-message" : "bot-message"}`;

        const isUser = sender === "user";
        const avatarText = isUser ? "👤" : "🤖";
        const authorText = isUser ? (meta.user_name || "You") : "Nova AI";
        const time = timeStr || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        msgDiv.innerHTML = `
            <div class="msg-avatar">${avatarText}</div>
            <div class="msg-bubble">
                <div class="msg-author">${authorText}</div>
                <div class="msg-text">${formatMessageText(text)}</div>
                <div class="msg-time">${time}</div>
            </div>
        `;

        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Show Typing Indicator
    function showTypingIndicator() {
        const indicator = document.createElement("div");
        indicator.id = "typingIndicator";
        indicator.className = "message bot-message";
        indicator.innerHTML = `
            <div class="msg-avatar">🤖</div>
            <div class="msg-bubble">
                <div class="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(indicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return indicator;
    }

    function removeTypingIndicator() {
        const ind = document.getElementById("typingIndicator");
        if (ind) ind.remove();
    }

    // Update Session Analytics in Sidebar
    function updateStats(stats, sentiment = null) {
        if (!stats) return;
        if (statUserName) statUserName.textContent = stats.user_name || "Anonymous";
        if (statTotalTurns) statTotalTurns.textContent = stats.total_turns || 0;
        if (statDuration) statDuration.textContent = stats.duration_formatted || "0m 0s";

        const dist = stats.sentiment_distribution || { positive: 0, neutral: 0, negative: 0 };
        const total = (dist.positive + dist.neutral + dist.negative) || 1;

        if (cntPos) cntPos.textContent = dist.positive;
        if (cntNeu) cntNeu.textContent = dist.neutral;
        if (cntNeg) cntNeg.textContent = dist.negative;

        if (fillPos) fillPos.style.width = `${(dist.positive / total) * 100}%`;
        if (fillNeu) fillNeu.style.width = `${(dist.neutral / total) * 100}%`;
        if (fillNeg) fillNeg.style.width = `${(dist.negative / total) * 100}%`;

        if (sentiment && liveSentimentBadge) {
            const badgeIcons = { positive: "😊 Positive", negative: "🙁 Negative", neutral: "😐 Neutral" };
            liveSentimentBadge.textContent = badgeIcons[sentiment] || "😐 Neutral";
        }
    }

    // Handle Form Submit
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        // Reset input box
        userInput.value = "";
        userInput.style.height = "auto";
        charCount.textContent = "0/1000";

        // Display user message in UI
        appendMessage("user", text);
        playBeep("user");

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            removeTypingIndicator();

            if (response.ok) {
                appendMessage("bot", data.reply, null, { user_name: data.user_name });
                playBeep("bot");
                updateStats(data.stats, data.sentiment);
            } else {
                appendMessage("bot", `⚠️ Error: ${data.reply || "Something went wrong."}`);
            }
        } catch (err) {
            removeTypingIndicator();
            appendMessage("bot", "⚠️ Network error connecting to Nova AI server.");
        }
    });

    // Clear Chat Action
    async function clearConversation() {
        if (!confirm("Are you sure you want to clear this conversation and reset memory?")) return;
        try {
            await fetch("/api/clear", { method: "POST" });
            messagesContainer.innerHTML = `
                <div class="message bot-message welcome-card">
                    <div class="msg-avatar">🤖</div>
                    <div class="msg-bubble">
                        <div class="msg-author">Nova AI • Assistant</div>
                        <div class="msg-text">
                            <p>🧹 Conversation memory has been cleared. What would you like to explore next?</p>
                        </div>
                        <div class="msg-time">Just now</div>
                    </div>
                </div>
            `;
            const statsRes = await fetch("/api/stats");
            const stats = await statsRes.json();
            updateStats(stats, "neutral");
        } catch (e) {
            console.error("Failed to clear chat", e);
        }
    }

    if (quickClearBtn) quickClearBtn.addEventListener("click", clearConversation);
    if (clearChatBtn) clearChatBtn.addEventListener("click", clearConversation);

    // Export Actions
    if (exportMdBtn) {
        exportMdBtn.addEventListener("click", () => {
            window.location.href = "/api/export/md";
        });
    }
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener("click", () => {
            window.location.href = "/api/export/json";
        });
    }
});
