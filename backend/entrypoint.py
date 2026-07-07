import os
import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"
])
