from fastapi import FastAPI

from app.docker_manager import DockerManager


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


@app.get("/containers")
def get_containers():
    docker_manager = DockerManager()

    return {
        "containers": docker_manager.get_containers()
    }