"""
nlp_engine.py - Advanced Natural Language Processing & Intent Engine for Chatbot.
Provides tokenization, intent recognition with fuzzy matching, sentiment analysis,
and entity extraction (names, math, conversions, dates).
"""

import re
import difflib
from typing import Dict, Any, List, Optional, Tuple

class NLPEngine:
    """
    Hybrid NLP Engine combining Regex pattern recognition,
    Fuzzy Sequence Matching for typo tolerance, and Lexicon-based Sentiment Analysis.
    """

    # Lexicon for Rule-based Sentiment Analysis
    POSITIVE_WORDS = {
        "good", "great", "excellent", "awesome", "fantastic", "amazing", "happy",
        "love", "wonderful", "cool", "fine", "best", "brilliant", "super",
        "nice", "glad", "delighted", "perfect", "enjoy", "pleased", "yay", "helpful"
    }

    NEGATIVE_WORDS = {
        "bad", "terrible", "awful", "horrible", "sad", "angry", "hate", "worst",
        "poor", "upset", "unhappy", "annoyed", "frustrated", "depressed",
        "boring", "useless", "stupid", "broken", "pain", "slow", "error", "sucks"
    }

    # Intent definitions with sample canonical phrases and regex patterns
    INTENTS = {
        "greeting": {
            "patterns": [
                r"\b(hello|hi|hey|greetings|howdy|hola|yo|sup|good\s*(morning|afternoon|evening|day))\b"
            ],
            "samples": [
                "hello", "hi", "hey", "hey there", "hello bot", "good morning",
                "good afternoon", "good evening", "greetings", "howdy", "hola", "yo"
            ],
            "responses": [
                "Hello there! How can I assist you today?",
                "Hi! Great to see you. What's on your mind?",
                "Hey! I'm here and ready to help.",
                "Greetings! What can I do for you today?"
            ]
        },
        "farewell": {
            "patterns": [
                r"\b(bye|goodbye|see\s*you|exit|quit|later|cya|take\s*care|farewell|adios)\b"
            ],
            "samples": [
                "bye", "goodbye", "see you", "exit", "quit", "see ya", "talk to you later",
                "bye bye", "cya", "farewell", "catch you later"
            ],
            "responses": [
                "Goodbye! Have a fantastic day ahead!",
                "See you soon! Feel free to return anytime you need help.",
                "Take care! It was a pleasure chatting with you.",
                "Bye! Let me know if you need anything else later."
            ]
        },
        "ask_bot_name": {
            "patterns": [
                r"\b(what\s*(is|'s)\s*your\s*name|who\s*are\s*you|what\s*should\s*i\s*call\s*you|your\s*name)\b"
            ],
            "samples": [
                "what is your name", "who are you", "what's your name",
                "what should i call you", "tell me your name", "do you have a name"
            ],
            "responses": [
                "I am **Nova**, an Advanced AI-powered Python Chatbot created to assist you!",
                "You can call me **Nova**! I'm your intelligent virtual assistant.",
                "I'm **Nova**, an upgraded conversational assistant with NLP, memory, and built-in tools!"
            ]
        },
        "ask_bot_status": {
            "patterns": [
                r"\b(how\s*are\s*you|how\s*('s|is)\s*it\s*going|how\s*do\s*you\s*do|how\s*are\s*things|you\s*doing\s*well)\b"
            ],
            "samples": [
                "how are you", "how's it going", "how are you doing", "how do you do",
                "how are things", "are you doing well", "how are you today"
            ],
            "responses": [
                "I'm operating at 100% efficiency! Thanks for asking. How are you doing?",
                "I'm doing wonderfully! Ready to crunch numbers, answer questions, or tell jokes. How about you?",
                "All systems running smoothly! How's your day going?"
            ]
        },
        "user_status_good": {
            "patterns": [
                r"\b(i\s*('m|am)\s*(good|fine|great|doing\s*well|awesome|happy|wonderful|fantastic)|doing\s*good)\b"
            ],
            "samples": [
                "i am fine", "i'm good", "i am great", "doing well", "im happy", "all good"
            ],
            "responses": [
                "That's wonderful to hear! 😊 What would you like to explore today?",
                "Glad to hear that! Let's make today even more productive.",
                "Awesome! I'm here if you need anything."
            ]
        },
        "user_status_bad": {
            "patterns": [
                r"\b(i\s*('m|am)\s*(bad|sad|tired|upset|stressed|sick|not\s*good|unhappy|down))\b"
            ],
            "samples": [
                "i am sad", "i'm not good", "i feel bad", "i am tired", "feeling down"
            ],
            "responses": [
                "I'm sorry to hear that. 💙 Remember to take a deep breath and take care of yourself. Can I cheer you up with a joke or quote?",
                "Sending positive vibes your way! If you want a distraction, feel free to ask me for a fun fact, joke, or trivia.",
                "Hang in there! Better days are always around the corner."
            ]
        },
        "tell_user_name": {
            "patterns": [
                r"\b(my\s*name\s*is\s+([A-Za-z0-9_-]+)|i\s*am\s+([A-Za-z0-9_-]+)|call\s*me\s+([A-Za-z0-9_-]+))\b"
            ],
            "samples": [
                "my name is Alex", "i am Kathir", "call me Sarah", "my name is David"
            ],
            "responses": [
                "Nice to meet you, {name}! I've stored that in my memory.",
                "Great to know you, {name}! How can I help you today?",
                "Pleasure meeting you, {name}! I'll remember your name."
            ]
        },
        "ask_user_name": {
            "patterns": [
                r"\b(what\s*(is|'s)\s*my\s*name|do\s*you\s*know\s*my\s*name|who\s*am\s*i|remember\s*my\s*name)\b"
            ],
            "samples": [
                "what is my name", "do you know who i am", "what's my name", "who am i", "remember my name"
            ],
            "responses": []  # Handled dynamically using memory
        },
        "gratitude": {
            "patterns": [
                r"\b(thank\s*you|thanks|thx|appreciate\s*it|thank\s*u|ty)\b"
            ],
            "samples": [
                "thank you", "thanks", "thanks a lot", "thank you so much", "thx", "appreciate it"
            ],
            "responses": [
                "You're very welcome! Always happy to help.",
                "Anytime! Let me know if there's anything else you need.",
                "Glad I could help! 😊",
                "No problem at all!"
            ]
        },
        "apology": {
            "patterns": [
                r"\b(sorry|my\s*bad|i\s*apologize|forgive\s*me)\b"
            ],
            "samples": [
                "sorry", "i am sorry", "my bad", "so sorry", "apologies"
            ],
            "responses": [
                "No need to apologize at all! We're all good.",
                "It's completely fine! No worries at all.",
                "All good! How can we proceed?"
            ]
        },
        "compliment": {
            "patterns": [
                r"\b(you\s*are\s*(smart|awesome|cool|great|helpful|the\s*best|amazing|intelligent))\b"
            ],
            "samples": [
                "you are awesome", "you are smart", "you are very helpful", "you're the best", "great job"
            ],
            "responses": [
                "Thank you so much! That means a lot coming from you! ✨",
                "I appreciate the compliment! I strive to be as helpful as possible.",
                "You're awesome too! Thanks for the kind words."
            ]
        },
        "help": {
            "patterns": [
                r"\b(help|what\s*can\s*you\s*do|features|commands|menu|options|how\s*to\s*use)\b"
            ],
            "samples": [
                "help", "what can you do", "commands", "features", "how do I use this", "help menu"
            ],
            "responses": [
                "Here is what I can do for you:\n"
                "• **Conversations**: General chit-chat, greetings, questions & context memory.\n"
                "• **Calculations**: Type `calculate 25 * 4 + 10` or `sqrt(144)`\n"
                "• **Date & Time**: Ask `what time is it` or `current date`\n"
                "• **Unit Conversions**: Ask `convert 100 km to miles` or `30 C to F`\n"
                "• **Fun & Entertainment**: Ask for `joke`, `trivia`, `quote`, or `riddle`\n"
                "• **Commands**: `/help`, `/stats`, `/history`, `/clear`, `/export`, `/quit`"
            ]
        },
        "joke": {
            "patterns": [
                r"\b(tell\s*me\s*a\s*joke|joke|make\s*me\s*laugh|funny\s*joke|another\s*joke)\b"
            ],
            "samples": [
                "tell me a joke", "joke", "make me laugh", "say something funny", "tell a joke"
            ],
            "responses": []  # Handled dynamically by Tools
        },
        "trivia": {
            "patterns": [
                r"\b(trivia|fun\s*fact|interesting\s*fact|tell\s*me\s*a\s*fact|did\s*you\s*know)\b"
            ],
            "samples": [
                "trivia", "fun fact", "tell me a fact", "give me a fact", "interesting fact"
            ],
            "responses": []  # Handled dynamically by Tools
        },
        "quote": {
            "patterns": [
                r"\b(quote|inspire\s*me|inspirational\s*quote|motivate\s*me|motivational\s*quote)\b"
            ],
            "samples": [
                "quote", "inspire me", "motivational quote", "give me a quote", "inspirational quote"
            ],
            "responses": []  # Handled dynamically by Tools
        },
        "riddle": {
            "patterns": [
                r"\b(riddle|tell\s*me\s*a\s*riddle|give\s*me\s*a\s*riddle|brain\s*teaser)\b"
            ],
            "samples": [
                "riddle", "tell me a riddle", "give me a riddle", "brain teaser"
            ],
            "responses": []  # Handled dynamically by Tools
        },
        "datetime": {
            "patterns": [
                r"\b(what\s*time\s*is\s*it|current\s*time|time\s*now|what\s*is\s*today('s|\s*)date|what\s*day\s*is\s*it|current\s*date)\b"
            ],
            "samples": [
                "what time is it", "current time", "what is the date", "what is today's date", "time now", "what day is it"
            ],
            "responses": []  # Handled dynamically by Tools
        },
        "calculate": {
            "patterns": [
                r"\b(calculate|compute|solve|math|what\s*is\s*[\d\(\.\+\-\*\/\^\s]+)\b",
                r"(\d+\s*[\+\-\*\/\^\%]\s*\d+)"
            ],
            "samples": [
                "calculate 25 * 4", "what is 10 + 20", "solve 50 / 2", "compute 2^8", "sqrt(144)"
            ],
            "responses": []  # Handled dynamically by Tools
        },
        "unit_conversion": {
            "patterns": [
                r"\b(convert\s+[\d\.]+\s*[A-Za-z]+\s+to\s+[A-Za-z]+)\b",
                r"\b([\d\.]+\s*(c|f|celsius|fahrenheit|km|miles|kg|lbs|pounds|meters|feet)\s+in\s+[A-Za-z]+)\b"
            ],
            "samples": [
                "convert 100 km to miles", "convert 30 c to f", "convert 5 kg to lbs", "convert 10 meters to feet"
            ],
            "responses": []  # Handled dynamically by Tools
        },
        "creator_info": {
            "patterns": [
                r"\b(who\s*(created|made|built|developed|coded)\s*you|your\s*creator|who\s*is\s*your\s*developer)\b"
            ],
            "samples": [
                "who created you", "who made you", "who is your developer", "who built this chatbot"
            ],
            "responses": [
                "I was created as part of the Code Alpha Advanced AI Chatbot project!",
                "I was built using Python with clean modular NLP, context memory, and custom tools.",
                "I was developed by talented engineers in the Code Alpha AI initiative!"
            ]
        }
    }

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for high-speed matching."""
        self.compiled_patterns = {}
        for intent_name, data in self.INTENTS.items():
            compiled_list = []
            for pattern_str in data.get("patterns", []):
                compiled_list.append(re.compile(pattern_str, re.IGNORECASE))
            self.compiled_patterns[intent_name] = compiled_list

    def clean_text(self, text: str) -> str:
        """Sanitize and normalize raw user input text."""
        if not text:
            return ""
        text = text.strip()
        # Keep alphanumeric, basic math symbols and standard punctuation
        text = re.sub(r"\s+", " ", text)
        return text

    def tokenize(self, text: str) -> List[str]:
        """Split text into lowercase alphanumeric word tokens."""
        clean = re.sub(r"[^\w\s]", "", text.lower())
        return [tok for tok in clean.split() if tok]

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Evaluate sentiment polarity using rule-based lexical analysis.
        Returns sentiment label, score (-1.0 to 1.0), and word counts.
        """
        tokens = self.tokenize(text)
        if not tokens:
            return {"sentiment": "neutral", "score": 0.0, "positive_count": 0, "negative_count": 0}

        pos_count = sum(1 for tok in tokens if tok in self.POSITIVE_WORDS)
        neg_count = sum(1 for tok in tokens if tok in self.NEGATIVE_WORDS)

        diff = pos_count - neg_count
        total_matched = pos_count + neg_count

        if total_matched == 0:
            score = 0.0
            sentiment = "neutral"
        else:
            score = max(-1.0, min(1.0, diff / (total_matched + 1e-5)))
            if diff > 0:
                sentiment = "positive"
            elif diff < 0:
                sentiment = "negative"
            else:
                sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "positive_count": pos_count,
            "negative_count": neg_count
        }

    def extract_name(self, text: str) -> Optional[str]:
        """Extract a person's name from introduction sentences."""
        patterns = [
            r"\b(?:my\s*name\s*is|i\s*am\s+called|call\s*me|i\s*am|i'm)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)\b"
        ]
        stopwords = {
            "fine", "good", "happy", "here", "sad", "user", "human", "sorry",
            "great", "ok", "okay", "bye", "goodbye", "hello", "hi", "hey",
            "tired", "back", "doing", "well", "ready", "new", "sure", "wondering",
            "asking", "just", "not", "also", "a", "an", "the", "so", "very",
            "feeling", "looking", "trying", "going", "available"
        }
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                words = candidate.lower().split()
                # If first word or entire candidate is a stopword, reject
                if any(w in stopwords for w in words):
                    continue
                if len(candidate) > 1:
                    return candidate.title()
        return None

    def extract_math_expression(self, text: str) -> Optional[str]:
        """Extract mathematical expression from query."""
        # 1. Explicit calculate keyword
        calc_match = re.search(r"(?:calculate|compute|solve|eval|evaluate|what\s+is)\s+([0-9\.\+\-\*\/\^\%\(\)\s\w]+)", text, re.IGNORECASE)
        if calc_match:
            expr = calc_match.group(1).strip()
            # Clean trailing punctuation like '?'
            expr = expr.rstrip("?").strip()
            if any(char.isdigit() for char in expr):
                return expr

        # 2. Standalone math expression containing operators and numbers
        if re.search(r"^\s*[\d\(\.\s]+[\+\-\*\/\^\%][\d\(\)\.\+\-\*\/\^\%\s\w]+\s*\??$", text):
            expr = text.strip().rstrip("?").strip()
            return expr

        return None

    def extract_conversion_query(self, text: str) -> Optional[Tuple[float, str, str]]:
        """
        Extract numeric value, source unit, and target unit.
        Example: 'convert 100 km to miles' -> (100.0, 'km', 'miles')
        """
        pattern = r"(?:convert\s+)?([0-9\.]+)\s*([A-Za-z°]+)\s+(?:to|in|into)\s+([A-Za-z°]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
                from_u = match.group(2).lower().replace("°", "")
                to_u = match.group(3).lower().replace("°", "")
                return value, from_u, to_u
            except ValueError:
                return None
        return None

    def classify_intent(self, text: str) -> Dict[str, Any]:
        """
        Classify user input into an intent using Regex matching and Fuzzy Similarity fallback.
        Returns: {
            'intent': str,
            'confidence': float,
            'matched_pattern': Optional[str],
            'is_fuzzy': bool
        }
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return {"intent": "empty", "confidence": 1.0, "matched_pattern": None, "is_fuzzy": False}

        # 1. Check for command prefixes (e.g. /help, /clear, /stats, /export)
        if cleaned.startswith("/"):
            cmd = cleaned[1:].lower().split()[0]
            if cmd in ["help", "clear", "stats", "history", "export", "quit", "exit", "reset"]:
                return {"intent": f"cmd_{cmd}", "confidence": 1.0, "matched_pattern": f"/{cmd}", "is_fuzzy": False}

        # 2. Check Regex Patterns (High Priority / Precision)
        for intent_name, patterns in self.compiled_patterns.items():
            for p in patterns:
                match = p.search(cleaned)
                if match:
                    return {
                        "intent": intent_name,
                        "confidence": 0.95,
                        "matched_pattern": p.pattern,
                        "is_fuzzy": False
                    }

        # 3. Fuzzy Matching against Sample Sentences (Typo & Paraphrase Tolerance)
        best_intent = "unknown"
        best_ratio = 0.0

        for intent_name, data in self.INTENTS.items():
            samples = data.get("samples", [])
            for sample in samples:
                # Direct string similarity
                ratio = difflib.SequenceMatcher(None, cleaned.lower(), sample.lower()).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_intent = intent_name

        # Confidence threshold for fuzzy matching
        if best_ratio >= 0.65:
            return {
                "intent": best_intent,
                "confidence": round(best_ratio, 2),
                "matched_pattern": "fuzzy_sample_match",
                "is_fuzzy": True
            }

        return {
            "intent": "unknown",
            "confidence": round(best_ratio, 2),
            "matched_pattern": None,
            "is_fuzzy": False
        }
