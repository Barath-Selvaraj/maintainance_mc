from fastapi import FastAPI

app = FastAPI(
    title="On-Premise Management Service",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "service": "management-service",
        "status": "running",
        "message": "On-premise management service is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }