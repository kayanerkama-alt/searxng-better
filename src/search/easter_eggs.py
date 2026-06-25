# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Easter Eggs & Hidden Features for Atomic Search
Fun surprises for power users!
"""

import random
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EasterEgg:
    """An easter egg definition"""
    trigger: str
    response: str
    response_type: str = "text"  # text, ascii, animation, game
    rarity: float = 1.0  # 0.0 to 1.0, probability of showing
    sound: Optional[str] = None
    requires_exact: bool = False


class EasterEggManager:
    """
    Manages all easter eggs and hidden features
    """
    
    # Built-in easter eggs
    EASTER_EGGS = [
        EasterEgg(
            trigger="42",
            response="🎲 The answer to life, the universe, and everything is... 42!\n\nBut what was the question?",
            rarity=0.5
        ),
        EasterEgg(
            trigger="hello world",
            response="""🐍 Hello, World!

    print("Hello, World!")
    ^~~~^
   /     \\
  | 0   0 |
   \\  △  /
    \\___/""",
            response_type="ascii",
            rarity=0.8
        ),
        EasterEgg(
            trigger="ping",
            response="🏓 Pong! Latency: {}ms",
            response_type="animation",
            rarity=1.0
        ),
        EasterEgg(
            trigger="who are you",
            response="🤖 I am Atomic Search, a privacy-first search engine!\n\nI don't track, I don't profile, and I definitely don't sell your data.",
            rarity=0.9
        ),
        EasterEgg(
            trigger="sudo make me a sandwich",
            response="🍞 What? Make it yourself!\n\n(jk, here you go: 🥪)",
            rarity=0.5
        ),
        EasterEgg(
            trigger="hack the planet",
            response="""💀 CYCLOPS ACTIVATED...

    ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗
    ██╔══██╗██║  ██║██╔═══██╗██╔════╝╚══██╔══╝
    ██████╔╝███████║██║   ██║███████╗   ██║   
    ██╔═══╝ ██╔══██║██║   ██║╚════██║   ██║   
    ██║     ██║  ██║╚██████╔╝███████║   ██║   
    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   

Just kidding! Try searching for something instead. 🔍""",
            response_type="ascii",
            rarity=0.1
        ),
        EasterEgg(
            trigger="matrix",
            response="""🟢 Wake up, Neo...

    The Matrix has you...
    Follow the white rabbit.🐰

🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩
🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩
🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩
🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩

