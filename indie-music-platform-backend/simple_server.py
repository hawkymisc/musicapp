"""
シンプルなFastAPIサーバー
"""
from fastapi import FastAPI
import uvicorn

# 最小限のFastAPIアプリケーション
app = FastAPI(title="シンプルAPIサーバー")

@app.get("/")
async def root():
    return {"message": "Hello, World\!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# サーバー起動
if __name__ == "__main__":
    uvicorn.run("simple_server:app", host="127.0.0.1", port=8000, reload=True)
