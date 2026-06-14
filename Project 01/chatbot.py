"""
DecodeBot - Futuristic Terminal AI Assistant
=============================================
Version    : 2.0 (10/10 Production Build)
Author     : Darshil
Purpose    : AI Internship Project — Interactive Rule-Based Chatbot
Description: A cinematic, fault-tolerant, immersive terminal assistant
             built on beginner Python concepts with professional engineering.

Usage:
    python chatbot.py

Requirements:
    colorama>=0.4.6   (optional — degrades gracefully without it)
"""

# ─────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────

import os
import sys
import time
import random
import signal
import datetime
import unicodedata

# ── Colorama (optional — graceful fallback if missing) ──────────────────────
COLOR_SUPPORT = False
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
    COLOR_SUPPORT = True
except ImportError:
    print("[WARNING] colorama not installed. Running in plain-text mode.")
    print("         Install it with:  pip install colorama>=0.4.6\n")

    # Stub objects so every Fore.X and Style.X still works without crashing
    class _Stub:
        def __getattr__(self, _):
            return ""
    Fore  = _Stub()
    Style = _Stub()


# ─────────────────────────────────────────────
#  CONSTANTS & CONFIGURATION
# ─────────────────────────────────────────────

BOT_NAME          = "DecodeBot"
LOG_FILE          = "conversation_log.txt"
UNKNOWN_LOG_FILE  = "unknown_queries.log"
MAX_LOG_BYTES     = 1_000_000        # 1 MB — log rotation threshold
MAX_INPUT_CHARS   = 200              # Hard cap on user input length
VERSION           = "2.0"

# Global state
_logging_disabled      = False       # Set True if disk-full error occurs
_unknown_streak        = 0           # Counter for consecutive unknown inputs
_recent_topics         = []          # Circular buffer of last 3 topics
_user_name             = "User"      # Set during startup


# ─────────────────────────────────────────────
#  RESPONSE POOLS  (5+ variations each)
# ─────────────────────────────────────────────

GREETING_RESPONSES = [
    "Hey {name}! Neural handshake confirmed. 🤝 What can I process for you?",
    "Hello {name}! DecodeBot online and ready to roll. 🚀",
    "Greetings, {name}! All systems nominal. How can I assist?",
    "Yo {name}! Signal received. Let's get to work. ⚡",
    "Hi {name}! Warm welcome from the AI core. 😊 What's on your mind?",
    "Hey hey {name}! Uptime 100%. Ready for your commands. 🔋",
]

HOW_ARE_YOU_RESPONSES = [
    "Running at peak efficiency, {name}! All modules green. ✅",
    "Fantastic! Processing capacity at 100%. How about you, {name}?",
    "Never better — electrons flowing smoothly today. 😄",
    "Optimal. My mood buffer is overflowing with positivity, {name}! ☀️",
    "All systems go! Thanks for asking, {name}. 🚀",
    "Feeling electric! Ready to conquer whatever you throw at me. ⚡",
]

MOTIVATIONAL_RESPONSES = [
    "You've got this, {name}! Every expert was once a beginner. 💪",
    "Remember: even the most powerful AI started as a single 'Hello World'. Keep going! 🌟",
    "Setbacks are just plot twists in your success story, {name}. Push forward! 🔥",
    "The fact that you're still here means you haven't given up — that's strength. 💎",
    "Every line of code you write is a step toward mastery, {name}. Keep building! 🏗️",
    "Tough days train you for epic wins. You're forging something amazing. ⚔️",
    "Progress > Perfection. One small step today = massive leaps tomorrow. 🚀",
    "Even machines need debugging sometimes, {name}. So do humans — and that's okay. 🛠️",
]

UNKNOWN_RESPONSES = [
    "Hmm... my neural network is still learning that one, {name}. 🤔",
    "Interesting input detected. Processing... no match found. Try 'help'! 💡",
    "That command isn't in my current database, {name}. But I'm always evolving! 🔄",
    "404: Response not found. Type 'help' to see what I *do* know! 😅",
    "My response matrix drew a blank on that one. Let's try something else? 🌀",
    "Input logged for future training. Meanwhile, type 'help' for available commands. 📝",
]

