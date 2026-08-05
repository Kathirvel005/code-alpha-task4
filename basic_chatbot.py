"""
basic_chatbot.py - Entry point for the Chatbot application.
Powered by the upgraded AdvancedChatbot engine with NLP, Memory, Dynamic Tools & Rich CLI.
"""

import sys

# Ensure UTF-8 output encoding for emoji and symbol support across all terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from advanced_chatbot import AdvancedChatbot

def chatbot():
    """Main execution function for the chatbot."""
    bot = AdvancedChatbot(bot_name="Nova")
    bot.run_cli()

if __name__ == "__main__":
    chatbot()
