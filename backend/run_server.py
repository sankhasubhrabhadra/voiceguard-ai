import sys
import os
import uvicorn

sys.path.insert(0, os.path.dirname(__file__))
from app.main import app

if __name__ == "__main__":
    print("Starting VoiceGuard AI server on http://0.0.0.0:8000 (accessible via localhost & 127.0.0.1)...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
