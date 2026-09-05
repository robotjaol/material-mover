import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import export, prediction

app = FastAPI(title="Pallet Flow Forecasting API", version="2.0.0")
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(prediction.router)
app.include_router(export.router)


@app.get("/health")
def health():
    return {"status": "ok"}