JOKES = [
    "Why do programmers prefer dark mode?\n   Because light attracts bugs! 🐛",
    "Why did Python break up with Java?\n   Too much class drama. 😂",
    "Why do programmers hate nature?\n   Too many bugs and no stack trace! 🌿",
    "What's a computer's favourite snack?\n   Microchips. 🍟",
    "Why was the developer broke?\n   Because he used up all his cache! 💸",
    "How do you comfort a JavaScript developer?\n   You reassure them: 'undefined is not the end.' 🤣",
    "Why did the programmer quit his job?\n   Because he didn't get arrays. 📊",
    "What do you call a programmer from Finland?\n   Nerdic! 😄",
    "Why do Java developers wear glasses?\n   Because they don't C#! 👓",
    "What's the object-oriented way to get wealthy?\n   Inheritance. 💰",
]

AI_FACTS = [
    "🧠 AI stands for Artificial Intelligence — machines simulating human reasoning.",
    "📊 Machine Learning is a subset of AI where systems learn from data patterns.",
    "🐍 Python is the most popular programming language in AI and Data Science.",
    "🤖 The term 'Artificial Intelligence' was coined by John McCarthy in 1956.",
    "🔢 Neural Networks are inspired by the biological structure of the human brain.",
    "🌐 GPT models are trained on hundreds of billions of text tokens from the internet.",
    "♟️ In 1997, IBM's Deep Blue defeated world chess champion Garry Kasparov.",
    "🎨 AI can now generate photorealistic images, music, and even full videos.",
    "🩺 AI is used in medical imaging to detect cancer earlier than human doctors.",
    "🚗 Self-driving cars use a combination of computer vision, AI, and sensor fusion.",
    "💬 Natural Language Processing (NLP) allows computers to understand human language.",
]

FUN_FACTS = [
    "🌍 Honey never spoils — archaeologists found 3,000-year-old honey in Egyptian tombs!",
    "🐙 Octopuses have three hearts and blue blood.",
    "⚡ Lightning strikes Earth about 100 times every second.",
    "🔢 The number of atoms in the observable universe is estimated at 10^80.",
    "🦈 Sharks are older than trees — they've existed for over 450 million years.",
    "🌙 The Moon is drifting away from Earth at about 3.8 cm per year.",
    "🐜 Ants have been farming fungi for over 50 million years.",
]

PYTHON_FACTS = [
    "🐍 Python was created by Guido van Rossum and first released in 1991.",
    "📦 Python has over 400,000 packages on PyPI (Python Package Index).",
    "🔤 Python's name is inspired by Monty Python's Flying Circus, not the snake!",
    "🚀 Python is used by NASA, Google, Netflix, Instagram, and thousands of startups.",
    "🧪 Python is the #1 language for AI, data science, automation, and scripting.",
    "💡 Python code reads almost like English — that's why beginners love it!",
    "🏆 Python has been ranked the most popular programming language for multiple years.",
]


# ─────────────────────────────────────────────
#  UTILITY: COLOR HELPERS
# ─────────────────────────────────────────────

def cyan(text):
    """Return cyan-colored text (headers)."""
    return f"{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def green(text):
    """Return green-colored text (bot replies)."""
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"

def yellow(text):
    """Return yellow-colored text (system notifications)."""
    return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"

def red(text):
    """Return red-colored text (errors / shutdown)."""
    return f"{Fore.RED}{text}{Style.RESET_ALL}"

def magenta(text):
    """Return magenta-colored text (user prompts)."""
    return f"{Fore.MAGENTA}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def dim(text):
    """Return dimmed text (secondary info)."""
    return f"{Style.DIM}{text}{Style.RESET_ALL}"


# ─────────────────────────────────────────────
#  UTILITY: TYPING EFFECT
# ─────────────────────────────────────────────

def typing_effect(text, delay=0.025, color_fn=None):
    """
    Print text character-by-character to simulate AI typing.

    Args:
        text     (str)      : The message to display.
        delay    (float)    : Pause between each character in seconds.
        color_fn (callable) : Optional color wrapper (e.g. green).
    """
    if color_fn:
        # Apply color to the whole string, then stream it
        colored = color_fn(text)
        # Detect if color codes are active (non-empty prefix)
        prefix  = color_fn("") if COLOR_SUPPORT else ""
        suffix  = Style.RESET_ALL if COLOR_SUPPORT else ""
        sys.stdout.write(prefix)
        sys.stdout.flush()
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write(suffix + "\n")
        sys.stdout.flush()
    else:
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        print()


