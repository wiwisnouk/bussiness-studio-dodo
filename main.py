import os
from fastapi import FastAPI, HTTPException, Form
from routers.HomePage import router

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)