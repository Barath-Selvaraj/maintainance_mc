import time
import threading

import docker


class MonitoringService:

    CHECK_INTERVAL = 15
    RESTART_THRESHOLD = 3

    def __init__(self):

        self.docker_client = docker.from_env()

        self.previous_restart_counts = {}

        self.alerted_containers = set()

        self.latest_status = []

        self.running = False

    def check_containers(self):

        containers = self.docker_client.containers.list(
            all=True
        )

        current_status = []

        for container in containers:

            container.reload()

            restart_count = container.attrs[
                "RestartCount"
            ]

            status = container.status

            current_status.append({
                "name": container.name,
                "status": status,
                "restart_count": restart_count,
                "id": container.short_id,
            })

            previous_count = self.previous_restart_counts.get(
                container.name,
                restart_count
            )

            new_restarts = restart_count - previous_count

            if (
                restart_count >= self.RESTART_THRESHOLD
                and container.name not in self.alerted_containers
            ):

                self.send_restart_alert(
                    container.name,
                    restart_count
                )

                self.alerted_containers.add(
                    container.name
                )

            self.previous_restart_counts[
                container.name
            ] = restart_count

        self.latest_status = current_status

    def send_restart_alert(
        self,
        container_name,
        restart_count
    ):

        print(
            f"ALERT: {container_name} "
            f"has restarted {restart_count} times"
        )

    def get_status(self):

        return {
            "containers": self.latest_status
        }

    def start(self):

        if self.running:
            return

        self.running = True

        thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )

        thread.start()

    def _monitor_loop(self):

        while self.running:

            try:

                self.check_containers()

            except Exception as error:

                print(
                    f"Monitoring error: {error}"
                )

            time.sleep(
                self.CHECK_INTERVAL
            )