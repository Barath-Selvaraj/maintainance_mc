import os
import subprocess


class DeploymentService:

    FEATURE_REPOSITORIES = {
        "feature1": "https://github.com/Barath-Selvaraj/feature1_mc.git",
    }

    def clone_feature(self, feature_name: str):

        if feature_name not in self.FEATURE_REPOSITORIES:
            raise ValueError(f"Unknown feature: {feature_name}")

        repository_url = self.FEATURE_REPOSITORIES[feature_name]

        workspace = "/workspace"
        feature_path = os.path.join(workspace, feature_name)

        if os.path.exists(feature_path):
            return {
                "status": "already_exists",
                "feature": feature_name,
                "path": feature_path,
            }

        subprocess.run(
            [
                "git",
                "clone",
                repository_url,
                feature_path,
            ],
            check=True,
        )

        return {
            "status": "cloned",
            "feature": feature_name,
            "path": feature_path,
        }