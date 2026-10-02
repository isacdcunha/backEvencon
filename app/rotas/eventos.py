from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import datas, esquemas, modelos
from app.banco import obter_sessao

rotas = APIRouter(prefix="/eventos", tags=["Eventos"])


def buscar_ou_404(sessao: Session, id: int) -> modelos.Evento:
    evento = sessao.get(modelos.Evento, id)
    if not evento:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evento não encontrado.")
    return evento


def criar_eventos(sessao: Session, dados: list[esquemas.EventoEntrada]) -> list[modelos.Evento]:
    ids_lugares = {proximo.lugar_id for item in dados for proximo in item.lugares_proximos}
    existentes = set(
        sessao.scalars(select(modelos.Lugar.id).where(modelos.Lugar.id.in_(ids_lugares)))
    )
    faltando = ids_lugares - existentes
    if faltando:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"Lugar não encontrado: {', '.join(str(id) for id in sorted(faltando))}.",
        )

    eventos = []
    for item in dados:
        campos = item.model_dump(exclude={"lugares_proximos"})
        campos["data"] = item.data or datas.data_curta(item.inicio)
        campos["data_completa"] = item.data_completa or datas.data_completa(item.inicio)
        # o mesmo lugar repetido na lista conta uma vez só
        proximos = {proximo.lugar_id: proximo.distancia_km for proximo in item.lugares_proximos}
        eventos.append(
            modelos.Evento(
                **campos,
                lugares=[
                    modelos.EventoLugar(lugar_id=lugar_id, distancia_km=distancia)
                    for lugar_id, distancia in proximos.items()
                ],
            )
        )

    sessao.add_all(eventos)
    sessao.commit()
    return eventos


@rotas.get("", response_model=list[esquemas.EventoResumo])
def listar_eventos(sessao: Session = Depends(obter_sessao)):
    return sessao.scalars(select(modelos.Evento).order_by(modelos.Evento.inicio)).all()


@rotas.get("/{id}", response_model=esquemas.EventoDetalhe)
def buscar_evento(id: int, sessao: Session = Depends(obter_sessao)):
    return esquemas.EventoDetalhe.de_modelo(buscar_ou_404(sessao, id))


@rotas.get("/{id}/semelhantes", response_model=list[esquemas.EventoResumo])
def buscar_semelhantes(
    id: int, limite: int = Query(3, ge=1, le=20), sessao: Session = Depends(obter_sessao)
):
    """Outros eventos, começando pelos que têm mais categorias em comum."""
    evento = buscar_ou_404(sessao, id)
    outros = sessao.scalars(
        select(modelos.Evento).where(modelos.Evento.id != id).order_by(modelos.Evento.inicio)
    ).all()

    def em_comum(outro: modelos.Evento) -> int:
        return len(set(outro.categorias) & set(evento.categorias))

    return sorted(outros, key=em_comum, reverse=True)[:limite]


@rotas.post("", response_model=esquemas.EventoDetalhe, status_code=status.HTTP_201_CREATED)
def criar_evento(dados: esquemas.EventoEntrada, sessao: Session = Depends(obter_sessao)):
    return esquemas.EventoDetalhe.de_modelo(criar_eventos(sessao, [dados])[0])


@rotas.post(
    "/lote", response_model=list[esquemas.EventoDetalhe], status_code=status.HTTP_201_CREATED
)
def criar_eventos_em_lote(
    dados: list[esquemas.EventoEntrada], sessao: Session = Depends(obter_sessao)
):
    """Insere vários eventos de uma vez. Se um falhar, nenhum é salvo."""
    return [esquemas.EventoDetalhe.de_modelo(evento) for evento in criar_eventos(sessao, dados)]
