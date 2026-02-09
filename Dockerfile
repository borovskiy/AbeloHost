FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Устанавливаем uv
RUN pip install uv

# Копируем конфиги
COPY pyproject.toml uv.lock ./

# В slim-образе зависимости для aiokafka скачаются в бинарном виде (wheels),
# поэтому компиляторы и apk/apt здесь не нужны.
RUN uv sync --frozen --no-cache

# Копируем код
COPY . .

# Запуск
CMD ["uv", "run", "python", "-m", "app.api_main"]