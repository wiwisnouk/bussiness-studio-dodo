import os
from fastapi import FastAPI, HTTPException, Form
from routers import HomePage
from datetime import datetime

app = FastAPI()

app.include_router(HomePage.router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run(
        app,  # Передаем app объект напрямую
        host="0.0.0.0",
        port=port,
        reload=False
    )