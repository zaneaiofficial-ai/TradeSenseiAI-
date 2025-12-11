#!/usr/bin/env python
"""Standalone server runner for TradeSensei backend."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    import uvicorn
    try:
        print("Starting TradeSensei AI backend...")
        uvicorn.run(
            'backend.main:app',
            host='127.0.0.1',
            port=8000,
            reload=False,
            log_level='info'
        )
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
