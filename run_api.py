#!/usr/bin/env python
"""Run FastAPI server."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    from src.phishing.config.settings import settings

    uvicorn.run(
        "src.phishing.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
