FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей (если нужны)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Создаем том для базы данных
VOLUME ["/app/data"]

# Запускаем бота
CMD ["python", "main.py"]
