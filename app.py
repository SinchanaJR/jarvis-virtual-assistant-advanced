import os
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-this-key")


def get_reply(message: str) -> dict:
    """Return a safe local response for common assistant commands."""
    text = (message or "").strip()
    lowered = text.lower()

    if not text:
        return {"reply": "I didn't hear anything. Please type or say something.", "action": None}

    if any(word in lowered for word in ["hello", "hi jarvis", "hey jarvis", "good morning", "good evening"]):
        return {"reply": "Hello! I'm Jarvis, your virtual assistant. How can I help you today?", "action": None}

    if "time" in lowered:
        return {"reply": f"The current server time is {datetime.now().strftime('%I:%M %p')}.", "action": None}

    if "date" in lowered or "day is it" in lowered:
        return {"reply": f"Today is {datetime.now().strftime('%A, %d %B %Y')}.", "action": None}

    if any(word in lowered for word in ["your name", "who are you", "introduce yourself"]):
        return {"reply": "I'm Jarvis, a browser-based virtual assistant built with Python, Flask, HTML, CSS, and JavaScript.", "action": None}

    if "help" in lowered or "what can you do" in lowered or "commands" in lowered:
        return {
            "reply": "You can ask me for the date or time, say hello, ask who I am, request a simple calculation, or ask me to open a website.",
            "action": None
        }

    # Simple arithmetic only; no eval() is used.
    match = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*([+*/-])\s*(-?\d+(?:\.\d+)?)\s*", text)
    if match:
        left, operator, right = match.groups()
        a, b = float(left), float(right)
        try:
            result = {"+": lambda: a + b, "-": lambda: a - b,
                      "*": lambda: a * b, "/": lambda: a / b}[operator]()
            if not result.is_integer():
                rendered = f"{result:.6g}"
            else:
                rendered = str(int(result))
            return {"reply": f"The answer is {rendered}.", "action": None}
        except ZeroDivisionError:
            return {"reply": "You can't divide by zero.", "action": None}

    site_map = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "gmail": "https://mail.google.com",
        "wikipedia": "https://www.wikipedia.org",
    }
    for site, url in site_map.items():
        if f"open {site}" in lowered:
            return {"reply": f"Opening {site.title()} in a new tab.", "action": {"type": "open_url", "url": url}}

    if "joke" in lowered:
        return {"reply": "Why do programmers prefer dark mode? Because light attracts bugs!", "action": None}

    return {
        "reply": "I'm still learning that skill. Try asking for the time, date, a calculation like 12 * 8, or say 'help' to see commands.",
        "action": None
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "")
    if not isinstance(message, str):
        return jsonify({"error": "Message must be text."}), 400
    if len(message) > 500:
        return jsonify({"error": "Please keep messages under 500 characters."}), 400
    return jsonify(get_reply(message))


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "app": "Jarvis Virtual Assistant"})


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host="127.0.0.1", port=5000)
