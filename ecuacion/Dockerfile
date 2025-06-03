FROM python:3.12-slim AS base

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /microservicios
COPY requirements.txt .
# Upgrade pip and setuptools before installing requirements
RUN pip install --upgrade pip setuptools && pip install --no-cache-dir -r requirements.txt

COPY multiplica.py .

CMD ["uvicorn", "multiplica:app", "--host", "0.0.0.0", "--port", "8000"]