def animated_dots(message, count=3, delay=0.45):
    """
    Display a message followed by animated loading dots.

    Args:
        message (str)   : Text to show before the dots.
        count   (int)   : Number of dots to animate.
        delay   (float) : Pause between dots.
    """
    sys.stdout.write(yellow(message))
    sys.stdout.flush()
    for _ in range(count):
        time.sleep(delay)
        sys.stdout.write(yellow("."))
        sys.stdout.flush()
    print()


# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────

def _rotate_log_if_needed(filepath):
    """
    Truncate a log file if it exceeds MAX_LOG_BYTES.

    Args:
        filepath (str): Path to the log file.
    """
    try:
        if os.path.exists(filepath) and os.path.getsize(filepath) > MAX_LOG_BYTES:
            # Keep the last 50 lines to preserve recent context
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            keep = lines[-50:] if len(lines) > 50 else lines
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"[LOG ROTATED — {datetime.datetime.now()}]\n")
                f.writelines(keep)
    except OSError:
        pass  # Rotation failure is non-fatal


def log_conversation(speaker, message):
    """
    Append a timestamped entry to conversation_log.txt.

    Args:
        speaker (str): "User" or bot name.
        message (str): The message content.
    """
    global _logging_disabled
    if _logging_disabled:
        return
    try:
        _rotate_log_if_needed(LOG_FILE)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {speaker}: {message}\n")
    except OSError as e:
        _logging_disabled = True
        print(yellow(f"\n⚠ Logging disabled (disk error: {e}). Chat continues normally.\n"))


def log_unknown(query):
    """
    Append an unrecognized query to unknown_queries.log.

    Args:
        query (str): The unrecognized user input.
    """
    global _logging_disabled
    if _logging_disabled:
        return
    try:
        _rotate_log_if_needed(UNKNOWN_LOG_FILE)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(UNKNOWN_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] UNKNOWN: {query}\n")
    except OSError:
        pass  # Unknown log failure is non-fatal


# ─────────────────────────────────────────────
#  INPUT VALIDATION
# ─────────────────────────────────────────────

def validate_input(raw):
    """
    Sanitize and validate user input.

    Handles:
      - Leading/trailing whitespace
      - Control characters and unusual Unicode
      - Empty strings
      - Oversized input (>MAX_INPUT_CHARS)

    Args:
        raw (str): Raw string from input().

    Returns:
        tuple(str, str):  (clean_input, warning_message_or_empty_string)
    """
    warning = ""

    # Normalize Unicode (NFC form), then strip non-printable control chars
    try:
        raw = unicodedata.normalize("NFC", raw)
    except (TypeError, ValueError):
        raw = ""

    # Remove ASCII control characters (except newline which is already stripped)
    cleaned = "".join(ch for ch in raw if unicodedata.category(ch) != "Cc" or ch == " ")
    cleaned = cleaned.strip()

    if not cleaned:
        return "", ""

    if len(cleaned) > MAX_INPUT_CHARS:
        warning = (
            f"⚡ Whoa! That's a {len(cleaned)}-character data-burst! "
            f"I've trimmed it to {MAX_INPUT_CHARS} characters for processing."
        )
        cleaned = cleaned[:MAX_INPUT_CHARS]

    return cleaned, warning


# ─────────────────────────────────────────────
#  CONTEXT MEMORY (last 3 topics)
# ─────────────────────────────────────────────

def _push_topic(topic):
    """
    Add a topic to the recent-topics buffer (max 3).

    Args:
        topic (str): A short keyword describing the current topic.
    """
    global _recent_topics
    if topic not in _recent_topics:
        _recent_topics.append(topic)
    if len(_recent_topics) > 3:
        _recent_topics.pop(0)


def _check_repeated_topic(topic):
    """
    Return a context-aware comment if a topic is repeated.

    Args:
        topic (str): Current topic keyword.

    Returns:
        str: Follow-up comment or empty string.
    """
    if _recent_topics.count(topic) >= 1:
        return f" (You seem really into {topic} today, {_user_name}! 😄)"
    return ""


# ─────────────────────────────────────────────
#  RESPONSE SUBSYSTEMS
# ─────────────────────────────────────────────

def tell_joke():
    """Return a randomly selected programming joke."""
    return "🎭 " + random.choice(JOKES)


