import os
import subprocess
import tarfile
import io

import docker
from app.nginx_service import NginxService

class DeploymentService:

    FEATURE_REPOSITORIES = {
        "feature1": "https://github.com/Barath-Selvaraj/feature1_mc.git",
        "feature2": "https://github.com/Barath-Selvaraj/feature2_mc.git",
        "feature3": "https://github.com/Barath-Selvaraj/feature3_mc.git",
    }

    def __init__(self):
        self.docker_client = docker.from_env()
        self.nginx_service = NginxService()

    def get_features(self):
        return list(self.FEATURE_REPOSITORIES.keys())

    def deploy_features(self, selected_features):

        results = []

        for feature_name in selected_features:

            result = self.deploy_feature(feature_name)

            results.append(result)

        return {
            "status": "deployment_completed",
            "features": results
        }

    def deploy_feature(self, feature_name: str):

        if feature_name not in self.FEATURE_REPOSITORIES:
            raise ValueError(
                f"Unknown feature: {feature_name}"
            )

        repository_url = self.FEATURE_REPOSITORIES[feature_name]

        workspace = "/workspace"

        feature_path = os.path.join(
            workspace,
            feature_name
        )

        # Clone only the selected feature
        if not os.path.exists(feature_path):

            subprocess.run(
                [
                    "git",
                    "clone",
                    repository_url,
                    feature_path,
                ],
                check=True,
            )

        else:

            subprocess.run(
                [
                    "git",
                    "-C",
                    feature_path,
                    "pull",
                    "origin",
                    "main",
                ],
                check=True,
            )

        image_name = f"{feature_name}:latest"

        container_name = f"{feature_name}-container"

        # Build Docker image
        image = self._build_image(
            feature_path,
            image_name
        )

        # Remove old container if it exists
        try:

            old_container = self.docker_client.containers.get(
                container_name
            )

            old_container.remove(force=True)

        except docker.errors.NotFound:
            pass

        # Create and start container
        container = self.docker_client.containers.run(
            image=image.id,
            name=container_name,
            detach=True,
            network="proxy-network",
            labels={
                "managed-feature": "true",
                "feature-name": feature_name,
            },
        )

        self.nginx_service.update_configuration()

        return {
            "status": "deployed",
            "feature": feature_name,
            "repository": repository_url,
            "image": image_name,
            "container": container.name,
            "container_id": container.short_id,
        }

    def _build_image(self, feature_path: str, image_name: str):

        dockerfile_path = os.path.join(
            feature_path,
            "Dockerfile"
        )

        if not os.path.exists(dockerfile_path):
            raise ValueError(
                f"Dockerfile not found in {feature_path}"
            )

        # Create an in-memory tar build context
        tar_buffer = io.BytesIO()

        with tarfile.open(
            fileobj=tar_buffer,
            mode="w"
        ) as tar:

            for root, dirs, files in os.walk(feature_path):

                for file_name in files:

                    full_path = os.path.join(
                        root,
                        file_name
                    )

                    relative_path = os.path.relpath(
                        full_path,
                        feature_path
                    )

                    tar.add(
                        full_path,
                        arcname=relative_path
                    )

        tar_buffer.seek(0)

        image, logs = self.docker_client.images.build(
            fileobj=tar_buffer,
            custom_context=True,
            dockerfile="Dockerfile",
            tag=image_name,
            rm=True,
        )

        return image