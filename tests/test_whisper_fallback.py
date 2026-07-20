import asyncio
import unittest

from ai.models.whisper_model import WhisperModel


class WhisperFallbackTest(unittest.TestCase):
    def test_transcribe_falls_back_to_mock_when_model_unavailable(self):
        model = WhisperModel(model_name="tiny", device="cpu")
        model.mock_mode = False
        result = asyncio.run(model.transcribe([0.0, 0.1, 0.2], sample_rate=16000))
        self.assertIn("segments", result)


if __name__ == "__main__":
    unittest.main()
