import logging
import time
import subprocess
from docker import from_env

class Container:
    def __init__(self, container_name, compose_file, description, status):
        self.container_name = container_name  # Имя контейнера
        self.compose_file = compose_file  # Путь к файлу compose
        self.description = description  # Описание контейнера
        self.status = status  # Статус контейнера

    def start(self, action_interval):
        # Запуск контейнера с задержкой
        logging.info(f"Waiting for {action_interval} seconds before starting missing container: {self.compose_file}")
        time.sleep(action_interval)
        try:
            subprocess.run(["docker", "compose", "-f", f"files/{self.compose_file}", "up", "-d"], check=True)
            self.status = 'running'  # Обновление статуса контейнера
            logging.info(f"Started container: {self.compose_file} ({self.description})")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to start container: {self.compose_file}. Error: {e}")

    def stop(self):
        # Остановка контейнера
        logging.info(f"Stopping unnecessary container: {self.container_name}")
        try:
            client = from_env()  # Подключение к Docker API
            container = client.containers.get(self.container_name)  # Получение контейнера по имени
            container.stop()  # Остановка контейнера
            self.status = 'stopped'  # Обновление статуса контейнера
            logging.info(f"Stopped container: {self.container_name}")
        except Exception as e:
            logging.error(f"Failed to stop container: {self.container_name}. Error: {e}")

    def to_dict(self):
        # Преобразование объекта контейнера в словарь для сохранения состояния
        return {
            'container_name': self.container_name,
            'compose_file': self.compose_file,
            'description': self.description,
            'status': self.status
        }
