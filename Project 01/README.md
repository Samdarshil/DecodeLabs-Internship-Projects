# 🤖 DecodeBot — Futuristic Terminal AI Assistant

> *"A cinematic, rule-based AI chatbot that feels alive — built on beginner Python, engineered like a pro."*

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![colorama](https://img.shields.io/badge/colorama-≥0.4.6-green?style=flat-square)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)

---

## 📖 Project Overview

**DecodeBot** is a terminal-based AI assistant built entirely in Python using beginner-friendly concepts — `if-else`, `loops`, `functions`, `dictionaries`, and `string handling` — yet engineered to feel significantly more advanced than a typical student project.

It was created as part of an **Artificial Intelligence internship assignment**, with the goal of demonstrating:
- Structured programming skills
- Terminal UI design
- Software presentation quality
- Fault-tolerant architecture
- Cinematic user experience

No machine learning APIs. No internet. Pure logic and creative engineering.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🚀 Cinematic boot sequence | Animated loading screen simulating AI system initialization |
| 🎨 Colored terminal UI | Cyan, green, yellow, red, magenta — a cyberpunk console aesthetic |
| 🧠 Personality engine | Friendly, witty, energetic — never robotic or boring |
| 💬 Context memory | Remembers your name and the last 3 conversation topics |
| 😄 10+ jokes | Randomized programming humor to keep things fun |
| 🧪 11+ AI facts | Educational snippets about artificial intelligence |
| 💪 8+ motivational lines | Empathetic emotional support responses |
| ⏰ Time & date | Shows current time with timezone and today's date |
| ❓ Paginated help menu | 3-page interactive command guide |
| 📝 Conversation logging | Every exchange saved to `conversation_log.txt` |
| 🔍 Unknown query logging | Unrecognized inputs saved to `unknown_queries.log` |
| 🛡️ Full fault tolerance | Handles empty input, long input, special chars, Ctrl+C, Ctrl+D |
| 🔄 Log rotation | Auto-trims log files at 1 MB to prevent disk bloat |
| 🎯 Exit confirmation | Asks "Are you sure?" before shutting down |
| 🌈 Colorama fallback | Degrades gracefully to plain text if colorama isn't installed |

---

## 🛠️ Technologies Used

| Library | Purpose | Required? |
|---|---|---|
| `colorama` | Terminal colors | Optional (graceful fallback) |
| `random` | Response variation | Built-in |
| `time` | Typing animation, delays | Built-in |
| `datetime` | Time & date display | Built-in |
| `os` | Screen clearing, file paths | Built-in |
| `sys` | Output control, exit | Built-in |
| `signal` | Ctrl+C interrupt handling | Built-in |
| `unicodedata` | Input sanitization | Built-in |

---

## 📁 Project Structure

```
DecodeBot/
│
├── chatbot.py              ← Main application (all logic here)
├── conversation_log.txt    ← Auto-generated on first run
├── unknown_queries.log     ← Auto-generated on first run
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
│
├── screenshots/
│   └── demo.png            ← Add your own screenshot here
│
└── assets/
    └── banner.txt          ← (Optional) Custom ASCII art banner
```

---

## 🚀 Installation & Setup

### 1. Prerequisites

- Python **3.8 or higher**
- A terminal that supports ANSI escape codes  
  *(Windows: use Windows Terminal or PowerShell; avoid legacy CMD for best results)*

### 2. Clone / Download

```bash
# Option A — if using Git
git clone https://github.com/yourusername/DecodeBot.git
cd DecodeBot

# Option B — manual download
# Download and extract the project ZIP, then open a terminal in the folder
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run DecodeBot

```bash
python chatbot.py
```

---

## 💡 Usage Examples

| You type | DecodeBot replies |
|---|---|
| `hello` | Dynamic greeting using your name |
| `tell joke` | Random programming joke |
| `ai fact` | Educational AI snippet |
| `i am sad` | Empathetic motivational response |
| `time` | Current time with timezone |
| `date` | Today's full date |
| `what is ai` | Clear AI explanation |
| `tell me about python` | Random Python fact |
| `help` | Paginated 3-page command menu |
| `bye` | Shutdown with confirmation prompt |

## 🔧 Troubleshooting

### Colors not showing on Windows CMD

**Problem:** You see garbage like `←[32m` instead of green text.  
**Fix:** Use **Windows Terminal** or **PowerShell** instead of the legacy `cmd.exe`. Alternatively, run:
```bash
pip install colorama>=0.4.6
```
DecodeBot will still work without color — it degrades gracefully.

---

### `colorama` not found error

**Problem:** `ModuleNotFoundError: No module named 'colorama'`  
**Fix:**
```bash
pip install colorama>=0.4.6
```
Or just run without it — DecodeBot detects the missing library and runs in plain-text mode automatically.

---

### Ctrl+C shows a Python traceback

**Problem:** Pressing Ctrl+C prints an ugly error instead of shutting down gracefully.  
**Fix:** This should not happen in normal operation — DecodeBot registers a `signal.SIGINT` handler. If it does occur, check that you are running `chatbot.py` directly (`python chatbot.py`) and not from inside a restricted environment like IDLE.

---

### Log files growing too large

**Problem:** `conversation_log.txt` is taking up too much disk space.  
**Fix:** DecodeBot automatically trims log files at **1 MB**, keeping the most recent 50 lines. You can also safely delete the log files manually — they will be recreated on the next run.

---

### Emoji characters showing as boxes or `?`

**Problem:** On some older terminals, emoji renders incorrectly.  
**Fix:** Switch to a modern terminal with Unicode support (Windows Terminal, iTerm2, GNOME Terminal). The chat will still work normally — only the visual emoji may appear differently.

---

### `python` command not found

**Problem:** Running `python chatbot.py` gives "command not found".  
**Fix:** Try `python3 chatbot.py` instead. On some systems Python 3 is accessed via `python3`.

---

## ⚠️ Known Limitations

- **Rule-based only** — Responses are pattern-matched, not AI-generated. The bot cannot handle arbitrary natural language with true comprehension.
- **Session memory only** — User name and topic history reset when the program exits (no persistent cross-session memory).
- **No GUI** — This is a pure terminal application. No graphical interface.
- **Single language** — Only English input is supported.
- **No voice** — Text only; no speech recognition or text-to-speech in this version.

---

## 🔮 Future Upgrade Roadmap

| Upgrade | Technology |
|---|---|
| Graphical UI | `tkinter` or `PyQt6` |
| Voice assistant | `speech_recognition` + `pyttsx3` |
| Persistent memory | `SQLite` or `JSON` storage |
| Sentiment analysis | `TextBlob` or `VADER` |
| Plugin system | Dynamic module loading |
| Real-time updates | WebSocket integration |
| Containerization | Docker |
| Automated testing | `pytest` unit tests |
| CI/CD pipeline | GitHub Actions |
| Multi-language support | `i18n` / `gettext` |
| Theme system | Light / Dark / Cyberpunk / Hacker |
| Export conversation | PDF or JSON export |
| True NLP | `spaCy` intent parsing |
| Web interface | `Flask` + HTML frontend |
| AI backend (future) | Local LLM via `ollama` |

---

## 👨‍💻 Author

**Darshil**  
BCA Student — Artificial Intelligence Internship Project  
*"Building tomorrow's tools with today's fundamentals."*

---

## 📄 License

This project is open-source under the **MIT License**.  
Feel free to use, modify, and build upon it — just give credit!

---

*DecodeBot — Because your internship project shouldn't look like everyone else's.*
>>>>>>> 5b15163 (Initial commit)
