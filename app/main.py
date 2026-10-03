import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.banco import criar_tabelas
from app.rotas import auth, eventos, lugares

# Endereços do front-end que podem chamar a API, separados por vírgula.
ORIGENS = os.getenv("EVENCON_ORIGENS", "http://localhost:5173").split(",")


@asynccontextmanager
async def ao_iniciar(app: FastAPI):
    criar_tabelas()
    yield


app = FastAPI(title="Evencon API", lifespan=ao_iniciar)

app.add_middleware(CORSMiddleware, allow_origins=ORIGENS, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.rotas)
app.include_router(eventos.rotas)
app.include_router(lugares.rotas)
