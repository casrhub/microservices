from fastapi import FastAPI
from pydantic import BaseModel
import requests
import mysql.connector
from datetime import datetime

app = FastAPI()

# MySQL connection configuration
db_config = {
    'host': 'mysql',
    'user': 'root',
    'password': 'root',
    'database': 'microservicios'
}

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
    suma_resp = requests.post("http://suma:8000/sumar", json={"a": valores.a, "b": valores.b})
    resta_resp = requests.post("http://resta:8000/restar", json={"c": valores.c, "d": valores.d})

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
