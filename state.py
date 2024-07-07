import yaml
from container import Container

class State:
    def __init__(self, file_path):
        self.file_path = file_path  # Путь к файлу state.yml
        self.containers = []  # Список контейнеров
        self.load_state()  # Загрузка состояния из файла

    def load_state(self):
        # Загрузка состояния из файла state.yml
        with open(self.file_path, 'r') as file:
            state_data = yaml.safe_load(file)
            self.containers = [Container(**container_data) for container_data in state_data.get('containers', [])]

    def get_enabled_containers(self):
        # Получение списка включенных контейнеров
        return [container for container in self.containers if container.status == 'enabled']

    def get_disabled_containers(self):
        # Получение списка отключенных контейнеров
        return [container for container in self.containers if container.status == 'disabled']

    def get_all_containers_state(self):
        # Получение всех контейнеров
        return self.containers

    def get_container_names(self):
        # Получение имен всех контейнеров
        return [container.container_name for container in self.containers]
