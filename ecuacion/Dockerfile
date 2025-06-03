FROM python:3.12-slim

WORKDIR /microservicios

# Instala dependencias del sistema para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tu código
COPY multiplica.py .

# Comando para correr la app
CMD ["uvicorn", "multiplica:app", "--host", "0.0.0.0", "--port", "8000"]
