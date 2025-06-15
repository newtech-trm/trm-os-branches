from fastapi import FastAPI
from contextlib import asynccontextmanager
from trm_api.core.config import settings
from trm_api.db.session import connect_to_db, close_db_connection
from trm_api.core.logging_config import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Actions on startup
    setup_logging()
    print("--- Server starting up ---")
    connect_to_db()
    yield
    # Actions on shutdown
    print("--- Server shutting down ---")
    close_db_connection()

# Initialize the FastAPI app with the lifespan manager
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
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

# Kết thúc khởi động server khi chạy trực tiếp (python -m trm_api.main)
if __name__ == "__main__":
    import uvicorn
    import logging
    
    # Cấu hình logging chi tiết hơn
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Bật logging cho neomodel (xem log truy vấn Neo4j)
    neomodel_logger = logging.getLogger('neomodel')
    neomodel_logger.setLevel(logging.DEBUG)
    
    print(f"[TRM API] Khởi động server trên cổng 8001 với logging cấp độ DEBUG")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")
