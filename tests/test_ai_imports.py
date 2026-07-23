import unittest

from ai.main import app


class AIImportsTest(unittest.TestCase):
    def test_app_imports(self):
        self.assertIsNotNone(app)


if __name__ == "__main__":
    unittest.main()
