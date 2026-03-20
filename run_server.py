#!/usr/bin/env python
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from backend.main import app
        import uvicorn
        print("Starting server on http://127.0.0.1:8000")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
