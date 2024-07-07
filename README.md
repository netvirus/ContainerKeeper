### README.md

# ContainerKeeper (CK)

ContainerKeeper (CK) — это сервис для управления контейнерами Docker, который автоматически запускает и останавливает контейнеры на основе заданных условий. Он обеспечивает мониторинг контейнеров, сверяя их текущее состояние с желаемым состоянием, описанным в конфигурационном файле `state.yml`. Сервис также предоставляет API для получения текущего состояния контейнеров.

## Особенности

- Автоматический запуск и остановка контейнеров в соответствии с состоянием, описанным в `state.yml`.
- Мониторинг состояния контейнеров с заданным интервалом.
- API для получения текущего состояния контейнеров.

## Установка

1. Установите Docker и Docker Compose.
2. Склонируйте репозиторий ContainerKeeper:
    ```bash
    git clone https://github.com/yourusername/ContainerKeeper.git
    ```
3. Перейдите в директорию проекта:
    ```bash
    cd ContainerKeeper
    ```
4. Сбилдить
   ```bash
    docker build . -t container_keeper:latest
    ```
## Настройка

1. Создайте файл `state.yml` в директории `state` и опишите в нем контейнеры, которые должны быть управляемыми сервисом. Пример:
    ```yaml
    containers:
      - container_name: web_server
        description: A web server container
        compose_file: web_server_compose.yml
        status: enabled
      - container_name: database
        description: A database container
        compose_file: database_compose.yml
        status: enabled
      - container_name: cache
        description: A cache container
        compose_file: cache_compose.yml
        status: enabled
    ```

2. Убедитесь, что файлы Docker Compose для каждого контейнера находятся в директории `files` и имеют соответствующие имена (например, `web_server_compose.yml`, `database_compose.yml`, `cache_compose.yml`).

## Использование

1. Постройте Docker образ и запустите контейнер:
    ```bash
    docker compose up -d
    ```

2. Логи сервиса можно просмотреть с помощью команды:
    ```bash
    docker compose logs -f
    ```

## Переменные окружения

- `API_HOST`: Хост для запуска API (по умолчанию: `0.0.0.0`).
- `API_PORT`: Порт для запуска API (по умолчанию: `8080`).
- `CHECK_INTERVAL`: Интервал проверки состояния контейнеров в секундах (по умолчанию: `60`).
- `ACTION_INTERVAL`: Интервал ожидания перед выполнением действий над контейнерами в секундах (по умолчанию: `5`).

## API

### Получить текущее состояние контейнеров

- **URL:** `/api/v1/getRunningContainers`
- **Метод:** `GET`
- **Описание:** Возвращает текущее состояние всех контейнеров, управляемых сервисом.
- **Пример ответа:**
    ```json
    [
        {
            "container_name": "web_server",
            "description": "A web server container",
            "compose_file": "web_server_compose.yml",
            "status": "enabled",
            "current_status": "running"
        },
        {
            "container_name": "database",
            "description": "A database container",
            "compose_file": "database_compose.yml",
            "status": "enabled",
            "current_status": "running"
        },
        {
            "container_name": "cache",
            "description": "A cache container",
            "compose_file": "cache_compose.yml",
            "status": "enabled",
            "current_status": "running"
        }
    ]
    ```

## Автор

[https://t.me/netvirus](https://t.me/netvirus)
