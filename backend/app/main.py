"""
FastAPI entry point.
"""

import uvicorn
from core.app_factory import create_app

app = create_app()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
