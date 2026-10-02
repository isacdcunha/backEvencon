"""Carga em massa de lugares e eventos a partir dos arquivos em dados/.

    python -m app.carga             insere o que está em dados/
    python -m app.carga --recriar   apaga tudo antes de inserir

Nos eventos, cada lugar próximo é indicado pelo nome:
    "lugaresProximos": [{ "lugar": "Pátio América", "distanciaKm": 0.4 }]
"""

import json
import sys
from pathlib import Path

from sqlalchemy import func, select

from app import esquemas, modelos
from app.banco import Base, CriarSessao, criar_tabelas, motor
from app.rotas.eventos import criar_eventos
from app.rotas.lugares import criar_lugares

PASTA_DADOS = Path(__file__).parent.parent / "dados"


def ler(arquivo: str) -> list[dict]:
    return json.loads((PASTA_DADOS / arquivo).read_text(encoding="utf-8"))


def carregar(recriar: bool = False) -> tuple[int, int]:
    if recriar:
        Base.metadata.drop_all(motor)
    criar_tabelas()

    with CriarSessao() as sessao:
        if sessao.scalar(select(func.count()).select_from(modelos.Evento)):
            raise SystemExit("O banco já tem eventos. Use --recriar para apagar e carregar de novo.")

        # lugares que já existem no banco são mantidos; só os novos são inseridos
        ja_existem = set(sessao.scalars(select(modelos.Lugar.nome)))
        novos = [
            esquemas.LugarEntrada.model_validate(item)
            for item in ler("lugares.json")
            if item["nome"] not in ja_existem
        ]
        criar_lugares(sessao, novos)
        id_por_nome = {lugar.nome: lugar.id for lugar in sessao.scalars(select(modelos.Lugar))}

        eventos = []
        for item in ler("eventos.json"):
            proximos = []
            for proximo in item.get("lugaresProximos", []):
                if proximo["lugar"] not in id_por_nome:
                    raise SystemExit(
                        f"Evento '{item['titulo']}': lugar '{proximo['lugar']}' "
                        "não está em lugares.json."
                    )
                proximos.append(
                    {"lugarId": id_por_nome[proximo["lugar"]], "distanciaKm": proximo["distanciaKm"]}
                )
            eventos.append(esquemas.EventoEntrada.model_validate({**item, "lugaresProximos": proximos}))

        criar_eventos(sessao, eventos)
        return len(novos), len(eventos)


if __name__ == "__main__":
    lugares, eventos = carregar(recriar="--recriar" in sys.argv)
    print(f"Carga concluída: {lugares} lugares e {eventos} eventos inseridos.")
