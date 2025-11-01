from fastapi import FastAPI
import uvicorn
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from internal.config.config import Config

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    cfg = Config()
    print("Config loaded:", cfg)
    uvicorn.run(
        app, 
        host=cfg.rest_host, 
        port=cfg.rest_port  # Используем порт из конфига
    )