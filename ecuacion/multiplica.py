from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import psycopg2
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# PostgreSQL connection configuration
db_config = {
    'host': os.getenv('POSTGRES_HOST', 'dpg-d0vluvfdiees73f0gmsg-a'),
    'user': os.getenv('POSTGRES_USER', 'microservicesdb_nrzf_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'MhGw7Xq8cFF3CoKTYPnxoO6i5NVoiUzL'),
    'database': os.getenv('POSTGRES_DATABASE', 'microservicesdb_nrzf'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

# Service URLs
SUMA_URL = os.getenv('SUMA_URL', 'https://suma-service-z2qf.onrender.com/sumar')
RESTA_URL = os.getenv('RESTA_URL', 'https://resta-service.onrender.com/restar')

# Create database connection
def get_db_connection():
    return psycopg2.connect(**db_config)

# Create table if not exists
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            id SERIAL PRIMARY KEY,
            a FLOAT,
            b FLOAT,
            c FLOAT,
            d FLOAT,
            suma FLOAT,
            resta FLOAT,
            resultado FLOAT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

class Input(BaseModel):
    a: float
    b: float
    c: float
    d: float

@app.post("/resolver")
def resolver(valores: Input):
    try:
        # Call suma service
        logger.info(f"Calling suma service at {SUMA_URL}")
        suma_resp = requests.post(SUMA_URL, json={"a": valores.a, "b": valores.b})
        logger.info(f"Suma response status: {suma_resp.status_code}")
        logger.info(f"Suma response content: {suma_resp.text}")
        
        if suma_resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Suma service error: {suma_resp.text}")
        
        suma = suma_resp.json()["resultado"]

        # Call resta service
        logger.info(f"Calling resta service at {RESTA_URL}")
        resta_resp = requests.post(RESTA_URL, json={"c": valores.c, "d": valores.d})
        logger.info(f"Resta response status: {resta_resp.status_code}")
        logger.info(f"Resta response content: {resta_resp.text}")
        
        if resta_resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Resta service error: {resta_resp.text}")
        
        resta = resta_resp.json()["resultado"]

        resultado = suma * resta

        # Store result in PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO resultados (a, b, c, d, suma, resta, resultado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (valores.a, valores.b, valores.c, valores.d, suma, resta, resultado))
        conn.commit()
        cursor.close()
        conn.close()

        return {"resultado": resultado}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service communication error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
