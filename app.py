"""
app.py - Flask Web Application and REST API for the Advanced Chatbot.
Provides a modern web UI, real-time message streaming, conversation state endpoints,
and statistics monitoring.
"""

import sys
import os

# Ensure UTF-8 output encoding across all operating systems
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from flask import Flask, render_template, request, jsonify, send_file
from advanced_chatbot import AdvancedChatbot

app = Flask(__name__)
# Initialize the stateful Chatbot engine
bot = AdvancedChatbot(bot_name="Nova")

@app.route("/")
def index():
    """Render the primary Web Chat Interface."""
    return render_template("index.html", bot_name=bot.bot_name)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Handle chat message submissions.
    Payload: { "message": "hello" }
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "error": "Empty message provided.",
            "reply": "Please enter a message!",
            "intent": "empty",
            "confidence": 1.0,
            "sentiment": "neutral"
        }), 400

    result = bot.process_message(message)
    stats = bot.memory.get_stats()
    user_name = bot.memory.get_user_name()

    return jsonify({
        "reply": result["reply"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "sentiment": result["sentiment"],
        "sentiment_score": result["sentiment_score"],
        "should_exit": result.get("should_exit", False),
        "user_name": user_name,
        "stats": stats
    })

@app.route("/api/history", methods=["GET"])
def api_history():
    """Retrieve the full conversation turn history."""
    return jsonify({
        "history": bot.memory.history,
        "stats": bot.memory.get_stats()
    })

@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Retrieve session analytical metrics."""
    return jsonify(bot.memory.get_stats())

@app.route("/api/clear", methods=["POST"])
def api_clear():
    """Reset current conversation memory and context."""
    bot.memory.clear()
    return jsonify({
        "success": True,
        "message": "Conversation history cleared successfully."
    })

@app.route("/api/export/<fmt>", methods=["GET"])
def api_export(fmt):
    """Download conversation export file (json or markdown)."""
    fmt = fmt.lower()
    if fmt not in ("json", "md", "markdown"):
        fmt = "md"

    export_filename = f"chat_export_{bot.memory.session_id}.{ 'json' if fmt == 'json' else 'md' }"
    export_path = os.path.join(os.path.dirname(__file__), export_filename)

    if fmt == "json":
        bot.memory.export_to_json(export_path)
        mimetype = "application/json"
    else:
        bot.memory.export_to_markdown(export_path)
        mimetype = "text/markdown"

    return send_file(export_path, as_attachment=True, download_name=export_filename, mimetype=mimetype)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Nova AI Chatbot Web Server on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
