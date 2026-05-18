import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from models.database import create_tables
from models.seed import seed_database
from routers import auth, agent, products, watchlist, notifications
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await seed_database()
    yield


app = FastAPI(
    title="DropAgent API",
    description="AI destekli dropshipping ürün araştırma platformu",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(agent.router)
app.include_router(products.router)
app.include_router(watchlist.router)
app.include_router(notifications.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "DropAgent API"}


# Frontend - static/index.html dosyasını ana sayfa olarak sun
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")

if __name__ == "__main__":
    import uvicorn
    print("DropAgent başlatılıyor... Tarayıcıda http://localhost:8000 adresini açabilirsiniz.")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
