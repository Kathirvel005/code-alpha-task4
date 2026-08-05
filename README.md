# 🤖 Nova AI — Advanced Hybrid NLP & Rule-Based Chatbot

A production-grade, multi-modal conversational chatbot built with Python. Powered by a hybrid Natural Language Processing (NLP) intent engine, typo-tolerant fuzzy matching, sentiment analysis, multi-turn stateful memory, dynamic built-in tools (safe AST math evaluator, unit conversions, live datetime, trivia/jokes), and a sleek modern Web UI.

---

## 🌟 Key Features

### 🧠 1. Intelligent Natural Language Processing (NLP)
- **Typo & Variation Tolerance**: Uses SequenceMatcher fuzzy similarity to understand misspelled words (e.g. `"helo"`, `"gudbye"`, `"what ur name"`).
- **Sentiment Analysis**: Real-time polarity scoring (`positive`, `neutral`, `negative`) with visual mood indicators.
- **Entity Extraction**: Automatically detects and remembers user names (`"My name is Alex"`), math expressions, units, and dates.

### 💾 2. Multi-Turn Context & Memory
- **User Persona Tracking**: Remembers the user's name across turns and personalizes future answers.
- **Session Analytics**: Tracks total turns, sentiment distribution, and duration.
- **Transcript Export**: Export conversations anytime to formatted **Markdown** (`.md`) or structured **JSON** (`.json`).

### 🧮 3. Dynamic Built-in Tools
- **Safe Math Evaluator**: AST-based parser computing complex expressions, powers, and functions (`calculate (50 * 2) + sqrt(144)` or `2^8`) without dangerous `eval()`.
- **Unit & Currency Conversions**: Length (`km` ⇄ `miles`, `m` ⇄ `ft`), Weight (`kg` ⇄ `lbs`), Temperature (`°C` ⇄ `°F` ⇄ `K`), and Digital Storage (`GB` ⇄ `MB` ⇄ `Bytes`).
- **Live Date & Time**: Real-time timezone-aware queries (`what time is it`, `what is today's date`).
- **Entertainment**: Curated tech jokes, programming trivia, motivational quotes, and riddles.

### 💻 4. Dual Interfaces
1. **Interactive Colored Terminal CLI**: ANSI/Colorama styling with custom avatars, banners, sentiment badges, and robust error handling.
2. **Modern Glassmorphic Web App**: Built with Flask, featuring glowing dark-theme aesthetics, typing indicator animations, quick prompt chips, audio feedback, and session analytics.

---

## 📂 Project Architecture

```
code alpha 4/
├── basic_chatbot.py      # Main CLI entry point (backwards-compatible)
├── advanced_chatbot.py   # Full OO Chatbot class and CLI orchestrator
├── nlp_engine.py         # Intent classification, fuzzy matching & sentiment
├── memory.py             # Session memory, analytics & transcript exporter
├── tools.py              # AST Math parser, DateTime, Unit converter & Jokes
├── app.py                # Flask Web Server & REST API endpoints
├── test_chatbot.py       # 21 comprehensive automated unit tests
├── templates/
│   └── index.html        # Responsive glassmorphic Web UI
├── static/
│   ├── style.css         # Dark neon & glassmorphism stylesheet
│   └── app.js            # Real-time WebSocket/Fetch client controller
└── README.md             # Project documentation
```

---

## 🚀 How to Run

### 1. Terminal CLI Mode
To start the chatbot directly in your terminal:
```powershell
py basic_chatbot.py
# or
py advanced_chatbot.py
```

### 2. Modern Web Interface Mode
To launch the interactive Web Dashboard:
```powershell
py app.py
```
Then open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

### 3. Run Automated Unit Tests
To verify all NLP components, memory, tools, and endpoints:
```powershell
py -m unittest test_chatbot.py -v
```

---

## ⚡ Slash Commands

| Command | Description |
| :--- | :--- |
| `/help` | Show full list of features, tips, and commands |
| `/stats` | View session duration, turns, and sentiment breakdown |
| `/history` | Display recent conversation turns |
| `/clear` | Clear conversation history and reset context memory |
| `/export md` | Export chat transcript as a Markdown document |
| `/export json` | Export conversation data as a JSON file |
| `/quit` or `bye` | Exit the chatbot session cleanly |

---

## 💬 Example CLI Conversation

```text
============================================================
       🤖  NOVA ADVANCED AI CHATBOT  🤖       
============================================================
• Type your message or questions naturally.
• Try: calculate 25 * 4, what time is it, joke, convert 100 km to miles
• Special commands: /help, /stats, /history, /clear, /export
• Type 'bye' or '/quit' to exit.
============================================================

You: hello there!
🤖 Nova [greeting | 😊]: Hello there! How can I assist you today?

You: my name is Kathir
🤖 Nova [tell_user_name | 😊]: Nice to meet you, **Kathir**! I'll remember that for the rest of our chat. 😊

You (Kathir): what is my name?
🤖 Nova [ask_user_name | 😐]: Your name is **Kathir**! I have it saved in my memory. 😊

You (Kathir): calculate (50 * 2) + sqrt(144)
🤖 Nova [calculate | 😐]: 🧮 Result: **(50 * 2) + sqrt(144) = 112**

You (Kathir): convert 100 km to miles
🤖 Nova [unit_conversion | 😐]: 📏 **100.0 km = 62.1371 miles**

You (Kathir): what time is it?
🤖 Nova [datetime | 😐]: 🕒 Current Time: **12:50:00 AM**
📅 Today's Date: **Thursday, August 06, 2026**

You (Kathir): tell me a joke
🤖 Nova [joke | 😐]: 🎭 Why did the Python programmer get glasses? Because they couldn't C#! 🐍

You (Kathir): /stats
🤖 Nova [cmd_stats | 😐]: 📊 **Session Statistics [session_20260806_005000]**
• **User**: Kathir
• **Active Duration**: 1m 15s
• **Total Turns**: 8
• **Sentiment Breakdown**: 😊 Positive: 2 | 😐 Neutral: 6 | 🙁 Negative: 0

You (Kathir): bye
🤖 Nova [farewell | 😐]: Goodbye Kathir! It was wonderful talking with you.
```

---

## 🛡️ Bug Fixes Applied from Original
1. **Windows Unicode/Emoji Crash**: Fixed `UnicodeEncodeError` by adding dynamic UTF-8 stream reconfigurations.
2. **Rigid String Matching**: Replaced rigid `== "hello"` checks with regex token matching and SequenceMatcher fuzzy similarity for typo tolerance.
3. **Memory Amnesia**: Added multi-turn memory manager to retain user identities and session states.
4. **Crash on Empty Input / Interrupt**: Handled EOF and `Ctrl+C` gracefully.
