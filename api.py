import os
import traceback
from contextlib import asynccontextmanager
from typing import List, Optional
from uuid import uuid4
import asyncpg
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Configuración Leyendo Variables de Entorno ---
# Lee las variables de entorno que configurarás en Render
# Los valores por defecto son solo para referencia, NO DEBEN usarse en producción sin .env/Render envs
DB_USER = os.environ.get("API_DB_USER", "postgres.wlkuhjbpersxhfubomkd")
DB_PASSWORD = os.environ.get("API_DB_PASSWORD", "asPB19510")
DB_HOST = os.environ.get("API_DB_HOST", "aws-0-us-east-2.pooler.supabase.com")
DB_PORT = os.environ.get("API_DB_PORT", "6543")
DB_NAME = os.environ.get("API_DB_NAME", "postgres")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Nombre de la tabla en PostgreSQL (puede ser el mismo o diferente)
DB_TABLE_NAME = "productions_api"

# Variable global para el pool de conexiones
db_pool = None

# --- Lifespan para gestionar el pool de conexiones ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    print("--- LIFESPAN: Creando pool de conexiones PostgreSQL...")
    try:
        # Verificar si las variables de entorno esenciales están presentes
        if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
             # En un entorno real, es mejor obtener los valores directamente sin default
             # y fallar aquí si no están configurados en Render/Variables de Entorno
             print("ADVERTENCIA: Usando valores por defecto para la conexión a BD. Asegúrate de configurar las variables de entorno API_DB_* en Render.")
             # raise ValueError("Faltan variables de entorno para la conexión a la BD de la API")

        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1, # Mínimo de conexiones inactivas
            max_size=10 # Máximo de conexiones totales
        )
        print("--- LIFESPAN: Pool de conexiones creado. Inicializando DB...")
        await inicializar_db() # Llama a la versión async
        print(f"--- LIFESPAN: DB lista (Tabla: {DB_TABLE_NAME}).")
        yield # La aplicación se ejecuta aquí
    except Exception as e:
        print(f"--- LIFESPAN ERROR CRÍTICO al iniciar: {e}")
        traceback.print_exc()
        # Considera si la app debe fallar si la DB no inicia
        # raise
    finally:
        if db_pool:
            print("--- LIFESPAN: Cerrando pool de conexiones PostgreSQL...")
            await db_pool.close()
            print("--- LIFESPAN: Pool cerrado.")

# --- Instancia de FastAPI ---
app = FastAPI(
    title=f"API de {DB_TABLE_NAME.capitalize()} con PostgreSQL",
    lifespan=lifespan
)
print("--- FastAPI app creada ---")

# --- DEBUG MIDDLEWARE (Opcional, puedes quitarlo para producción limpia) ---
@app.middleware("http")
async def debug_middleware_before_cors(request: Request, call_next):
    print(f"\n--- DEBUG REQ: Petición recibida para: {request.url.path}")
    print(f"--- DEBUG REQ: Método: {request.method}")
    origin_header = request.headers.get('origin')
    print(f"--- DEBUG REQ: Origen (Header 'origin'): {origin_header}")
    try:
        response = await call_next(request)
        print(f"--- DEBUG RSP: Status Code Respuesta (antes de enviar): {response.status_code}")
        print(f"--- DEBUG RSP: Headers Respuesta (antes de CORS): {response.headers}")
        return response
    except Exception as e:
        print(f"--- DEBUG EXC: EXCEPCIÓN en middleware: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error intercepted by debug middleware: {e}")

# --- CORS Middleware ---
print("--- Adding CORS Middleware ---")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000", # Desarrollo Django local
        "http://localhost:8000",  # Desarrollo Django local
        "https://construccion-3lh4.onrender.com" # <-- Tu URL de Django en producción
        # Puedes añadir más orígenes si es necesario
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("--- CORS Middleware Added ---")

# --- Modelos Pydantic (Sin cambios) ---
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

# --- Funciones de Base de Datos (Adaptadas a asyncpg) ---

async def inicializar_db():
    """Crea la tabla si no existe usando el pool"""
    if not db_pool:
        print("--- ERROR inicializar_db: Pool no disponible.")
        return
    # Usa una conexión del pool
    async with db_pool.acquire() as connection:
        try:
            # Ejecuta el CREATE TABLE para PostgreSQL
            # Usamos REAL para precio como en SQLite, considera NUMERIC(10, 2) para dinero
            await connection.execute(f'''
            CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                imagen_url TEXT NOT NULL,
                cantidad_comentarios INTEGER NOT NULL DEFAULT 0
            )
            ''')
            print(f"--- DEBUG DB: Tabla {DB_TABLE_NAME} verificada/creada.")
            # No insertamos datos de ejemplo aquí para que sea persistente
        except Exception as e:
             print(f"--- DEBUG DB: ERROR al crear tabla {DB_TABLE_NAME}: {e}")
             traceback.print_exc()
             raise # Propagar el error es útil durante el lifespan

# --- Endpoints (Adaptados a asyncpg) ---

