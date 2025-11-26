import os
from fastapi import FastAPI, HTTPException, Form
from routers import HomePage

app = FastAPI()

app.include_router(HomePage.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)