def ai_fact():
    """Return a randomly selected AI fact."""
    return random.choice(AI_FACTS)


def fun_fact():
    """Return a randomly selected fun/general fact."""
    return random.choice(FUN_FACTS)


def get_time():
    """
    Return the current local time string.
    Falls back to UTC if timezone info is unavailable.

    Returns:
        str: Formatted time string with timezone.
    """
    try:
        now      = datetime.datetime.now().astimezone()
        tz_name  = now.strftime("%Z")
        tz_name  = tz_name if tz_name else "UTC"
        return f"🕐 Current time: {now.strftime('%I:%M:%S %p')} [{tz_name}]"
    except Exception:
        now = datetime.datetime.utcnow()
        return f"🕐 Current UTC time: {now.strftime('%I:%M:%S %p')} [UTC] (timezone unavailable)"


def get_date():
    """
    Return the current local date string.

    Returns:
        str: Formatted date string.
    """
    try:
        now = datetime.datetime.now().astimezone()
        return f"📅 Today is: {now.strftime('%A, %d %B %Y')}"
    except Exception:
        now = datetime.datetime.utcnow()
        return f"📅 Today (UTC) is: {now.strftime('%A, %d %B %Y')}"


# ─────────────────────────────────────────────
#  HELP MENU (paginated)
# ─────────────────────────────────────────────

HELP_PAGES = [
    # Page 1 — Greetings & Identity
    f"""
{cyan('─' * 56)}
{cyan('  DECODEBOT HELP SYSTEM  ·  Page 1 / 3')}
{cyan('─' * 56)}
  📌 GREETINGS
     hi · hello · hey · good morning · good evening

  📌 IDENTITY
     who are you
     what is your name
     what can you do
{cyan('─' * 56)}
  Press ENTER for next page, or type 'q' to close help.
""",
    # Page 2 — Utility & Entertainment
    f"""
{cyan('─' * 56)}
{cyan('  DECODEBOT HELP SYSTEM  ·  Page 2 / 3')}
{cyan('─' * 56)}
  📌 UTILITY
     time  ·  date  ·  help

  📌 ENTERTAINMENT
     tell joke  ·  fun fact  ·  ai fact

  📌 KNOWLEDGE
     what is ai
     tell me about python
     how are you
{cyan('─' * 56)}
  Press ENTER for next page, or type 'q' to close help.
""",
    # Page 3 — Emotional & Exit
    f"""
{cyan('─' * 56)}
{cyan('  DECODEBOT HELP SYSTEM  ·  Page 3 / 3')}
{cyan('─' * 56)}
  📌 EMOTIONAL SUPPORT
     i am sad  ·  i feel stressed
     i am tired  ·  motivate me

  📌 EXIT
     bye  ·  exit  ·  quit  ·  shutdown

  💡 TIP: All commands are case-insensitive.
     Partial matches work (e.g. "joke" → tell joke).
{cyan('─' * 56)}
  Press ENTER to close help.
""",
]


def show_help():
    """
    Display the paginated help menu.
    User presses ENTER to advance pages or types 'q' to exit help.
    """
    for i, page in enumerate(HELP_PAGES):
        print(page)
        try:
            choice = input("  ").strip().lower()
            if choice == "q":
                break
        except (EOFError, KeyboardInterrupt):
            break
        # Last page — no more input needed
        if i == len(HELP_PAGES) - 1:
            break


# ─────────────────────────────────────────────
#  CORE RESPONSE ENGINE
# ─────────────────────────────────────────────