(But seriously, search something!)""",
            response_type="ascii",
            rarity=0.2
        ),
        EasterEgg(
            trigger="give me pizza",
            response="🍕 Here's a pizza!\n\n    🍕\n   /| |\\\n  / | | \\\n |  | |  |\n  \\ | | /\n   \\|_|/",
            response_type="ascii",
            rarity=0.6
        ),
        EasterEgg(
            trigger="roll dice",
            response="🎲 Rolling dice... *click click click*\n\nYou rolled a {}! 🎉",
            rarity=1.0
        ),
        EasterEgg(
            trigger="flip coin",
            response="🪙 Flipping coin... *whirr*\n\nYou got {}!",
            rarity=1.0
        ),
        EasterEgg(
            trigger="rps",
            response="✊✋✌️ Rock Paper Scissors!\n\nChoose: rock, paper, or scissors\n\nI choose {}!",
            rarity=0.8
        ),
        EasterEgg(
            trigger="coffee",
            response="☕ *brewing coffee...*\n\n        ( ((\n         ) ))\n        ._______.]\n        |      |]\n        \\      /\n         `----'",
            response_type="ascii",
            rarity=0.7
        ),
        EasterEgg(
            trigger="cat",
            response="""🐱 Meow!

   /\\_____/\\
  /  o   o  \\
 ( ==  ^  == )
  )         (
 /           \\
/     }     {  \\
\\    /\\____/\\  /
 \\__|  |  | __/
    (__|__|__)
    
*cat purrs*""",
            response_type="ascii",
            rarity=0.6
        ),
        EasterEgg(
            trigger="starwars",
            response="""⭐ A long time ago in a galaxy far, far away...

    ★  ☆  ★  ☆  ★
    
        ╔═══════════════════════════════╗
        ║   Episode IV                ║
        ║   A NEW HOPE                 ║
        ║                              ║
        ║   It is a period of civil    ║
        ║   war...                     ║
        ╚═══════════════════════════════╝""",
            response_type="ascii",
            rarity=0.3
        ),
        EasterEgg(
            trigger="道",
            response="☯️ 道可道，非常道。名可名，非常名。\n\nThe way that can be spoken is not the eternal way.",
            rarity=0.5
        ),
        EasterEgg(
            trigger="1337",
            response="""🦁 Leet Speak Activated!

    /\\/\\/\\    1337    /\\/\\/\\
      /  \\      SPEAK    /  \\
     / /\\ \\    ACTIVATED  /\\ \\
    / /  \\ \\              /  \\ \\
   /_/    \\_\\            /    \\_\\
   
G3t 0wn3d!1!""",
            response_type="ascii",
            rarity=0.4
        ),
        EasterEgg(
            trigger="magic 8 ball",
            response="🔮 *shaking magic 8 ball...*\n\nThe spirits have spoken: {}",
            rarity=1.0
        ),
        EasterEgg(
            trigger="fortune",
            response="🍀 {}",
            rarity=1.0
        ),
        EasterEgg(
            trigger="joke",
            response="😂 {}",
            rarity=1.0
        ),
        EasterEgg(
            trigger="fact",
            response="📚 Did you know?\n\n{}",
            rarity=1.0
        ),
        EasterEgg(
            trigger="quote",
            response="💬 \"{}\"\n\n— {}",
            rarity=1.0
        ),
        EasterEgg(
            trigger="konami",
            response="🎮 KONAMI CODE!!!\n\n↑↑↓↓←→←→BA\n\n+30 LIVES! 🕹️\n\n(Just kidding, but nice try!)",
            response_type="ascii",
            rarity=0.1
        ),
    ]
    
    # Data for random responses
    MAGIC_8_BALL_RESPONSES = [
        "Yes, definitely.",
        "My sources say no.",
        "Reply hazy, try again.",
        "Don't count on it.",
        "Yes.",
        "No.",
        "Outlook not so good.",
        "Signs point to yes.",
        "Absolutely!",
        "I don't think so.",
        "Very likely.",
        "Ask again later.",
        "42.",
        "Only time will tell.",
        "Without a doubt."
    ]
    
    FORTUNES = [
        "A beautiful day for a search!",
        "Your next search will be even better.",
        "Privacy is not a privilege, it's a right.",
        "The best search is one that respects you.",
        "Today is a great day for discovery!",
        "Someone is looking for exactly what you found.",
        "The best things in life are not things.",
        "You have excellent taste in search engines.",
        "Your privacy is protected today.",
        "A wise person once said: use Atomic Search."
    ]
    
    JOKES = [
        "Why do programmers prefer dark mode?\nBecause light attracts bugs.",
        "How many programmers does it take to change a light bulb?\nNone, that's a hardware problem.",
        "Why was the JavaScript developer sad?\nBecause he didn't Node how to Express himself.",
        "What do you call a search engine that doesn't track?\nA-maze-ing!",
        "Why do search engines make terrible chefs?\nThey always return results, but no recipes.",
        "I told my computer I needed a break.\nIt hasn't sent me any notifications since.",
        "Why did the privacy-conscious user bring a ladder?\nTo access the high-quality results.",
        "What's an privacy-advocate's favorite game?\nHide and seek (for data).",
    ]
    
    FACTS = [
        "The first search engine was called Archie, created in 1990.",
        "Google processes over 3.5 billion searches per day.",
        "91% of pages get zero traffic from Google.",
        "The first computer virus was created in 1971.",
        "The @ symbol was first used in an email address in 1971.",
        "The first webcam was used at Cambridge University to monitor a coffee pot.",
        "Google's index contains trillions of web pages.",
        "The term 'spam' for junk email comes from a Monty Python sketch.",
        "The first 1GB hard drive weighed about 550 pounds.",
        "QR codes were created in 1994 by Toyota."
    ]
    
    QUOTES = [
        ("The internet is becoming the town square for the global village of tomorrow.", "Bill Gates"),
        ("The best way to predict the future is to invent it.", "Alan Kay"),
        ("Privacy is not about hiding something. It's about being able to control who has access to information about you.", "Eduardo Sahara"),
        ("The cloud is just someone else's computer.", "Anonymous"),
        ("Any sufficiently advanced technology is indistinguishable from magic.", "Arthur C. Clarke"),
        ("Talk is cheap. Show me the code.", "Linus Torvalds"),
        ("First, solve the problem. Then, write the code.", "John Johnson"),
        ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ]
    
    def __init__(self):
        self._triggers: Dict[str, EasterEgg] = {}
        self._register_eggs()
        self._stats = {"triggered": 0, "by_egg": {}}
    
    def _register_eggs(self):
        """Register all easter eggs"""
        for egg in self.EASTER_EGGS:
            key = egg.trigger.lower()
            if egg.requires_exact:
                self._triggers[key] = egg
            else:
                # Add partial match
                self._triggers[key] = egg
    
    def check_trigger(self, query: str) -> Optional[str]:
        """
        Check if query triggers an easter egg
        
        Args:
            query: The search query
        
        Returns:
            Easter egg response or None
        """
        query_lower = query.lower().strip()
        
        # Check exact matches
        for trigger, egg in self._triggers.items():
            if egg.requires_exact:
                if query_lower == trigger:
                    return self._execute_egg(egg, query)
            else:
                if trigger in query_lower or query_lower == trigger:
                    # Check rarity
                    if random.random() <= egg.rarity:
                        result = self._execute_egg(egg, query)
                        self._stats["triggered"] += 1
                        self._stats["by_egg"][egg.trigger] = self._stats["by_egg"].get(egg.trigger, 0) + 1
                        return result
        
        return None
    
    def _execute_egg(self, egg: EasterEgg, query: str) -> str:
        """Execute an easter egg and format the response"""
        response = egg.response
        
        # Handle dynamic content
        if "{}" in response:
            if "dice" in egg.trigger:
                import time
                response = response.replace("{}", str(random.randint(1, 6)))
            elif "coin" in egg.trigger:
                result = random.choice(["Heads 🪙", "Tails 🪙"])
                response = response.replace("{}", result)
            elif "rps" in egg.trigger:
                choices = ["rock ✊", "paper ✋", "scissors ✌️"]
                response = response.replace("{}", random.choice(choices))
            elif "magic 8 ball" in egg.trigger:
                response = response.replace("{}", random.choice(self.MAGIC_8_BALL_RESPONSES))
            elif "fortune" in egg.trigger:
                response = response.replace("{}", random.choice(self.FORTUNES))
            elif "joke" in egg.trigger:
                response = response.replace("{}", random.choice(self.JOKES))
            elif "fact" in egg.trigger:
                response = response.replace("{}", random.choice(self.FACTS))
            elif "quote" in egg.trigger:
                quote, author = random.choice(self.QUOTES)
                response = response.replace("{}", quote)
                response = response.replace("— {}", f"— {author}")
            elif "ping" in egg.trigger:
                import time
                latency = random.randint(5, 150)
                response = response.replace("{}", str(latency))
        
        return response
    
    def get_stats(self) -> Dict[str, Any]:
        """Get easter egg statistics"""
        return {
            "total_triggered": self._stats["triggered"],
            "top_eggs": sorted(
                self._stats["by_egg"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "total_eggs": len(self.EASTER_EGGS)
        }


# Global instance
_easter_eggs = EasterEggManager()


def check_easter_egg(query: str) -> Optional[str]:
    """Check if query triggers an easter egg"""
    return _easter_eggs.check_trigger(query)


def get_easter_egg_stats() -> Dict[str, Any]:
    """Get easter egg statistics"""
    return _easter_eggs.get_stats()
