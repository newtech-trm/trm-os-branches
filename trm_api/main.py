from fastapi import FastAPI
from trm_api.core.config import settings

# Initialize the FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get("/", tags=["Root"])
def read_root():
    """
    Welcome endpoint.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "ok"}

# Include the main API router
from trm_api.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
