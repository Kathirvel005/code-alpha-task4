"""
test_chatbot.py - Comprehensive Unit Test Suite for Advanced AI Chatbot.
Tests NLP Intent Classification, Fuzzy Matching, Entity Extraction,
Math Engine, Unit Conversions, Memory Management, and End-to-End Orchestration.
"""

import unittest
import os
import json
from nlp_engine import NLPEngine
from tools import MathTool, DateTimeTool, UnitConverterTool, TriviaJokeTool
from memory import MemoryManager
from advanced_chatbot import AdvancedChatbot


class TestNLPEngine(unittest.TestCase):
    def setUp(self):
        self.nlp = NLPEngine()

    def test_clean_text(self):
        self.assertEqual(self.nlp.clean_text("  hello   world!  "), "hello world!")
        self.assertEqual(self.nlp.clean_text(""), "")

    def test_intent_classification_exact(self):
        res = self.nlp.classify_intent("hello")
        self.assertEqual(res["intent"], "greeting")

        res_bye = self.nlp.classify_intent("bye")
        self.assertEqual(res_bye["intent"], "farewell")

        res_name = self.nlp.classify_intent("what is your name")
        self.assertEqual(res_name["intent"], "ask_bot_name")

    def test_intent_fuzzy_tolerance(self):
        # Typo tolerance
        res = self.nlp.classify_intent("helo")
        self.assertEqual(res["intent"], "greeting")
        self.assertTrue(res["is_fuzzy"])

        res_bye = self.nlp.classify_intent("goodby")
        self.assertEqual(res_bye["intent"], "farewell")

    def test_sentiment_analysis(self):
        pos = self.nlp.analyze_sentiment("This is wonderful and fantastic!")
        self.assertEqual(pos["sentiment"], "positive")
        self.assertGreater(pos["score"], 0)

        neg = self.nlp.analyze_sentiment("I feel terrible, sad, and frustrated.")
        self.assertEqual(neg["sentiment"], "negative")
        self.assertLess(neg["score"], 0)

        neu = self.nlp.analyze_sentiment("The current date is today.")
        self.assertEqual(neu["sentiment"], "neutral")

    def test_extract_name(self):
        self.assertEqual(self.nlp.extract_name("My name is Kathir"), "Kathir")
        self.assertEqual(self.nlp.extract_name("Call me Sarah"), "Sarah")
        self.assertEqual(self.nlp.extract_name("I am David Miller"), "David Miller")

    def test_extract_math_expression(self):
        self.assertEqual(self.nlp.extract_math_expression("calculate 25 * 4"), "25 * 4")
        self.assertEqual(self.nlp.extract_math_expression("what is 10 + 20?"), "10 + 20")
        self.assertEqual(self.nlp.extract_math_expression("50 / 2"), "50 / 2")

    def test_extract_conversion(self):
        res = self.nlp.extract_conversion_query("convert 100 km to miles")
        self.assertIsNotNone(res)
        val, from_u, to_u = res
        self.assertEqual(val, 100.0)
        self.assertEqual(from_u, "km")
        self.assertEqual(to_u, "miles")


class TestMathTool(unittest.TestCase):
    def test_arithmetic(self):
        res = MathTool.evaluate("25 + 75")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 100)

        res = MathTool.evaluate("(10 + 5) * 4")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 60)

    def test_power_and_sqrt(self):
        res = MathTool.evaluate("2^8")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 256)

        res = MathTool.evaluate("sqrt(144)")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 12)

    def test_division_by_zero(self):
        res = MathTool.evaluate("10 / 0")
        self.assertFalse(res["success"])
        self.assertIn("zero", res["error"].lower())


class TestUnitConverterTool(unittest.TestCase):
    def test_length_conversion(self):
        res = UnitConverterTool.convert(1, "km", "meters")
        self.assertTrue(res["success"])
        self.assertIn("1000", res["output"])

    def test_temperature_conversion(self):
        res = UnitConverterTool.convert(100, "C", "F")
        self.assertTrue(res["success"])
        self.assertIn("212", res["output"])

        res2 = UnitConverterTool.convert(32, "F", "C")
        self.assertTrue(res2["success"])
        self.assertIn("0", res2["output"])

    def test_weight_conversion(self):
        res = UnitConverterTool.convert(1, "kg", "lbs")
        self.assertTrue(res["success"])
        self.assertIn("2.2046", res["output"])


class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.mem = MemoryManager()

    def test_user_name_persistence(self):
        self.assertIsNone(self.mem.get_user_name())
        self.mem.set_user_name("Alex")
        self.assertEqual(self.mem.get_user_name(), "Alex")

    def test_record_turns_and_stats(self):
        self.mem.record_turn("hi", "hello", "greeting", 0.95, "positive", 0.5)
        self.mem.record_turn("bye", "goodbye", "farewell", 1.0, "neutral", 0.0)

        stats = self.mem.get_stats()
        self.assertEqual(stats["total_turns"], 2)
        self.assertEqual(stats["sentiment_distribution"]["positive"], 1)
        self.assertEqual(stats["sentiment_distribution"]["neutral"], 1)

    def test_export_json_and_md(self):
        self.mem.record_turn("hello", "hi there", "greeting", 0.95, "positive", 0.5)
        json_path = "test_export.json"
        md_path = "test_export.md"

        try:
            self.mem.export_to_json(json_path)
            self.assertTrue(os.path.exists(json_path))
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertEqual(len(data["history"]), 1)

            self.mem.export_to_markdown(md_path)
            self.assertTrue(os.path.exists(md_path))
        finally:
            if os.path.exists(json_path):
                os.remove(json_path)
            if os.path.exists(md_path):
                os.remove(md_path)


class TestAdvancedChatbotOrchestrator(unittest.TestCase):
    def setUp(self):
        self.bot = AdvancedChatbot(bot_name="Nova")

    def test_conversation_flow_and_name_memory(self):
        # 1. User introduces name
        r1 = self.bot.process_message("My name is Kathir")
        self.assertIn("Kathir", r1["reply"])
        self.assertEqual(self.bot.memory.get_user_name(), "Kathir")

        # 2. User asks what is my name
        r2 = self.bot.process_message("What is my name?")
        self.assertIn("Kathir", r2["reply"])

        # 3. Math calculation
        r3 = self.bot.process_message("calculate (50 * 2) + 15")
        self.assertIn("115", r3["reply"])

        # 4. Commands
        r4 = self.bot.process_message("/stats")
        self.assertIn("Session Statistics", r4["reply"])

        # 5. Farewell
        r5 = self.bot.process_message("bye")
        self.assertTrue(r5["should_exit"])


class TestFlaskWebApp(unittest.TestCase):
    def setUp(self):
        from app import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_index_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nova AI", response.data)

    def test_chat_api(self):
        response = self.client.post("/api/chat", json={"message": "hello"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("reply", data)
        self.assertEqual(data["intent"], "greeting")

    def test_stats_and_history_api(self):
        res_stats = self.client.get("/api/stats")
        self.assertEqual(res_stats.status_code, 200)

        res_hist = self.client.get("/api/history")
        self.assertEqual(res_hist.status_code, 200)

    def test_clear_api(self):
        res = self.client.post("/api/clear")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])


if __name__ == "__main__":
    unittest.main()
