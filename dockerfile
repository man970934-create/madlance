FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЕ файлы проекта
COPY . .

# Создаем директорию для базы данных
RUN mkdir -p /app/data

# Проверяем наличие всех необходимых файлов
RUN echo "=== Проверка файлов ===" && \
    ls -la && \
    echo "=== main.py: $(test -f main.py && echo 'OK' || echo 'MISSING') ===" && \
    echo "=== database.py: $(test -f database.py && echo 'OK' || echo 'MISSING') ===" && \
    echo "=== config.py: $(test -f config.py && echo 'OK' || echo 'MISSING') ==="

# Запуск
CMD ["python", "main.py"]
