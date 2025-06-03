from fastapi import FastAPI
from pydantic import BaseModel
import requests
import mysql.connector
from datetime import datetime
import os

app = FastAPI()

# MySQL connection configuration
db_config = {
    'host': os.getenv('MYSQL_HOST', 'mysql'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'database': os.getenv('MYSQL_DATABASE', 'microservicios')
}

# Service URLs
SUMA_URL = os.getenv('SUMA_URL', 'https://suma-service-z2qf.onrender.com/sumar')
RESTA_URL = os.getenv('RESTA_URL', 'https://resta-service.onrender.com/restar')

# Create database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Create table if not exists
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            id INT AUTO_INCREMENT PRIMARY KEY,
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
    # Call suma service
    suma_resp = requests.post(SUMA_URL, json={"a": valores.a, "b": valores.b})
    # Call resta service
    resta_resp = requests.post(RESTA_URL, json={"c": valores.c, "d": valores.d})

    suma = suma_resp.json()["resultado"]
    resta = resta_resp.json()["resultado"]

    resultado = suma * resta

    # Store result in MySQL
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
