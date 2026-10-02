"""Textos de data em português, como o front-end exibe."""

from datetime import datetime

DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]  # fmt: skip


def _hora(inicio: datetime) -> str:
    return f"{inicio.hour}h{inicio.minute:02d}" if inicio.minute else f"{inicio.hour}h"


def data_curta(inicio: datetime) -> str:
    """Ex.: 'Sáb 3 out · 20h30'"""
    dia = DIAS[inicio.weekday()][:3].capitalize()
    mes = MESES[inicio.month - 1][:3]
    return f"{dia} {inicio.day} {mes} · {_hora(inicio)}"


def data_completa(inicio: datetime) -> str:
    """Ex.: 'Sábado, 3 de outubro · 20h30'"""
    dia = DIAS[inicio.weekday()].capitalize()
    if inicio.weekday() < 5:
        dia += "-feira"
    return f"{dia}, {inicio.day} de {MESES[inicio.month - 1]} · {_hora(inicio)}"
