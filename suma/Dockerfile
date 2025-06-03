
FROM python:3.10-slim

WORKDIR /microservicios
COPY suma.py .

RUN pip install fastapi uvicorn pydantic requests

CMD ["uvicorn", "suma:app", "--host", "0.0.0.0", "--port", "8000"]
