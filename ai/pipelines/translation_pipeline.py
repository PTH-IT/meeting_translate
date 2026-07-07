"""Translation pipeline with entity preservation."""
import os
from typing import Dict, List, Optional

from ai.models.translation_model import TranslationModel
from ai.postprocess.output_formatter import OutputFormatter


class TranslationPipeline:
    """Multilingual translation pipeline."""
    
    def __init__(self):
        self.model = TranslationModel()
        self.formatter = OutputFormatter()
        self.mock_mode = os.environ.get("MOCK_TRANSLATION", "true").lower() == "true"
    
    async def translate(self, text: str, target_lang: str = "vi") -> str:
        if self.mock_mode:
            return self.model._mock_translate(text, target_lang)
        
        entities = self.formatter.extract_entities(text)
        translated = await self.model.translate(text, target_lang=target_lang)
        return self.formatter.restore_entities(translated, entities)
    
    async def translate_batch(self, texts: List[str], target_langs: List[str]) -> Dict[str, List[str]]:
        result = {lang: [] for lang in target_langs}
        for text in texts:
            for lang in target_langs:
                result[lang].append(await self.translate(text, target_lang=lang))
        return result
