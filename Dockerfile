# Установим базовый образ Python
FROM python:3.9-slim

# Установим рабочую директорию
WORKDIR /app

# Скопируем requirements.txt
COPY requirements.txt .

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем все файлы проекта
COPY . .

# Укажем порт
EXPOSE 5050

# Запустим приложение
CMD ["python", "app.py"]