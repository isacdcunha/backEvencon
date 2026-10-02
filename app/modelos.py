"""Tabelas do banco."""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.banco import Base


class Lugar(Base):
    __tablename__ = "lugares"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    tipo: Mapped[str]
    faixa_preco: Mapped[int]
    aberto: Mapped[bool]
    horario: Mapped[str]
    icone: Mapped[str]
    gradiente: Mapped[str]
    categoria: Mapped[str]
    bairro: Mapped[str]
    acessivel: Mapped[bool]
    pet_friendly: Mapped[bool]
    para_familia: Mapped[bool]


class EventoLugar(Base):
    """Liga um evento a um lugar próximo, com a distância entre os dois."""

    __tablename__ = "evento_lugar"

    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), primary_key=True)
    lugar_id: Mapped[int] = mapped_column(ForeignKey("lugares.id"), primary_key=True)
    distancia_km: Mapped[float]

    lugar: Mapped[Lugar] = relationship(lazy="joined")


class Evento(Base):
    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str]
    categorias: Mapped[list[str]] = mapped_column(JSON)
    data: Mapped[str]
    inicio: Mapped[datetime] = mapped_column(index=True)
    local: Mapped[str]
    preco: Mapped[float]
    rotulo_preco: Mapped[str]
    distancia_km: Mapped[float]
    icone: Mapped[str]
    destaque: Mapped[str | None]
    bairro: Mapped[str]
    acessivel: Mapped[bool]
    pet_friendly: Mapped[bool]
    para_familia: Mapped[bool]

    data_completa: Mapped[str]
    detalhe_horario: Mapped[str]
    endereco: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    organizador: Mapped[str]
    detalhe_organizador: Mapped[str]
    interessados: Mapped[int]
    amigas_interessadas: Mapped[list[str]] = mapped_column(JSON)
    sobre: Mapped[str]
    tags: Mapped[list[str]] = mapped_column(JSON)
    informacoes: Mapped[list[dict[str, str]]] = mapped_column(JSON)
    classificacao: Mapped[str]
    lote: Mapped[str]
    link_compra: Mapped[str]
    tempo_de_carro: Mapped[str]

    lugares: Mapped[list[EventoLugar]] = relationship(
        cascade="all, delete-orphan", order_by=EventoLugar.distancia_km
    )