@app.get(f"/{DB_TABLE_NAME}", response_model=List[Production])
async def get_productions():
    print(f"--- DEBUG ENDPOINT: GET /{DB_TABLE_NAME}")
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database connection pool not available")
    try:
        async with db_pool.acquire() as connection:
            # fetch devuelve una lista de Records
            rows = await connection.fetch(f'SELECT * FROM {DB_TABLE_NAME}')
        # Convertir records a diccionarios para Pydantic
        results = [Production(**dict(row)) for row in rows]
        print(f"--- DEBUG ENDPOINT: Devolviendo {len(results)} registros.")
        return results
    except Exception as e:
        print(f"--- DEBUG ENDPOINT GET ALL ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

@app.get(f"/{DB_TABLE_NAME}/{{production_id}}", response_model=Production)
async def get_production(production_id: str):
    print(f"--- DEBUG ENDPOINT: GET /{DB_TABLE_NAME}/{production_id}")
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database connection pool not available")
    try:
        async with db_pool.acquire() as connection:
            # fetchrow devuelve un Record o None. Placeholders son $1, $2...
            row = await connection.fetchrow(
                f'SELECT * FROM {DB_TABLE_NAME} WHERE id = $1', production_id
            )
        if row is None:
            raise HTTPException(status_code=404, detail="Production item not found")
        return Production(**dict(row))
    except HTTPException:
         raise # Re-lanzar HTTPException (ej. 404)
    except Exception as e:
        print(f"--- DEBUG ENDPOINT GET ONE ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching item: {e}")

@app.post(f"/{DB_TABLE_NAME}", response_model=Production, status_code=201)
async def create_production(production_data: ProductionCreate):
    print(f"--- DEBUG ENDPOINT: POST /{DB_TABLE_NAME}")
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database connection pool not available")

    nuevo_id = str(uuid4())
    query = f'''
        INSERT INTO {DB_TABLE_NAME} (id, nombre, precio, imagen_url, cantidad_comentarios)
        VALUES ($1, $2, $3, $4, $5)
    '''
    try:
        async with db_pool.acquire() as connection:
            # execute no devuelve filas, solo el status (ej. "INSERT 0 1")
            await connection.execute(
                query,
                nuevo_id,
                production_data.nombre,
                production_data.precio,
                production_data.imagen_url,
                production_data.cantidad_comentarios
            )
        print(f"--- DEBUG ENDPOINT: Production creada con ID: {nuevo_id}")
        # Devolvemos el objeto completo como lo creamos
        return Production(id=nuevo_id, **production_data.dict())
    except Exception as e:
        print(f"--- DEBUG ENDPOINT POST ERROR: {e}")
        traceback.print_exc()
        # Podrías verificar errores específicos de PG aquí (ej. violación de constraint)
        raise HTTPException(status_code=500, detail=f"Error creating item: {e}")

@app.put(f"/{DB_TABLE_NAME}/{{production_id}}", response_model=Production)
async def update_production(production_id: str, production_update: ProductionCreate):
    print(f"--- DEBUG ENDPOINT: PUT /{DB_TABLE_NAME}/{production_id}")
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database connection pool not available")

    # Verificar si existe primero (más robusto que confiar en RETURNING para 404)
    async with db_pool.acquire() as connection:
        exists = await connection.fetchval(f'SELECT 1 FROM {DB_TABLE_NAME} WHERE id = $1', production_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Production item not found")

    # Si existe, intentar actualizar
    query = f'''
        UPDATE {DB_TABLE_NAME}
        SET nombre = $1, precio = $2, imagen_url = $3, cantidad_comentarios = $4
        WHERE id = $5
    '''
    try:
        async with db_pool.acquire() as connection:
            await connection.execute(
                query,
                production_update.nombre,
                production_update.precio,
                production_update.imagen_url,
                production_update.cantidad_comentarios,
                production_id
            )
        print(f"--- DEBUG ENDPOINT: Production actualizada con ID: {production_id}")
        # Devolvemos el objeto actualizado como lo recibiríamos
        return Production(id=production_id, **production_update.dict())
    except HTTPException:
         raise # Re-lanzar 404 si se lanzó arriba
    except Exception as e:
        print(f"--- DEBUG ENDPOINT PUT ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating item: {e}")

@app.delete(f"/{DB_TABLE_NAME}/{{production_id}}", status_code=204)
async def delete_production(production_id: str):
    print(f"--- DEBUG ENDPOINT: DELETE /{DB_TABLE_NAME}/{production_id}")
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database connection pool not available")

    # Verificar si existe primero
    async with db_pool.acquire() as connection:
         exists = await connection.fetchval(f'SELECT 1 FROM {DB_TABLE_NAME} WHERE id = $1', production_id)
         if not exists:
              raise HTTPException(status_code=404, detail="Production item not found")

    # Si existe, intentar borrar
    query = f'DELETE FROM {DB_TABLE_NAME} WHERE id = $1'
    try:
        async with db_pool.acquire() as connection:
            await connection.execute(query, production_id)
        print(f"--- DEBUG ENDPOINT: Production eliminada con ID: {production_id}")
        # Para 204 No Content, no se devuelve cuerpo
        return None
    except HTTPException:
         raise # Re-lanzar 404
    except Exception as e:
        print(f"--- DEBUG ENDPOINT DELETE ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting item: {e}")

# --- Bloque para ejecutar Uvicorn (Modificado para Render) ---
if __name__ == "__main__":
    # Lee el puerto de la variable de entorno PORT que Render proporciona.
    # Usa 8001 como valor por defecto si PORT no está definida (útil para desarrollo local).
    port = int(os.environ.get("PORT", 8001))
    print(f"--- Starting Uvicorn on host 0.0.0.0 port {port} ---")
    # reload=False es importante para producción. Render maneja los reinicios.
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)