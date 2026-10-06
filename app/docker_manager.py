import docker


class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def get_containers(self):
        containers = self.client.containers.list(all=True)

        return [
            {
                "name": container.name,
                "status": container.status,
                "id": container.short_id,
            }
            for container in containers
        ]

    def get_container_count(self):
        return len(self.client.containers.list(all=True))