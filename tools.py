"""
tools.py - Dynamic built-in tools for Chatbot.
Provides safe AST-based mathematical evaluation, live datetime information,
comprehensive unit conversions, and curated jokes, trivia, quotes, and riddles.
"""

import ast
import math
import random
import datetime
from typing import Dict, Any, Tuple, Optional

class MathTool:
    """Safe AST-based arithmetic and scientific expression evaluator."""

    # Allowed binary operators
    ALLOWED_OPERATORS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a ** b,
        ast.BitXor: lambda a, b: a ** b,  # Handle ^ as power in casual math
    }

    # Allowed unary operators
    ALLOWED_UNARY = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a,
    }

    # Allowed math functions and constants
    ALLOWED_FUNCTIONS = {
        "sqrt": math.sqrt,
        "abs": abs,
        "round": round,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "ceil": math.ceil,
        "floor": math.floor,
        "factorial": math.factorial,
        "rad": math.radians,
        "deg": math.degrees,
    }

    ALLOWED_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    @classmethod
    def _eval_node(cls, node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return cls._eval_node(node.body)
        elif isinstance(node, ast.Constant):  # Python 3.8+ numeric/constant literals
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Unsupported constant type: {type(node.value)}")
        elif isinstance(node, ast.Name):
            name_lower = node.id.lower()
            if name_lower in cls.ALLOWED_CONSTANTS:
                return float(cls.ALLOWED_CONSTANTS[name_lower])
            raise ValueError(f"Unknown variable or constant: '{node.id}'")
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in cls.ALLOWED_OPERATORS:
                left = cls._eval_node(node.left)
                right = cls._eval_node(node.right)
                if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                    raise ZeroDivisionError("Division by zero is undefined.")
                if op_type in (ast.Pow, ast.BitXor) and (left > 1000 or right > 100):
                    raise OverflowError("Exponent values too large to compute safely.")
                return cls.ALLOWED_OPERATORS[op_type](left, right)
            raise ValueError(f"Operator {op_type.__name__} is not allowed.")
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in cls.ALLOWED_UNARY:
                operand = cls._eval_node(node.operand)
                return cls.ALLOWED_UNARY[op_type](operand)
            raise ValueError(f"Unary operator {op_type.__name__} is not allowed.")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id.lower()
                if func_name in cls.ALLOWED_FUNCTIONS:
                    args = [cls._eval_node(arg) for arg in node.args]
                    return float(cls.ALLOWED_FUNCTIONS[func_name](*args))
                raise ValueError(f"Function '{node.func.id}' is not supported.")
            raise ValueError("Unsupported call format.")
        else:
            raise ValueError(f"Expression type '{type(node).__name__}' is not allowed.")

    @classmethod
    def evaluate(cls, expression_str: str) -> Dict[str, Any]:
        """Safely parse and evaluate math expression string."""
        clean_expr = expression_str.strip().replace("x", "*").replace("X", "*")
        try:
            parsed = ast.parse(clean_expr, mode="eval")
            result = cls._eval_node(parsed)
            # Format integer outputs neatly (e.g. 50.0 -> 50)
            if result.is_integer():
                formatted_result = int(result)
            else:
                formatted_result = round(result, 6)
            return {
                "success": True,
                "expression": clean_expr,
                "result": formatted_result,
                "output": f"🧮 Result: **{clean_expr} = {formatted_result}**"
            }
        except ZeroDivisionError:
            return {"success": False, "error": "Error: Cannot divide by zero.", "output": "⚠️ Math Error: Division by zero is undefined."}
        except OverflowError as e:
            return {"success": False, "error": str(e), "output": f"⚠️ Math Error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e), "output": f"⚠️ Math Error: Could not compute '{expression_str}' ({str(e)})."}


class DateTimeTool:
    """Provides current time, date, day of the week, and calendar info."""

    @classmethod
    def get_current_info(cls) -> str:
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%A, %B %d, %Y")
        iso_str = now.strftime("%Y-%m-%d")
        day_of_year = now.strftime("%j")
        week_num = now.strftime("%U")
        
        return (
            f"🕒 Current Time: **{time_str}**\n"
            f"📅 Today's Date: **{date_str}**\n"
            f"📊 Week: **{week_num}** | Day of year: **{day_of_year}** (ISO: `{iso_str}`)"
        )

    @classmethod
    def get_time_only(cls) -> str:
        now = datetime.datetime.now()
        return f"🕒 The current time is **{now.strftime('%I:%M:%S %p')}**."

    @classmethod
    def get_date_only(cls) -> str:
        now = datetime.datetime.now()
        return f"📅 Today is **{now.strftime('%A, %B %d, %Y')}**."


class UnitConverterTool:
    """Converts temperature, distance, weight, and digital storage units."""

    LENGTH_FACTORS = {
        "m": 1.0, "meter": 1.0, "meters": 1.0,
        "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0,
        "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
        "mm": 0.001, "millimeter": 0.001, "millimeters": 0.001,
        "mi": 1609.344, "mile": 1609.344, "miles": 1609.344,
        "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
        "in": 0.0254, "inch": 0.0254, "inches": 0.0254,
        "yd": 0.9144, "yard": 0.9144, "yards": 0.9144
    }

    WEIGHT_FACTORS = {
        "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0,
        "g": 0.001, "gram": 0.001, "grams": 0.001,
        "mg": 0.000001, "milligram": 0.000001,
        "lb": 0.45359237, "lbs": 0.45359237, "pound": 0.45359237, "pounds": 0.45359237,
        "oz": 0.0283495, "ounce": 0.0283495, "ounces": 0.0283495,
        "ton": 1000.0, "tonne": 1000.0
    }

    STORAGE_FACTORS = {
        "b": 1, "byte": 1, "bytes": 1,
        "kb": 1024, "kilobyte": 1024, "kilobytes": 1024,
        "mb": 1024**2, "megabyte": 1024**2, "megabytes": 1024**2,
        "gb": 1024**3, "gigabyte": 1024**3, "gigabytes": 1024**3,
        "tb": 1024**4, "terabyte": 1024**4, "terabytes": 1024**4,
    }

    @classmethod
    def convert(cls, val: float, from_u: str, to_u: str) -> Dict[str, Any]:
        f = from_u.lower().strip()
        t = to_u.lower().strip()

        # 1. Temperature conversions
        temp_units = {"c", "celsius", "f", "fahrenheit", "k", "kelvin"}
        if f in temp_units and t in temp_units:
            # Normalize to Celsius first
            if f in ("c", "celsius"):
                c_val = val
            elif f in ("f", "fahrenheit"):
                c_val = (val - 32) * 5 / 9
            else:  # Kelvin
                c_val = val - 273.15

            # Convert from Celsius to target
            if t in ("c", "celsius"):
                res = c_val
                target_sym = "°C"
            elif t in ("f", "fahrenheit"):
                res = (c_val * 9 / 5) + 32
                target_sym = "°F"
            else:
                res = c_val + 273.15
                target_sym = "K"

            return {
                "success": True,
                "output": f"🔄 **{val} {from_u.upper()} = {round(res, 2)} {target_sym}**"
            }

        # 2. Length conversions
        if f in cls.LENGTH_FACTORS and t in cls.LENGTH_FACTORS:
            meters = val * cls.LENGTH_FACTORS[f]
            res = meters / cls.LENGTH_FACTORS[t]
            return {
                "success": True,
                "output": f"📏 **{val} {from_u} = {round(res, 4)} {to_u}**"
            }

        # 3. Weight conversions
        if f in cls.WEIGHT_FACTORS and t in cls.WEIGHT_FACTORS:
            kg = val * cls.WEIGHT_FACTORS[f]
            res = kg / cls.WEIGHT_FACTORS[t]
            return {
                "success": True,
                "output": f"⚖️ **{val} {from_u} = {round(res, 4)} {to_u}**"
            }

        # 4. Storage conversions
        if f in cls.STORAGE_FACTORS and t in cls.STORAGE_FACTORS:
            bytes_val = val * cls.STORAGE_FACTORS[f]
            res = bytes_val / cls.STORAGE_FACTORS[t]
            return {
                "success": True,
                "output": f"💾 **{val} {from_u} = {round(res, 4)} {to_u}**"
            }

        return {
            "success": False,
            "output": f"⚠️ Sorry, I don't know how to convert between `{from_u}` and `{to_u}`."
        }


class TriviaJokeTool:
    """Curated collection of entertaining facts, programming jokes, quotes, and riddles."""

    JOKES = [
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
        "Why did the Python programmer get glasses? Because they couldn't C#! 🐍",
        "There are 10 types of people in the world: those who understand binary, and those who don't. 💻",
        "Why was the JavaScript developer sad? Because they didn't Node how to Express themselves! 🚀",
        "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?' 📊",
        "How do you comfort a JavaScript bug? You console it! 😄",
        "Why do Java programmers wear glasses? Because they don't C#! ☕",
        "An optimist sees the glass half full. A pessimist sees it half empty. A programmer sees it twice as large as necessary! 🥤",
        "Real programmers count from 0. 🔢",
        "Why did the function break up with the loop? It felt like they were going in circles! 🔄"
    ]

    TRIVIA = [
        "🧠 **Did you know?** The first computer programmer was Ada Lovelace in 1843, who wrote an algorithm for Charles Babbage's Analytical Engine.",
        "🐍 **Did you know?** Python was named after the British comedy troupe *Monty Python*, not the snake!",
        "🚀 **Did you know?** The Apollo 11 guidance computer had only 4KB of RAM and a 32KB hard drive, but it landed humans on the Moon!",
        "🌐 **Did you know?** The world's first website (info.cern.ch) was published on August 6, 1991 by Tim Berners-Lee.",
        "🎮 **Did you know?** The first video game was 'Spacewar!', created in 1962 on a PDP-1 minicomputer at MIT.",
        "💾 **Did you know?** The first 1GB hard drive was released in 1980 by IBM. It weighed about 550 pounds (250 kg) and cost $40,000!"
    ]

    QUOTES = [
        "💡 *'Talk is cheap. Show me the code.'* — Linus Torvalds",
        "✨ *'Programs must be written for people to read, and only incidentally for machines to execute.'* — Harold Abelson",
        "🌟 *'Simplicity is prerequisite for reliability.'* — Edsger W. Dijkstra",
        "🚀 *'The only way to do great work is to love what you do.'* — Steve Jobs",
        "⚡ *'Make it work, make it right, make it fast.'* — Kent Beck",
        "🎯 *'First, solve the problem. Then, write the code.'* — John Johnson"
    ]

    RIDDLES = [
        ("🧩 **Riddle**: What has keys, but no locks; space, but no room; and you can enter, but never go in?\n\n||*Answer: A Keyboard!*||"),
        ("🧩 **Riddle**: I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?\n\n||*Answer: An Echo!*||"),
        ("🧩 **Riddle**: What gets wetter and wetter the more it dries?\n\n||*Answer: A Towel!*||"),
        ("🧩 **Riddle**: The more you take, the more you leave behind. What are they?\n\n||*Answer: Footsteps!*||"),
        ("🧩 **Riddle**: I have branches, but no fruit, trunk or leaves. What am I?\n\n||*Answer: A Bank!*||")
    ]

    @classmethod
    def get_joke(cls) -> str:
        return f"🎭 {random.choice(cls.JOKES)}"

    @classmethod
    def get_trivia(cls) -> str:
        return random.choice(cls.TRIVIA)

    @classmethod
    def get_quote(cls) -> str:
        return random.choice(cls.QUOTES)

    @classmethod
    def get_riddle(cls) -> str:
        return random.choice(cls.RIDDLES)
