from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import config, plans
import uvicorn
import os

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="AutoDeployDocs API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development allowing all origins is fine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(plans.router, prefix="/api/plans", tags=["plans"])

# Mount Static Files
# Mount Static Files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True)
