"""
memory.py - Session Memory, User State Tracking & Analytics.
Handles short-term conversational context, persistent user attributes (e.g. name),
turn history logs, conversation statistics, and export to JSON / Markdown.
"""

import json
import datetime
from typing import Dict, Any, List, Optional

class MemoryManager:
    """Manages multi-turn conversation state, user persona, and session analytics."""

    def __init__(self):
        self.session_id = datetime.datetime.now().strftime("session_%Y%m%d_%H%M%S")
        self.start_time = datetime.datetime.now()
        self.history: List[Dict[str, Any]] = []
        self.user_profile: Dict[str, Any] = {
            "name": None,
            "interests": [],
            "custom_attributes": {}
        }
        self.intent_counter: Dict[str, int] = {}
        self.sentiment_history: List[str] = []

    def set_user_name(self, name: str):
        """Store or update user's preferred name."""
        self.user_profile["name"] = name.strip().title()

    def get_user_name(self) -> Optional[str]:
        """Retrieve stored user's name if known."""
        return self.user_profile.get("name")

    def record_turn(
        self,
        user_input: str,
        bot_response: str,
        intent: str,
        confidence: float,
        sentiment: str,
        sentiment_score: float
    ):
        """Log a complete conversation turn with analytical metadata."""
        turn_data = {
            "turn_index": len(self.history) + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "time_display": datetime.datetime.now().strftime("%H:%M:%S"),
            "user_input": user_input,
            "bot_response": bot_response,
            "intent": intent,
            "confidence": confidence,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score
        }
        self.history.append(turn_data)

        # Update stats
        self.intent_counter[intent] = self.intent_counter.get(intent, 0) + 1
        self.sentiment_history.append(sentiment)

    def get_last_turn(self) -> Optional[Dict[str, Any]]:
        """Retrieve the most recent conversation turn."""
        if self.history:
            return self.history[-1]
        return None

    def get_recent_context(self, n: int = 5) -> List[Dict[str, Any]]:
        """Retrieve the last N turns for short-term contextual reasoning."""
        return self.history[-n:]

    def get_stats(self) -> Dict[str, Any]:
        """Generate comprehensive analytics for the current session."""
        now = datetime.datetime.now()
        duration_seconds = int((now - self.start_time).total_seconds())
        total_turns = len(self.history)

        pos = self.sentiment_history.count("positive")
        neu = self.sentiment_history.count("neutral")
        neg = self.sentiment_history.count("negative")

        # Most frequent intents
        sorted_intents = sorted(self.intent_counter.items(), key=lambda x: x[1], reverse=True)

        return {
            "session_id": self.session_id,
            "started_at": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": duration_seconds,
            "duration_formatted": f"{duration_seconds // 60}m {duration_seconds % 60}s",
            "total_turns": total_turns,
            "user_name": self.user_profile.get("name") or "Anonymous",
            "sentiment_distribution": {
                "positive": pos,
                "neutral": neu,
                "negative": neg
            },
            "top_intents": sorted_intents[:5]
        }

    def clear(self):
        """Reset conversation history while maintaining session start timestamp."""
        self.history.clear()
        self.sentiment_history.clear()
        self.intent_counter.clear()

    def export_to_json(self, filepath: str) -> str:
        """Export full conversation logs and metrics to a JSON file."""
        data = {
            "session_id": self.session_id,
            "user_profile": self.user_profile,
            "stats": self.get_stats(),
            "history": self.history
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def export_to_markdown(self, filepath: str) -> str:
        """Export conversation transcript formatted in Markdown."""
        stats = self.get_stats()
        lines = [
            f"# Chatbot Conversation Transcript",
            f"- **Session ID**: `{self.session_id}`",
            f"- **User**: {stats['user_name']}",
            f"- **Start Time**: {stats['started_at']}",
            f"- **Duration**: {stats['duration_formatted']}",
            f"- **Total Turns**: {stats['total_turns']}",
            f"",
            f"---",
            f"",
            f"## Conversation Log",
            f""
        ]

        for turn in self.history:
            lines.append(f"### Turn #{turn['turn_index']} [{turn['time_display']}]")
            lines.append(f"- **User**: {turn['user_input']}")
            lines.append(f"- **Bot**: {turn['bot_response']}")
            lines.append(f"- *Metadata: Intent `{turn['intent']}` (conf: {turn['confidence']}), Sentiment `{turn['sentiment']}`*")
            lines.append("")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return filepath
