import sys
import os
import uvicorn

sys.path.insert(0, os.path.dirname(__file__))
from app.main import app

if __name__ == "__main__":
    print("Starting VoiceGuard AI server on http://127.0.0.1:8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
