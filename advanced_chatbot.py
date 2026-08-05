"""
advanced_chatbot.py - Core Orchestrator for Advanced Multi-Modal AI Chatbot.
Integrates NLP classification, memory tracking, dynamic tools, and a rich CLI.
"""

import sys
import os
import random
from typing import Dict, Any, Optional

# Ensure UTF-8 output encoding across all operating systems and terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from nlp_engine import NLPEngine
from memory import MemoryManager
from tools import MathTool, DateTimeTool, UnitConverterTool, TriviaJokeTool

# Optional ANSI / Colorama Styling
try:
    import colorama
    colorama.init(autoreset=True)
    CYAN = colorama.Fore.CYAN
    GREEN = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    MAGENTA = colorama.Fore.MAGENTA
    RED = colorama.Fore.RED
    BLUE = colorama.Fore.BLUE
    WHITE = colorama.Fore.WHITE
    BRIGHT = colorama.Style.BRIGHT
    RESET = colorama.Style.RESET_ALL
except ImportError:
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    WHITE = "\033[37m"
    BRIGHT = "\033[1m"
    RESET = "\033[0m"


class AdvancedChatbot:
    """
    Advanced AI Chatbot with stateful memory, fuzzy NLP intent recognition,
    AST-based math computation, unit conversions, and session reporting.
    """

    def __init__(self, bot_name: str = "Nova"):
        self.bot_name = bot_name
        self.nlp = NLPEngine()
        self.memory = MemoryManager()

    def process_message(self, raw_input: str) -> Dict[str, Any]:
        """
        Process a user input string and return a structured dictionary containing
        the bot reply, detected intent, confidence score, sentiment, and flags.
        """
        cleaned = self.nlp.clean_text(raw_input)
        if not cleaned:
            return {
                "reply": "It looks like you sent an empty message! How can I help you? (Type /help for options)",
                "intent": "empty",
                "confidence": 1.0,
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "should_exit": False
            }

        # 1. Analyze Sentiment
        sentiment_data = self.nlp.analyze_sentiment(cleaned)
        sentiment = sentiment_data["sentiment"]
        sentiment_score = sentiment_data["score"]

        # 2. Check Interactive Slash Commands
        if cleaned.startswith("/"):
            parts = cleaned[1:].split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ("help", "commands"):
                reply = (
                    f"✨ **{self.bot_name} Chatbot Commands & Features** ✨\n\n"
                    "• `/help` - Show this comprehensive feature guide\n"
                    "• `/stats` - View session analytics and sentiment statistics\n"
                    "• `/history` - Display recent conversation turns\n"
                    "• `/clear` - Reset current conversation context and memory\n"
                    "• `/export [json|md]` - Export conversation log to file\n"
                    "• `/quit` or `/exit` - End the chat session\n\n"
                    "💡 **Natural Capabilities**:\n"
                    "• **Math**: `calculate (45 * 2) + sqrt(144)`\n"
                    "• **Conversions**: `convert 100 km to miles`, `30 C to F`\n"
                    "• **Date & Time**: `what time is it`, `today's date`\n"
                    "• **Memory**: `My name is Alex`, `What is my name?`\n"
                    "• **Fun**: `tell me a joke`, `trivia`, `quote`, `riddle`"
                )
                return self._build_result(raw_input, reply, f"cmd_{cmd}", 1.0, sentiment, sentiment_score)

            elif cmd == "stats":
                stats = self.memory.get_stats()
                pos = stats["sentiment_distribution"]["positive"]
                neu = stats["sentiment_distribution"]["neutral"]
                neg = stats["sentiment_distribution"]["negative"]
                reply = (
                    f"📊 **Session Statistics [{stats['session_id']}]**\n\n"
                    f"• **User**: {stats['user_name']}\n"
                    f"• **Active Duration**: {stats['duration_formatted']}\n"
                    f"• **Total Turns**: {stats['total_turns']}\n"
                    f"• **Sentiment Breakdown**: 😊 Positive: {pos} | 😐 Neutral: {neu} | 🙁 Negative: {neg}"
                )
                return self._build_result(raw_input, reply, "cmd_stats", 1.0, sentiment, sentiment_score)

            elif cmd == "history":
                recent = self.memory.get_recent_context(10)
                if not recent:
                    reply = "📜 No conversation history in this session yet."
                else:
                    lines = ["📜 **Recent Conversation History:**"]
                    for t in recent:
                        lines.append(f"• **You**: {t['user_input']}")
                        lines.append(f"  **{self.bot_name}**: {t['bot_response']}")
                    reply = "\n".join(lines)
                return self._build_result(raw_input, reply, "cmd_history", 1.0, sentiment, sentiment_score)

            elif cmd in ("clear", "reset"):
                self.memory.clear()
                reply = "🧹 Conversation history and context have been cleared!"
                return self._build_result(raw_input, reply, "cmd_clear", 1.0, sentiment, sentiment_score)

            elif cmd == "export":
                fmt = arg.lower() if arg in ("json", "md", "markdown") else "md"
                filename = f"chat_export_{self.memory.session_id}.{ 'json' if fmt == 'json' else 'md' }"
                if fmt == "json":
                    self.memory.export_to_json(filename)
                else:
                    self.memory.export_to_markdown(filename)
                reply = f"💾 Chat transcript successfully saved to `{filename}`!"
                return self._build_result(raw_input, reply, "cmd_export", 1.0, sentiment, sentiment_score)

            elif cmd in ("quit", "exit", "bye"):
                user_name = self.memory.get_user_name()
                farewell = f"Goodbye {user_name}! Have a wonderful day!" if user_name else "Goodbye! Have a great day!"
                return {
                    "reply": farewell,
                    "intent": "farewell",
                    "confidence": 1.0,
                    "sentiment": sentiment,
                    "sentiment_score": sentiment_score,
                    "should_exit": True
                }

        # 3. Check for Entity Introductions (e.g. "my name is Alex")
        name_candidate = self.nlp.extract_name(cleaned)
        if name_candidate:
            self.memory.set_user_name(name_candidate)
            reply = f"Nice to meet you, **{name_candidate}**! I'll remember that for the rest of our chat. 😊"
            return self._build_result(raw_input, reply, "tell_user_name", 0.98, sentiment, sentiment_score)

        # 4. Check for Unit Conversions (e.g. "convert 100 km to miles")
        conv_query = self.nlp.extract_conversion_query(cleaned)
        if conv_query:
            val, from_u, to_u = conv_query
            res = UnitConverterTool.convert(val, from_u, to_u)
            return self._build_result(raw_input, res["output"], "unit_conversion", 0.95, sentiment, sentiment_score)

        # 5. Check for Math Calculations (e.g. "calculate 25 * 4", "sqrt(144)")
        math_expr = self.nlp.extract_math_expression(cleaned)
        if math_expr:
            res = MathTool.evaluate(math_expr)
            if res["success"]:
                return self._build_result(raw_input, res["output"], "calculate", 0.95, sentiment, sentiment_score)

        # 6. Intent Classification (Regex + Fuzzy Fallback)
        classification = self.nlp.classify_intent(cleaned)
        intent = classification["intent"]
        confidence = classification["confidence"]

        # 7. Route based on Intent
        if intent == "farewell":
            user_name = self.memory.get_user_name()
            farewell = f"Goodbye {user_name}! It was wonderful talking with you." if user_name else "Goodbye! Have a wonderful day ahead!"
            self.memory.record_turn(raw_input, farewell, "farewell", confidence, sentiment, sentiment_score)
            return {
                "reply": farewell,
                "intent": "farewell",
                "confidence": confidence,
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "should_exit": True
            }

        elif intent == "ask_user_name":
            stored_name = self.memory.get_user_name()
            if stored_name:
                reply = f"Your name is **{stored_name}**! I have it saved in my memory. 😊"
            else:
                reply = "I don't know your name yet! You can tell me by saying *'My name is [your name]'*."
            return self._build_result(raw_input, reply, intent, confidence, sentiment, sentiment_score)

        elif intent == "datetime":
            reply = DateTimeTool.get_current_info()
            return self._build_result(raw_input, reply, intent, confidence, sentiment, sentiment_score)

        elif intent == "joke":
            reply = TriviaJokeTool.get_joke()
            return self._build_result(raw_input, reply, intent, confidence, sentiment, sentiment_score)

        elif intent == "trivia":
            reply = TriviaJokeTool.get_trivia()
            return self._build_result(raw_input, reply, intent, confidence, sentiment, sentiment_score)

        elif intent == "quote":
            reply = TriviaJokeTool.get_quote()
            return self._build_result(raw_input, reply, intent, confidence, sentiment, sentiment_score)

        elif intent == "riddle":
            reply = TriviaJokeTool.get_riddle()
            return self._build_result(raw_input, reply, intent, confidence, sentiment, sentiment_score)

        elif intent in self.nlp.INTENTS and self.nlp.INTENTS[intent]["responses"]:
            responses = self.nlp.INTENTS[intent]["responses"]
            reply = random.choice(responses)
            user_name = self.memory.get_user_name() or "there"
            reply = reply.replace("{name}", user_name)
            return self._build_result(raw_input, reply, intent, confidence, sentiment, sentiment_score)

        # 8. Fallback for Unrecognized Inputs
        fallback_replies = [
            f"I'm not quite sure I understood that. 🤔\n"
            f"You can try asking me to calculate something (`calculate 25 * 4`), check the time, convert units (`100 km to miles`), tell a joke, or type `/help` for all features!",
            f"I didn't catch that. Could you rephrase it? Type `/help` to see what I can do.",
            f"Hmm, that's beyond my current rules. Feel free to ask a math question, request a fun fact, or check `/commands`."
        ]
        reply = random.choice(fallback_replies)
        return self._build_result(raw_input, reply, "unknown", confidence, sentiment, sentiment_score)

    def _build_result(
        self,
        user_input: str,
        reply: str,
        intent: str,
        confidence: float,
        sentiment: str,
        sentiment_score: float
    ) -> Dict[str, Any]:
        """Record turn in memory and return structured response."""
        self.memory.record_turn(user_input, reply, intent, confidence, sentiment, sentiment_score)
        return {
            "reply": reply,
            "intent": intent,
            "confidence": confidence,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "should_exit": False
        }

    def print_banner(self):
        """Display styled welcome banner for terminal session."""
        print(f"\n{CYAN}{BRIGHT}{'='*60}{RESET}")
        print(f"{GREEN}{BRIGHT}       🤖  {self.bot_name.upper()} ADVANCED AI CHATBOT  🤖       {RESET}")
        print(f"{CYAN}{BRIGHT}{'='*60}{RESET}")
        print(f"{WHITE}• Type your message or questions naturally.")
        print(f"• Try: {YELLOW}calculate 25 * 4{WHITE}, {YELLOW}what time is it{WHITE}, {YELLOW}joke{WHITE}, {YELLOW}convert 100 km to miles{WHITE}")
        print(f"• Special commands: {MAGENTA}/help{WHITE}, {MAGENTA}/stats{WHITE}, {MAGENTA}/history{WHITE}, {MAGENTA}/clear{WHITE}, {MAGENTA}/export{WHITE}")
        print(f"• Type {RED}'bye'{WHITE} or {RED}'/quit'{WHITE} to exit.")
        print(f"{CYAN}{BRIGHT}{'='*60}{RESET}\n")

    def run_cli(self):
        """Interactive Terminal Loop with color formatting and robust error handling."""
        self.print_banner()

        while True:
            try:
                user_name = self.memory.get_user_name()
                prompt_label = f"You ({user_name})" if user_name else "You"
                sys.stdout.write(f"{GREEN}{BRIGHT}{prompt_label}:{RESET} ")
                sys.stdout.flush()

                user_input = sys.stdin.readline()
                if not user_input:  # EOF reached
                    print(f"\n{CYAN}🤖 {self.bot_name}:{RESET} Goodbye! Have a great day!")
                    break

                user_input = user_input.strip()
                if not user_input:
                    continue

                res = self.process_message(user_input)

                # Sentiment indicator badge
                sent_emoji = "😊" if res["sentiment"] == "positive" else ("🙁" if res["sentiment"] == "negative" else "😐")
                intent_badge = f"{BLUE}[{res['intent']} | {sent_emoji}]{RESET}"

                # Print bot response
                print(f"{CYAN}{BRIGHT}🤖 {self.bot_name} {intent_badge}:{RESET} {res['reply']}\n")

                if res.get("should_exit", False):
                    break

            except KeyboardInterrupt:
                print(f"\n\n{YELLOW}Session interrupted by user. Goodbye!{RESET}")
                break
            except Exception as e:
                print(f"\n{RED}⚠️ Error processing input: {str(e)}{RESET}\n")


if __name__ == "__main__":
    bot = AdvancedChatbot(bot_name="Nova")
    bot.run_cli()
