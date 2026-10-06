from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.docker_manager import DockerManager
from app.deployment import DeploymentService
from app.monitoring import MonitoringService
from app.schemas.deployment import FeatureSelection


monitoring_service = MonitoringService()


@asynccontextmanager
async def lifespan(app: FastAPI):

    monitoring_service.start()

    yield


app = FastAPI(
    title="On-Premise Management Service",
    version="1.0.0",
    lifespan=lifespan,
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


@app.get("/features")
def get_features():

    deployment_service = DeploymentService()

    return {
        "features": deployment_service.get_features()
    }


@app.post("/deploy")
def deploy_features(selection: FeatureSelection):

    try:

        deployment_service = DeploymentService()

        return deployment_service.deploy_features(
            selection.features
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

@app.delete("/features/{feature_name}")
def remove_feature(feature_name: str):

    try:
        deployment_service = DeploymentService()

        return deployment_service.remove_feature(
            feature_name
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )    