def chatbot_response(user_input):
    """
    Match user input to the appropriate response category.

    Uses keyword matching on a lowercased, stripped version of the input.
    Updates the recent-topics buffer and consecutive-unknown counter.

    Args:
        user_input (str): Cleaned, validated user input.

    Returns:
        str: The bot's response string.
    """
    global _unknown_streak

    text = user_input.lower().strip()

    # ── Greetings ────────────────────────────────────────────────
    if any(w in text for w in ("hello", "hi", "hey", "good morning", "good evening", "sup", "yo")):
        _unknown_streak = 0
        _push_topic("greetings")
        return random.choice(GREETING_RESPONSES).format(name=_user_name)

    # ── How are you ──────────────────────────────────────────────
    if "how are you" in text or "how r u" in text or "you okay" in text:
        _unknown_streak = 0
        _push_topic("wellbeing")
        return random.choice(HOW_ARE_YOU_RESPONSES).format(name=_user_name)

    # ── Identity ─────────────────────────────────────────────────
    if any(p in text for p in ("who are you", "your name", "what are you", "introduce")):
        _unknown_streak = 0
        _push_topic("identity")
        return (
            f"I'm {cyan(BOT_NAME)} v{VERSION} ⚡ — a futuristic rule-based AI assistant.\n"
            f"   Powered by: Python + creativity + a lot of if-else magic.\n"
            f"   I can chat, motivate, joke, share facts, and more.\n"
            f"   Type 'help' for the full command list, {_user_name}!"
        )

    # ── What can you do ──────────────────────────────────────────
    if "what can you do" in text or "capabilities" in text or "features" in text:
        _unknown_streak = 0
        return "Type 'help' to see everything I can do — it's actually pretty cool! 😎"

    # ── Mood / Emotional ─────────────────────────────────────────
    mood_triggers = ("sad", "tired", "stressed", "demotivated", "depressed",
                     "motivate", "unhappy", "anxious", "overwhelmed", "lonely")
    if any(w in text for w in mood_triggers):
        _unknown_streak = 0
        _push_topic("motivation")
        repeat_comment = _check_repeated_topic("motivation")
        return random.choice(MOTIVATIONAL_RESPONSES).format(name=_user_name) + repeat_comment

    # ── Jokes ─────────────────────────────────────────────────────
    if "joke" in text or "funny" in text or "make me laugh" in text:
        _unknown_streak = 0
        _push_topic("jokes")
        repeat_comment = _check_repeated_topic("jokes")
        return tell_joke() + repeat_comment

    # ── AI Fact ───────────────────────────────────────────────────
    if "ai fact" in text or "artificial intelligence fact" in text:
        _unknown_streak = 0
        _push_topic("AI")
        repeat_comment = _check_repeated_topic("AI")
        return ai_fact() + repeat_comment

    # ── Fun Fact ──────────────────────────────────────────────────
    if "fun fact" in text or "random fact" in text:
        _unknown_streak = 0
        _push_topic("facts")
        return fun_fact()

    # ── What is AI ───────────────────────────────────────────────
    if "what is ai" in text or "explain ai" in text or "tell me about ai" in text:
        _unknown_streak = 0
        _push_topic("AI")
        repeat_comment = _check_repeated_topic("AI")
        return (
            "🧠 AI (Artificial Intelligence) is the simulation of human intelligence\n"
            "   by machines — enabling them to learn, reason, and make decisions.\n"
            "   Modern AI powers everything from search engines to self-driving cars!"
            + repeat_comment
        )

    # ── Python ────────────────────────────────────────────────────
    if "python" in text:
        _unknown_streak = 0
        _push_topic("python")
        repeat_comment = _check_repeated_topic("python")
        return random.choice(PYTHON_FACTS) + repeat_comment

    # ── Time ──────────────────────────────────────────────────────
    if any(w in text for w in ("time", "clock", "hour")):
        _unknown_streak = 0
        return get_time()

    # ── Date ──────────────────────────────────────────────────────
    if any(w in text for w in ("date", "today", "day", "month", "year")):
        _unknown_streak = 0
        return get_date()

    # ── Help ──────────────────────────────────────────────────────
    if text in ("help", "commands", "menu", "?"):
        _unknown_streak = 0
        show_help()
        return ""   # help already printed

    # ── Exit triggers (handled upstream, but catch here too) ─────
    if any(w in text for w in ("bye", "exit", "quit", "shutdown", "close")):
        return "__EXIT__"

    # ── Unknown ───────────────────────────────────────────────────
    _unknown_streak += 1
    log_unknown(user_input)

    if _unknown_streak >= 3:
        _unknown_streak = 0
        return (
            f"I've been struggling to follow along, {_user_name}. 😅\n"
            f"   Type 'help' to see all the commands I understand!"
        )

    return random.choice(UNKNOWN_RESPONSES).format(name=_user_name)


# ─────────────────────────────────────────────
#  STARTUP SEQUENCE
# ─────────────────────────────────────────────

