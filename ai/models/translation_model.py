"""Translation model wrapper."""
import logging
import asyncio
import os
from typing import Optional

try:
    import torch
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    torch = None

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    AutoModelForCausalLM = None
    AutoTokenizer = None


logger = logging.getLogger(__name__)


class TranslationModel:
    """Multilingual translation model wrapper."""

    TARGET_LANGUAGES = {"vi": "vi", "en": "en", "ja": "ja", "zh": "zh"}
    GEMMA_LANG_MAP = {"vi": "Vietnamese", "en": "English", "ja": "Japanese", "zh": "Chinese"}

    def __init__(self, model_name: str = "google/gemma-2b-it", device: str = "cuda"):
        self.model_name = model_name
        self.device = "cuda" if torch is not None and getattr(torch, "cuda", None) is not None and torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.mock_mode = os.environ.get("MOCK_TRANSLATION", "false").lower() == "true"

        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.cache_dir = os.path.join(repo_root, "models", "huggingface")
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.info("TranslationModel init: mock_mode=%s model_name=%s device=%s cache_dir=%s", self.mock_mode, self.model_name, self.device, self.cache_dir)

    def _load_model_sync(self):
        if torch is None or AutoTokenizer is None or AutoModelForCausalLM is None:
            self.mock_mode = True
            return None, None

        logger.info("TranslationModel loading from_pretrained: %s cache_dir=%s device=%s", self.model_name, self.cache_dir, self.device)
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.cache_dir)
        dtype = torch.float16 if self.device == "cuda" else torch.float32

        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=dtype,
            cache_dir=self.cache_dir,
        )
        model.to(self.device)
        model.eval()
        logger.info("TranslationModel load success")
        return model, tokenizer

    async def load_model(self):
        """Load translation model asynchronously."""
        if self.model is None and not self.mock_mode:
            loop = asyncio.get_event_loop()
            self.model, self.tokenizer = await loop.run_in_executor(None, self._load_model_sync)
        elif self.model is not None:
            logger.debug("TranslationModel already loaded")
    
    def _mock_translate(self, text: str, target_lang: str) -> str:
        """Simple mock translation for testing."""
        if target_lang == "vi":
            if "hello" in text.lower():
                return "xin chào, đây là thử nghiệm"
            return f"[Dịch sang tiếng Việt] {text}"
        elif target_lang == "ja":
            if "hello" in text.lower():
                return "こんにちは、これはテストです"
            return f"[日本語訳] {text}"
        elif target_lang == "zh":
            if "hello" in text.lower():
                return "你好，这是一个测试"
            return f"[中文翻译] {text}"
        return text

    def _build_prompt(self, text: str, target_lang: str) -> str:
        tgt_lang = self.GEMMA_LANG_MAP[target_lang]

        return f"""
    You are a professional translator.

    Detect the source language automatically.

    Translate the text into {tgt_lang}.

    Return JSON only.

    {{
    "source_language": "<ISO639-1 code>",
    "translation": "<translated text>"
    }}

    Text:
    {text}
    """.strip()

    async def translate(
        self,
        text: str,
        target_lang: str = "vi",
    ) -> str:
        """Translate text to target language."""
        if self.mock_mode:
            return self._mock_translate(text, target_lang)

        await self.load_model()
        if self.mock_mode or self.model is None or self.tokenizer is None:
            return self._mock_translate(text, target_lang)

        prompt = self._build_prompt(text, target_lang)

        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt_text = self.tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            prompt_text = prompt

        loop = asyncio.get_event_loop()
        inputs = self.tokenizer(prompt_text, return_tensors="pt").to(self.device)

        with torch.no_grad():
            generated_tokens = await loop.run_in_executor(
                None,
                lambda: self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    do_sample=False,
                    temperature=0.0,
                    pad_token_id=self.tokenizer.eos_token_id,
                ),
            )

        output_tokens = generated_tokens[0][inputs.input_ids.shape[1]:]
        translation = self.tokenizer.decode(output_tokens, skip_special_tokens=True).strip()

        return translation or self._mock_translate(text, target_lang)

    async def detect_language(self, text: str) -> str:
        if self.mock_mode:
            return "en"

        await self.load_model()
        if self.mock_mode or self.model is None or self.tokenizer is None:
            return "en"

        prompt = f"""
    Detect the language of the following text.

    Return ONLY one ISO 639-1 language code.
    Supported codes:
    - vi
    - en
    - ja
    - zh

    Text:
    {text}
    """

        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        loop = asyncio.get_event_loop()

        with torch.no_grad():
            outputs = await loop.run_in_executor(
                None,
                lambda: self.model.generate(
                    **inputs,
                    max_new_tokens=8,
                    do_sample=False,
                    temperature=0.0,
                    pad_token_id=self.tokenizer.eos_token_id,
                ),
            )

        result = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True,
        ).strip().lower()

        if result in self.TARGET_LANGUAGES:
            return result

        return "en"