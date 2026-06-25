# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Translation & Currency Converter for Atomic Search
Instant translations and currency conversions
"""

import re
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class Translation:
    """Translation result"""
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: float = 0.9


@dataclass  
class CurrencyConversion:
    """Currency conversion result"""
    from_amount: float
    from_currency: str
    to_amount: float
    to_currency: str
    rate: float


# Currency rates (simplified - in production would fetch from API)
CURRENCY_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 149.50,
    "CAD": 1.36,
    "AUD": 1.53,
    "CHF": 0.88,
    "CNY": 7.24,
    "INR": 83.12,
    "BTC": 0.000024,
    "ETH": 0.00042,
}

# Language codes
LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "ru": "Russian", "ja": "Japanese",
    "ko": "Korean", "zh": "Chinese", "ar": "Arabic", "hi": "Hindi",
    "nl": "Dutch", "pl": "Polish", "tr": "Turkish", "sv": "Swedish",
}


class Translator:
    """Translation engine"""
    
    def __init__(self):
        self.currency_rates = CURRENCY_RATES.copy()
    
    def translate(self, text: str, source: str = "auto", target: str = "en") -> Optional[Translation]:
        """
        Translate text (simplified - uses replacements for demo)
        In production, would integrate with LibreTranslate, Google Translate API, etc.
        """
        if not text or len(text) > 500:
            return None
        
        # Simple pattern matching for common phrases
        translations = {
            "hello": {"es": "hola", "fr": "bonjour", "de": "hallo", "ja": "こんにちは"},
            "goodbye": {"es": "adios", "fr": "au revoir", "de": "auf wiedersehen"},
            "thank you": {"es": "gracias", "fr": "merci", "de": "danke"},
            "yes": {"es": "si", "fr": "oui", "de": "ja"},
            "no": {"es": "no", "fr": "non", "de": "nein"},
        }
        
        text_lower = text.lower().strip()
        
        if text_lower in translations:
            if target in translations[text_lower]:
                return Translation(
                    source_text=text,
                    translated_text=translations[text_lower][target],
                    source_lang=source,
                    target_lang=target,
                    confidence=0.95
                )
        
        return Translation(
            source_text=text,
            translated_text=f"[{target.upper()}] {text}",
            source_lang=source,
            target_lang=target,
            confidence=0.5
        )
    
    def detect_language(self, text: str) -> str:
        """Detect language (simplified)"""
        if not text:
            return "en"
        
        # Check for common patterns
        if re.search(r'[\u4e00-\u9fff]', text):
            return "zh"
        if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return "ja"
        if re.search(r'[\uac00-\ud7af]', text):
            return "ko"
        if re.search(r'[\u0400-\u04ff]', text):
            return "ru"
        if re.search(r'[\u0600-\u06ff]', text):
            return "ar"
        
        return "en"
    
    def convert_currency(self, amount: float, from_curr: str, to_curr: str) -> Optional[CurrencyConversion]:
        """Convert currency"""
        from_curr = from_curr.upper()
        to_curr = to_curr.upper()
        
        if from_curr not in self.currency_rates or to_curr not in self.currency_rates:
            return None
        
        from_rate = self.currency_rates[from_curr]
        to_rate = self.currency_rates[to_curr]
        
        # Convert through USD
        amount_usd = amount / from_rate
        result = amount_usd * to_rate
        
        return CurrencyConversion(
            from_amount=amount,
            from_currency=from_curr,
            to_amount=round(result, 2),
            to_currency=to_curr,
            rate=round(to_rate / from_rate, 6)
        )


class SearchEnhancer:
    """Enhance search with instant answers"""
    
    def __init__(self):
        self.translator = Translator()
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Setup regex patterns for instant answers"""
        # Translation: "translate X to Spanish"
        self.translate_pattern = re.compile(
            r'translate ["\']?(.+?)["\']? to (\w+)',
            re.IGNORECASE
        )
        
        # Currency: "100 USD to EUR"
        self.currency_pattern = re.compile(
            r'(\d+(?:\.\d+)?)\s*([A-Z]{3})\s+(?:to|in)\s+([A-Z]{3})',
            re.IGNORECASE
        )
        
        # Calculator: "calc 2+2" or "2+2"
        self.calc_pattern = re.compile(r'^[\d\s\+\-\*\/\.\(\)]+$')
        
        # Weather: "weather in London"
        self.weather_pattern = re.compile(
            r'weather (?:in |at )?(.+)',
            re.IGNORECASE
        )
        
        # Time: "time in Tokyo"
        self.time_pattern = re.compile(
            r'time (?:in |at )?(.+)',
            re.IGNORECASE
        )
        
        # Definition: "define X" or "what is X"
        self.define_pattern = re.compile(
            r'(?:define|what is|meaning of) ["\']?(.+?)["\']?$',
            re.IGNORECASE
        )
    
    def check_instant_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """Check if query matches instant answer patterns"""
        query = query.strip()
        
        # Currency conversion
        match = self.currency_pattern.search(query)
        if match:
            amount = float(match.group(1))
            from_curr = match.group(2).upper()
            to_curr = match.group(3).upper()
            result = self.translator.convert_currency(amount, from_curr, to_curr)
            if result:
                return {
                    "type": "currency",
                    "query": query,
                    "answer": f"{result.from_amount:,.2f} {result.from_currency} = {result.to_amount:,.2f} {result.to_currency}",
                    "details": {
                        "rate": f"1 {result.from_currency} = {result.rate} {result.to_currency}"
                    }
                }
        
        # Translation
        match = self.translate_pattern.search(query)
        if match:
            text = match.group(1)
            target = match.group(2).lower()
            result = self.translator.translate(text, target=target)
            if result:
                return {
                    "type": "translation",
                    "query": query,
                    "answer": result.translated_text,
                    "details": {
                        "source": result.source_lang,
                        "target": result.target_lang
                    }
                }
        
        # Calculator
        if self.calc_pattern.match(query):
            try:
                result = eval(query)
                return {
                    "type": "calculator",
                    "query": query,
                    "answer": str(result),
                    "details": {"expression": query}
                }
            except:
                pass
        
        # Time
        match = self.time_pattern.search(query)
        if match:
            location = match.group(1)
            return {
                "type": "time",
                "query": query,
                "answer": f"Time in {location}: Click to search",
                "details": {"location": location}
            }
        
        # Weather
        match = self.weather_pattern.search(query)
        if match:
            location = match.group(1)
            return {
                "type": "weather",
                "query": query,
                "answer": f"Weather in {location}: Click to search",
                "details": {"location": location}
            }
        
        return None
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        return list(self.currency_rates.keys())
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dict of supported languages"""
        return LANGUAGES.copy()


# Global instance
_enhancer = SearchEnhancer()


def get_instant_answer(query: str) -> Optional[Dict]:
    """Get instant answer for query"""
    return _enhancer.check_instant_answer(query)


def translate_text(text: str, source: str = "auto", target: str = "en") -> Optional[Translation]:
    """Translate text"""
    return _enhancer.translator.translate(text, source, target)


def convert_currency(amount: float, from_curr: str, to_curr: str) -> Optional[CurrencyConversion]:
    """Convert currency"""
    return _enhancer.translator.convert_currency(amount, from_curr, to_curr)


def get_search_enhancer() -> SearchEnhancer:
    """Get search enhancer instance"""
    return _enhancer
