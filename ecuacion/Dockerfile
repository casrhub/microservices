FROM python:3.12-slim AS base

# Update system packages and clean up
RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /microservicios
COPY requirements.txt .
# Upgrade pip and setuptools before installing requirements
RUN pip install --upgrade pip setuptools && pip install --no-cache-dir -r requirements.txt

COPY multiplica.py .

CMD ["uvicorn", "multiplica:app", "--host", "0.0.0.0", "--port", "8000"]
