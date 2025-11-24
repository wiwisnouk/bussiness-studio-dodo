from fastapi import FastAPI, HTTPException, Form
from routers import HomePage
from datetime import datetime

app = FastAPI()

app.include_router(HomePage.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)