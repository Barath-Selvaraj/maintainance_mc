import os

import docker


class NginxService:

    def __init__(self):
        self.docker_client = docker.from_env()

        self.nginx_container_name = "onprem-nginx"

        self.config_path = (
            "/shared-nginx/snippets/features.conf"
        )

    def update_configuration(self):

        containers = self.docker_client.containers.list(
            filters={
                "label": "managed-feature=true"
            }
        )

        config = ""

        for container in containers:

            feature_name = container.labels.get(
                "feature-name"
            )

            if not feature_name:
                continue

            container_name = container.name

            config += f"""
            location = /{feature_name} {{
                proxy_pass http://{container_name}:8000/;

                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }}

            location /{feature_name}/ {{
                proxy_pass http://{container_name}:8000/;

                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }}
            """

        with open(self.config_path, "w") as file:
            file.write(config)

        self.reload_nginx()

    def reload_nginx(self):

        nginx_container = self.docker_client.containers.get(
            self.nginx_container_name
        )

        result = nginx_container.exec_run(
            ["nginx", "-s", "reload"]
        )

        if result.exit_code != 0:

            raise RuntimeError(
                f"Nginx reload failed: {result.output.decode()}"
            )