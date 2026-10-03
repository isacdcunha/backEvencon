"""Formato dos dados que entram e saem da API.

O JSON usa camelCase (rotuloPreco, distanciaKm...), igual aos tipos do front-end.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app import modelos


class Esquema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


# ---------- Contas ----------


class CadastroEntrada(Esquema):
    nome: str = Field(min_length=1, max_length=80)
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", max_length=254)
    senha: str = Field(min_length=8, max_length=200)


class LoginEntrada(Esquema):
    email: str
    senha: str


class InteressesEntrada(Esquema):
    interesses: list[str] = Field(max_length=30)


class Usuario(Esquema):
    id: int
    nome: str
    email: str
    interesses: list[str]
    admin: bool


class SessaoAberta(Esquema):
    token: str
    usuario: Usuario


# ---------- Lugares ----------


class LugarEntrada(Esquema):
    nome: str = Field(min_length=1)
    tipo: str
    faixa_preco: int = Field(ge=1, le=4)
    aberto: bool
    horario: str
    icone: str
    gradiente: str
    categoria: str
    bairro: str
    acessivel: bool = False
    pet_friendly: bool = False
    para_familia: bool = False


class Lugar(LugarEntrada):
    id: int


class LugarProximo(Lugar):
    distancia_km: float


class LugarProximoEntrada(Esquema):
    lugar_id: int
    distancia_km: float = Field(ge=0)


# ---------- Eventos ----------


class InfoEvento(Esquema):
    icone: str
    titulo: str
    descricao: str


class EventoBase(Esquema):
    titulo: str = Field(min_length=1)
    categorias: list[str] = Field(min_length=1)
    inicio: datetime
    local: str
    preco: float = Field(ge=0)
    rotulo_preco: str
    distancia_km: float = Field(ge=0)
    icone: str
    destaque: str | None = None
    # foto de capa: um caminho (/imgs/festival-de-danca.jpg) ou a própria imagem em data URL
    imagem: str | None = Field(default=None, max_length=600_000)
    bairro: str
    acessivel: bool = False
    pet_friendly: bool = False
    para_familia: bool = False


class EventoResumo(EventoBase):
    """O que as listagens e o card de evento usam."""

    id: int
    data: str


class EventoDetalheBase(EventoBase):
    detalhe_horario: str
    endereco: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    organizador: str
    detalhe_organizador: str
    interessados: int = Field(default=0, ge=0)
    amigas_interessadas: list[str] = []
    sobre: str
    tags: list[str] = []
    informacoes: list[InfoEvento] = []
    classificacao: str
    lote: str
    link_compra: str
    tempo_de_carro: str


class EventoEntrada(EventoDetalheBase):
    # Textos de exibição da data: se não vierem, são montados a partir de `inicio`.
    data: str | None = None
    data_completa: str | None = None
    lugares_proximos: list[LugarProximoEntrada] = []


class EventoDetalhe(EventoDetalheBase):
    id: int
    data: str
    data_completa: str
    lugares_proximos: list[LugarProximo]

    @classmethod
    def de_modelo(cls, evento: modelos.Evento) -> "EventoDetalhe":
        proximos = [
            LugarProximo.model_validate(
                {**Lugar.model_validate(item.lugar).model_dump(), "distancia_km": item.distancia_km}
            )
            for item in evento.lugares
        ]
        campos = {
            nome: getattr(evento, nome)
            for nome in cls.model_fields
            if nome != "lugares_proximos"
        }
        return cls.model_validate({**campos, "lugares_proximos": proximos})