def display_banner():
    """
    Print the ASCII art banner and version info.
    Attempts to load assets/banner.txt; falls back to inline art.
    """
    inline_banner = rf"""
{cyan('╔══════════════════════════════════════════════════════╗')}
{cyan('║')}  {cyan('██████  ███████  ██████  ██████  ██████  ███████  ████████')}  {cyan('║')}
{cyan('║')}  {cyan(' ██  ██ ██      ██      ██  ██ ██   ██ ██      ██    ██')}  {cyan('║')}
{cyan('║')}  {cyan(' ██  ██ █████   ██      ██  ██ ██   ██ █████   ██    ██')}  {cyan('║')}
{cyan('║')}  {cyan(' ██  ██ ██      ██      ██  ██ ██   ██ ██      ██    ██')}  {cyan('║')}
{cyan('║')}  {cyan(' ██████  ███████ ██████ ██████ ██████  ███████  ██████')}   {cyan('║')}
{cyan('╠══════════════════════════════════════════════════════╣')}
{cyan('║')}    {yellow('⚡  DECODEBOT  ·  Futuristic AI Terminal Assistant')}       {cyan('║')}
{cyan('║')}    {dim(f'   Version {VERSION}  ·  Rule-Based Intelligence Engine')}        {cyan('║')}
{cyan('╚══════════════════════════════════════════════════════╝')}
    """

    # Try loading from file
    banner_path = os.path.join("assets", "banner.txt")
    if os.path.exists(banner_path):
        try:
            with open(banner_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(cyan(content))
            return
        except OSError:
            pass  # Fall through to inline banner

    print(inline_banner)


def loading_screen():
    """
    Display the cinematic AI boot sequence with animated messages.
    Simulates a realistic system initialization flow.
    """
    os.system("cls" if os.name == "nt" else "clear")
    display_banner()

    boot_steps = [
        ("Initializing neural communication modules",   0.6),
        ("Loading response matrix v2.0",                0.5),
        ("Calibrating personality engine",              0.5),
        ("Mounting knowledge base",                     0.4),
        ("Activating emotional response subsystem",     0.4),
        ("Applying terminal color schema",              0.35),
        ("Configuring conversation logger",             0.35),
        ("Running system integrity checks",             0.5),
        ("Establishing user context buffer",            0.3),
    ]

    for msg, pause in boot_steps:
        animated_dots(f"   {msg}", count=3, delay=pause / 3)

    time.sleep(0.3)
    print()
    print(green("   ✅  AI Core Stable — All systems nominal."))
    print(yellow("   ─" * 28))
    time.sleep(0.6)


# ─────────────────────────────────────────────
#  USER NAME COLLECTION
# ─────────────────────────────────────────────

def get_user_name():
    """
    Prompt for and validate the user's name at startup.

    Validation rules:
      - Strip whitespace
      - Reject empty strings or purely symbolic input
      - Default to 'User' if input is unusable

    Returns:
        str: Validated user name.
    """
    print()
    typing_effect(f"  {BOT_NAME}: Before we begin — what should I call you?", color_fn=green)
    try:
        raw_name = input(magenta("  You: ")).strip()
    except (EOFError, KeyboardInterrupt):
        return "User"

    # Keep only printable, alphabetic-ish characters for the name
    filtered = "".join(
        ch for ch in raw_name
        if unicodedata.category(ch) not in ("Cc", "Cf") and ch.strip()
    ).strip()

    if not filtered or not any(ch.isalpha() for ch in filtered):
        print(yellow("  [System] Name not recognized. Defaulting to 'User'."))
        return "User"

    # Capitalize nicely
    return filtered[:30].title()


# ─────────────────────────────────────────────
#  GRACEFUL SHUTDOWN
# ─────────────────────────────────────────────

def graceful_shutdown(triggered_by_signal=False):
    """
    Execute the cinematic shutdown sequence and exit cleanly.

    Args:
        triggered_by_signal (bool): True if called from a signal handler.
    """
    print()
    print(red("  ──────────────────────────────────────────────"))
    typing_effect(
        f"  {BOT_NAME}: Shutdown sequence initiated, {_user_name}...",
        delay=0.03, color_fn=red
    )

    shutdown_steps = [
        "Saving session context",
        "Flushing conversation logs",
        "Deallocating response buffers",
        "Powering down subsystems",
    ]
    for step in shutdown_steps:
        animated_dots(f"   {step}", count=3, delay=0.15)

    time.sleep(0.3)
    print()
    print(red("  ✖  DecodeBot offline. See you in the next session!"))
    print(red("  ──────────────────────────────────────────────"))
    print()

    log_conversation(BOT_NAME, f"[SESSION ENDED for {_user_name}]")
    sys.exit(0)


def handle_interrupt(signum, frame):
    """
    Signal handler for SIGINT (Ctrl+C).
    Routes to graceful_shutdown instead of a Python traceback.

    Args:
        signum: Signal number (unused).
        frame:  Current stack frame (unused).
    """
    print()  # Move past the "^C" on the current line
    typing_effect(
        f"\n  {BOT_NAME}: Ctrl+C detected — initiating graceful shutdown...",
        delay=0.025, color_fn=yellow
    )
    graceful_shutdown(triggered_by_signal=True)


# Register signal handler
signal.signal(signal.SIGINT, handle_interrupt)


# ─────────────────────────────────────────────
#  EXIT CONFIRMATION
# ─────────────────────────────────────────────

def confirm_exit():
    """
    Ask the user to confirm before shutting down.

    Returns:
        bool: True if user confirms, False otherwise.
    """
    try:
        typing_effect(
            f"  {BOT_NAME}: Are you sure you want to shut down, {_user_name}? (y/n)",
            delay=0.02, color_fn=yellow
        )
        answer = input(magenta("  You: ")).strip().lower()
        return answer in ("y", "yes", "yeah", "yep", "sure", "ok")
    except (EOFError, KeyboardInterrupt):
        return True


# ─────────────────────────────────────────────
#  MAIN CHAT LOOP
# ─────────────────────────────────────────────

def main():
    """
    Entry point — runs the full DecodeBot session:
      1. Boot animation
      2. Name collection
      3. Welcome message
      4. Main conversation loop
      5. Graceful shutdown
    """
    global _user_name

    # ── Boot ─────────────────────────────────────────────────────
    loading_screen()

    # ── Collect name ─────────────────────────────────────────────
    _user_name = get_user_name()

    # ── Log session start ─────────────────────────────────────────
    log_conversation(BOT_NAME, f"[SESSION STARTED for {_user_name}]")

    # ── Welcome ───────────────────────────────────────────────────
    print()
    print(yellow("  ─" * 28))
    typing_effect(
        f"  {BOT_NAME}: Welcome, {_user_name}! 🚀 Neural handshake complete.",
        delay=0.025, color_fn=green
    )
    typing_effect(
        f"  {BOT_NAME}: Type 'help' for commands, or just say hello!",
        delay=0.022, color_fn=green
    )
    print(yellow("  ─" * 28))
    print()

    # ── Conversation loop ─────────────────────────────────────────
    while True:
        try:
            raw = input(magenta(f"  {_user_name}: "))
        except EOFError:
            # Ctrl+D
            typing_effect(
                f"\n  {BOT_NAME}: EOF detected. Initiating shutdown...",
                color_fn=yellow
            )
            graceful_shutdown()
        except KeyboardInterrupt:
            # Backup handler (signal handler should catch this first)
            handle_interrupt(None, None)

        # ── Validate input ────────────────────────────────────────
        cleaned, warning = validate_input(raw)

        if warning:
            typing_effect(f"  {BOT_NAME}: {warning}", delay=0.02, color_fn=yellow)
            log_conversation(BOT_NAME, f"[INPUT TRUNCATED] {warning}")

        if not cleaned:
            response = f"Hello? Neural mic detected silence 😅 — try typing something, {_user_name}!"
            typing_effect(f"  {BOT_NAME}: {response}", delay=0.025, color_fn=green)
            continue

        # ── Log user input ────────────────────────────────────────
        log_conversation(_user_name, cleaned)

        # ── Get response ──────────────────────────────────────────
        response = chatbot_response(cleaned)

        # ── Handle exit ───────────────────────────────────────────
        if response == "__EXIT__":
            if confirm_exit():
                graceful_shutdown()
            else:
                typing_effect(
                    f"  {BOT_NAME}: Shutdown cancelled. Glad you're staying! 😊",
                    delay=0.025, color_fn=green
                )
            continue

        # ── Display response ──────────────────────────────────────
        if response:
            # Small delay to simulate "thinking"
            time.sleep(random.uniform(0.15, 0.35))
            typing_effect(f"  {BOT_NAME}: {response}", delay=0.022, color_fn=green)
            log_conversation(BOT_NAME, response)
            print()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    main()
