import logging
import os
import subprocess
import threading
import time
from docker import from_env
from flask import Flask, jsonify

from state import State

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Параметры сервиса
api_host = os.getenv('API_HOST', '0.0.0.0')
api_port = int(os.getenv('API_PORT', 8080))
check_interval = int(os.getenv('CHECK_INTERVAL', 60))
action_interval = int(os.getenv('ACTION_INTERVAL', 5))

# Инициализация Flask приложения
app = Flask(__name__)

# Глобальная переменная для хранения текущего состояния контейнеров
current_state = []

# Функция для обновления текущего состояния контейнеров
def update_current_state(client, state):
    global current_state
    # Получение списка всех запущенных контейнеров
    containers = client.containers.list()
    running_container_names = [container.attrs['Name'][1:] for container in containers]

    # Получение желаемых и отключенных контейнеров из состояния
    desired_containers = state.get_enabled_containers()
    disabled_containers = state.get_disabled_containers()

    # Обновление текущего состояния контейнеров
    current_state = []
    for container in desired_containers:
        if container.container_name in running_container_names:
            container.status = 'running'
        else:
            container.status = 'stopped'
        current_state.append(container.to_dict())

    for container in disabled_containers:
        if container.container_name in running_container_names:
            container.status = 'running'
        else:
            container.status = 'stopped'
        current_state.append(container.to_dict())

# Функция для проверки и управления контейнерами
def check_and_manage_containers(client, state):
    global action_thread

    # Получение списка всех запущенных контейнеров
    running_containers = client.containers.list()
    running_container_names = [container.attrs['Name'][1:] for container in running_containers]

    # Получение списка всех контейнеров из state.yml
    state.load_state()  # Перечитываем файл, вдруг там что-то изменилось
    state_containers = state.get_all_containers_state()
    state_container_names = state.get_container_names()

    # Фильтрация контейнеров, не описанных в state.yml
    filtered_running_containers = [container for container in running_containers if container.attrs['Name'][1:] in state_container_names]

    # Проверка и выключение контейнеров, которые работают, но отключены в state.yml
    for r_container in filtered_running_containers:
        state_container = next((c for c in state_containers if c.container_name == r_container.attrs['Name'][1:]), None)
        if state_container and state_container.status == 'disabled':
            logging.info(f"Stopping unnecessary container: {r_container.attrs['Name'][1:]}")
            r_container.stop()
            logging.info(f"Stopped container: {r_container.attrs['Name'][1:]}")

    # Проверка и запуск контейнеров, которые включены в state.yml, но не запущены
    for state_container in state_containers:
        if state_container.container_name not in running_container_names and state_container.status == 'enabled':
            logging.info(f"Waiting for {action_interval} seconds before starting missing container: {state_container.compose_file}")
            try:
                compose_file_path = f"files/{state_container.compose_file}"
                if not os.path.exists(compose_file_path):
                    logging.error(f"Compose file not found: {compose_file_path}")
                    continue
                subprocess.run(["docker", "compose", "-f", compose_file_path, "up", "-d"], check=True)
                logging.info(f"Started container: {state_container.compose_file} ({state_container.description})")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to start container: {state_container.compose_file}. Error: {e}")

# Функция для мониторинга контейнеров
def monitor_containers(client, state):
    while True:
        try:
            check_and_manage_containers(client, state)
            update_current_state(client, state)
        except Exception as e:
            logging.error(f"Error in monitor_containers: {e}")
        time.sleep(check_interval)

# Функция для запуска API сервера
def run_api_server():
    @app.route('/api/v1/getRunningContainers', methods=['GET'])
    def get_running_containers():
        return jsonify(current_state)

    app.run(host=api_host, port=api_port)

# Функция для вывода информации при старте
def print_startup_info(state):
    logging.info(f"API Host: {api_host}")
    logging.info(f"API Port: {api_port}")
    logging.info(f"Check Interval: {check_interval} seconds")
    logging.info(f"Action Interval: {action_interval} seconds")
    containers = state.get_all_containers_state()
    logging.info(f"Managing {len(containers)} containers")
    enabled_containers = [container for container in containers if container.status == 'enabled']
    disabled_containers = [container for container in containers if container.status == 'disabled']
    active_containers = [container.container_name for container in enabled_containers]
    noactive_containers = [container.container_name for container in disabled_containers]
    logging.info(f"Enabled containers: {active_containers}")
    logging.info(f"Disabled containers: {noactive_containers}")

# Основная функция для инициализации и запуска сервиса
def main():
    global action_thread
    action_thread = None

    client = from_env()  # Подключение к Docker API

    state = State('/app/state/state.yml')  # Загрузка состояния из файла

    print_startup_info(state)  # Вывод информации при старте

    monitor_thread = threading.Thread(target=monitor_containers, args=(client, state))  # Создание потока для мониторинга контейнеров
    monitor_thread.start()

    api_thread = threading.Thread(target=run_api_server)  # Создание потока для API сервера
    api_thread.start()

if __name__ == "__main__":
    main()
