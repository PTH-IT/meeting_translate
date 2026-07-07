"""Output formatting, entity preservation, confidence scoring."""
import re
from typing import Dict, List


class OutputFormatter:
    """Format AI outputs with entity preservation."""
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        entities = {
            "urls": [],
            "emails": [],
            "numbers": [],
        }
        entities["urls"] = re.findall(r'https?://[^\s]+', text)
        entities["emails"] = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        entities["numbers"] = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        return entities
    
    @staticmethod
    def restore_entities(text: str, entities: Dict[str, List[str]]) -> str:
        for url in entities["urls"]:
            if url in text:
                text = text.replace(url, f"<URL>{url}</URL>")
        for email in entities["emails"]:
            if email in text:
                text = text.replace(email, f"<EMAIL>{email}</EMAIL>")
        for num in entities["numbers"]:
            if num in text:
                text = text.replace(num, f"<NUM>{num}</NUM>")
        return text
