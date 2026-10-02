"""Conexão com o banco de dados."""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Por padrão o banco é o arquivo evencon.db na raiz do projeto.
URL_BANCO = os.getenv("EVENCON_BANCO", "sqlite:///evencon.db")

motor = create_engine(URL_BANCO, connect_args={"check_same_thread": False})
CriarSessao = sessionmaker(bind=motor, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def criar_tabelas() -> None:
    from app import modelos  # noqa: F401  (registra as tabelas na Base)

    Base.metadata.create_all(motor)


def obter_sessao() -> Iterator[Session]:
    with CriarSessao() as sessao:
        yield sessao
