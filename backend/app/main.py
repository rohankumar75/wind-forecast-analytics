import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="UK Wind Forecast Analytics API",
    version="1.0.0",
    description="Wind forecast and actual generation analysis for January 2026."
)

origins = [os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"service": "UK Wind Forecast Analytics API", "docs": "/docs"}
