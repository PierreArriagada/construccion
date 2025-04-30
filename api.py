from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
from uuid import uuid4
import sqlite3
import os
from pathlib import Path
import traceback # Añadido para imprimir errores completos

# Configuración de la base de datos
DB_PATH = "bd.sqlite3"
DB_TABLE_NAME = "productions" # Nombre de la tabla que se va a crear

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"--- LIFESPAN: Inicializando DB (tabla: {DB_TABLE_NAME})...")
    inicializar_db() # Llama a la función que crea/verifica la tabla
    print(f"--- LIFESPAN: DB lista en: {os.path.abspath(DB_PATH)}")
    yield
    print("--- LIFESPAN: Aplicación finalizando...")

# --- Instancia de FastAPI ---
app = FastAPI(
    title=f"API de {DB_TABLE_NAME.capitalize()} con bd.sqlite3",
    lifespan=lifespan
)
print("--- FastAPI app creada ---") # DEBUG para ir viendo el flujo de ejecución
print(f"--- DEBUG: DB_PATH: {os.path.abspath(DB_PATH)}") # DEBUG para ver la ruta absoluta de la DB

# --- DEBUG MIDDLEWARE (ANTES DE CORS) ---
@app.middleware("http")
async def debug_middleware_before_cors(request: Request, call_next):
    print(f"\n--- DEBUG REQ: Petición recibida para: {request.url.path}") # \n para separar logs
    print(f"--- DEBUG REQ: Método: {request.method}")
    # Intenta obtener 'origin', puede ser None si no es una petición CORS o desde el mismo origen
    origin_header = request.headers.get('origin')
    print(f"--- DEBUG REQ: Origen (Header 'origin'): {origin_header}")
    print(f"--- DEBUG REQ: Headers: {request.headers}")
    try:
        response = await call_next(request)
        print(f"--- DEBUG RSP: Status Code Respuesta (antes de enviar): {response.status_code}")
        # Imprime encabezados de la respuesta ANTES de que CORS los modifique
        print(f"--- DEBUG RSP: Headers Respuesta (antes de CORS): {response.headers}")
        return response
    except Exception as e:
        print(f"--- DEBUG EXC: EXCEPCIÓN antes de generar respuesta en middleware: {e}")
        traceback.print_exc() # Imprime el traceback completo del error
        # Es importante re-lanzar la excepción para que FastAPI la maneje
        # o devolver una respuesta de error explícita aquí.
        # Devolveremos un 500 genérico si una excepción llega hasta aquí.
        # Nota: Si la excepción ocurre DENTRO de call_next, FastAPI podría manejarla
        # antes de que este bloque catch la vea, dependiendo de dónde ocurra.
        # Por seguridad, lanzamos HTTPException para asegurarnos de que se maneje.
        raise HTTPException(status_code=500, detail=f"Internal server error intercepted by debug middleware: {e}")


# --- CORS Middleware (CON ORÍGENES ESPECÍFICOS) ---
print("--- Adding CORS Middleware ---")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000", # Origen desde donde se ejecuta el HTML
        "http://localhost:8000"  # Origen donde corre la API, revisar los puertos
    ],
    allow_credentials=True, # Cambiar a False si no necesitas cookies/auth headers
    allow_methods=["*"],    # Permite todos los métodos comunes
    allow_headers=["*"],    # Permite todas las cabeceras comunes
)
print("--- CORS Middleware Added ---")

# --- Modelos Pydantic ---
class Production(BaseModel): 
    id: str
    nombre: str
    precio: float
    imagen_url: str
    cantidad_comentarios: int

class ProductionCreate(BaseModel): 
    nombre: str
    precio: float
    imagen_url: str
    cantidad_comentarios: int = 0

