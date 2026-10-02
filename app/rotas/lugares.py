from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import esquemas, modelos
from app.banco import obter_sessao

rotas = APIRouter(prefix="/lugares", tags=["Lugares"])


def criar_lugares(sessao: Session, dados: list[esquemas.LugarEntrada]) -> list[modelos.Lugar]:
    nomes = [item.nome for item in dados]
    repetidos = set(sessao.scalars(select(modelos.Lugar.nome).where(modelos.Lugar.nome.in_(nomes))))
    repetidos |= {nome for nome in nomes if nomes.count(nome) > 1}
    if repetidos:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Já existe lugar com este nome: {', '.join(sorted(repetidos))}.",
        )

    lugares = [modelos.Lugar(**item.model_dump()) for item in dados]
    sessao.add_all(lugares)
    sessao.commit()
    return lugares


@rotas.get("", response_model=list[esquemas.Lugar])
def listar_lugares(sessao: Session = Depends(obter_sessao)):
    return sessao.scalars(select(modelos.Lugar).order_by(modelos.Lugar.nome)).all()


@rotas.post("", response_model=esquemas.Lugar, status_code=status.HTTP_201_CREATED)
def criar_lugar(dados: esquemas.LugarEntrada, sessao: Session = Depends(obter_sessao)):
    return criar_lugares(sessao, [dados])[0]


@rotas.post("/lote", response_model=list[esquemas.Lugar], status_code=status.HTTP_201_CREATED)
def criar_lugares_em_lote(
    dados: list[esquemas.LugarEntrada], sessao: Session = Depends(obter_sessao)
):
    """Insere vários lugares de uma vez. Se um falhar, nenhum é salvo."""
    return criar_lugares(sessao, dados)