# --- Funciones de Base de Datos ---
def get_db_connection():
    print("--- DEBUG DB: Creando conexión DB ---") # DEBUG para ver el flujo de ejecución
    # Verifica si la carpeta de la base de datos existe, si no, la crea
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    """Inicializa la tabla 'productions' si no existe"""
    if not os.path.exists(DB_PATH):
        print(f"--- DEBUG DB: Creando nueva base de datos: {DB_PATH}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Crear tabla con el nombre DB_TABLE_productions y todas sus columnas
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
        id TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        imagen_url TEXT NOT NULL,
        cantidad_comentarios INTEGER NOT NULL DEFAULT 0
    )
    ''')

    # Verificar si la tabla 'productions' está vacía
    cursor.execute(f'SELECT COUNT(*) FROM {DB_TABLE_NAME}')
    count = cursor.fetchone()[0]

    if count == 0:
        print(f"--- DEBUG DB: Insertando datos de ejemplo en la tabla {DB_TABLE_NAME}...")
        initial_productions = [
            {"id": str(uuid4()), "nombre": "Interior 1", "precio": 3, "imagen_url": "https://st1.uvnimg.com/dims4/default/6c3aded/2147483647/thumbnail/400x225/quality/75/?url=https%3A%2F%2Fuvn-brightspot.s3.amazonaws.com%2Fassets%2Fvixes%2Fimj%2Fhogartotal%2Ff%2Ffotos-de-interiores-13.jpg", "cantidad_comentarios": 42},
            {"id": str(uuid4()), "nombre": "Interior 2", "precio": 4, "imagen_url": "https://st1.uvnimg.com/dims4/default/1a62793/2147483647/thumbnail/400x225/quality/75/?url=https%3A%2F%2Fuvn-brightspot.s3.amazonaws.com%2Fassets%2Fvixes%2Fimj%2Fhogartotal%2Ff%2Ffotos-de-interiores.jpg","cantidad_comentarios": 28},
            {"id": str(uuid4()), "nombre": "Interior 3", "precio": 7, "imagen_url": "https://st1.uvnimg.com/dims4/default/8f7014d/2147483647/thumbnail/400x225/quality/75/?url=https%3A%2F%2Fuvn-brightspot.s3.amazonaws.com%2Fassets%2Fvixes%2Fimj%2Fhogartotal%2Ff%2Ffotos-de-interiores-2.jpg", "cantidad_comentarios": 87}
        ]
        try:
            cursor.executemany(
                f'INSERT INTO {DB_TABLE_NAME} (id, nombre, precio, imagen_url, cantidad_comentarios) VALUES (?, ?, ?, ?, ?)',
                [(p["id"], p["nombre"], p["precio"], p["imagen_url"], p["cantidad_comentarios"]) for p in initial_productions]
            )
            conn.commit()
            print("--- DEBUG DB: Datos de ejemplo insertados correctamente")
        except sqlite3.Error as e:
            print(f"--- DEBUG DB: ERROR al insertar datos de ejemplo: {e}")
            conn.rollback()
    else:
         print(f"--- DEBUG DB: La tabla {DB_TABLE_NAME} ya contiene datos ({count} registros).")

    conn.close()

# --- Endpoints ---
@app.get(f"/{DB_TABLE_NAME}", response_model=List[Production])
async def get_productions():
    print(f"--- DEBUG ENDPOINT: Entrando a get_productions para /{DB_TABLE_NAME}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {DB_TABLE_NAME}')
        productions_db = cursor.fetchall()
        print(f"--- DEBUG ENDPOINT: Se obtuvieron {len(productions_db)} registros de la DB")
        # Convertir filas a diccionarios si row_factory no lo hizo (aunque debería)
        # y luego validar con Pydantic
        results = [Production(**dict(item)) for item in productions_db]
        print(f"--- DEBUG ENDPOINT: Devolviendo {len(results)} registros desde get_productions")
        return results
    except Exception as e:
        print(f"--- DEBUG ENDPOINT: *** ERROR DENTRO DE get_productions ***: {e}")
        traceback.print_exc() # Imprime el traceback completo del error
        # Lanza HTTPException para que FastAPI devuelva un error 500 JSON
        raise HTTPException(status_code=500, detail=f"Error interno del servidor en get_productions: {e}")
    finally:
        if conn:
            conn.close()
            # print("--- DEBUG ENDPOINT: Conexión DB cerrada en get_productions")


# --- Otros Endpoints (get_production, create, update, delete) ---
# (Mantenidos de la versión anterior, sin prints de depuración detallados por ahora)

@app.get(f"/{DB_TABLE_NAME}/{{production_id}}", response_model=Production)
async def get_production(production_id: str):
    print(f"--- DEBUG ENDPOINT: Entrando a get_production para ID: {production_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {DB_TABLE_NAME} WHERE id = ?', (production_id,))
    production_db = cursor.fetchone()
    conn.close()
    if production_db is None:
        raise HTTPException(status_code=404, detail="Production item not found")
    return Production(**dict(production_db))

@app.post(f"/{DB_TABLE_NAME}", response_model=Production, status_code=201)
async def create_production(production_data: ProductionCreate):
    print(f"--- DEBUG ENDPOINT: Entrando a create_production")
    nuevo_id = str(uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f'INSERT INTO {DB_TABLE_NAME} (id, nombre, precio, imagen_url, cantidad_comentarios) VALUES (?, ?, ?, ?, ?)',
            (nuevo_id, production_data.nombre, production_data.precio, production_data.imagen_url, production_data.cantidad_comentarios)
        )
        conn.commit()
        print(f"--- DEBUG ENDPOINT: Production creada con ID: {nuevo_id}")
    except sqlite3.Error as e:
        print(f"--- DEBUG ENDPOINT: *** ERROR DENTRO DE create_production (DB) ***: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during creation: {e}")
    except Exception as e:
        print(f"--- DEBUG ENDPOINT: *** ERROR DENTRO DE create_production ***: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error during creation: {e}")
    finally:
        conn.close()
    return Production(id=nuevo_id, **production_data.dict())

@app.put(f"/{DB_TABLE_NAME}/{{production_id}}", response_model=Production)
async def update_production(production_id: str, production_update: ProductionCreate):
    print(f"--- DEBUG ENDPOINT: Entrando a update_production para ID: {production_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {DB_TABLE_NAME} WHERE id = ?', (production_id,))
    existing_production = cursor.fetchone()
    if existing_production is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Production item not found")
    try:
        cursor.execute(
            f'UPDATE {DB_TABLE_NAME} SET nombre = ?, precio = ?, imagen_url = ?, cantidad_comentarios = ? WHERE id = ?',
            (production_update.nombre, production_update.precio, production_update.imagen_url, production_update.cantidad_comentarios, production_id)
        )
        conn.commit()
        print(f"--- DEBUG ENDPOINT: Production actualizada con ID: {production_id}")
    except sqlite3.Error as e:
        print(f"--- DEBUG ENDPOINT: *** ERROR DENTRO DE update_production (DB) ***: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during update: {e}")
    except Exception as e:
        print(f"--- DEBUG ENDPOINT: *** ERROR DENTRO DE update_production ***: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error during update: {e}")
    finally:
        conn.close()
    return Production(id=production_id, **production_update.dict())

@app.delete(f"/{DB_TABLE_NAME}/{{production_id}}", status_code=204)
async def delete_production(production_id: str):
    print(f"--- DEBUG ENDPOINT: Entrando a delete_production para ID: {production_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {DB_TABLE_NAME} WHERE id = ?', (production_id,))
    existing_production = cursor.fetchone()
    if existing_production is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Production item not found")
    try:
        cursor.execute(f'DELETE FROM {DB_TABLE_NAME} WHERE id = ?', (production_id,))
        conn.commit()
        print(f"--- DEBUG ENDPOINT: Production eliminada con ID: {production_id}")
    except sqlite3.Error as e:
        print(f"--- DEBUG ENDPOINT: *** ERROR DENTRO DE delete_production (DB) ***: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during deletion: {e}")
    except Exception as e:
        print(f"--- DEBUG ENDPOINT: *** ERROR DENTRO DE delete_production ***: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error during deletion: {e}")
    finally:
        conn.close()
    return None

# --- Bloque para ejecutar Uvicorn ---
if __name__ == "__main__":
    print("--- Starting Uvicorn ---")
    # Usamos "api:app" porque el archivo es api.py y la instancia FastAPI se llama app
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)