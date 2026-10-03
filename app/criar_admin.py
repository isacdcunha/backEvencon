"""Cria a conta de administração, ou redefine a senha dela se já existir.

    python -m app.criar_admin

A senha vem da variável EVENCON_SENHA_ADMIN. Sem ela, uma senha aleatória é
gerada e mostrada uma única vez no terminal.
"""

import os
import secrets

from sqlalchemy import select

from app import modelos, seguranca
from app.banco import CriarSessao, criar_tabelas

EMAIL_ADMIN = os.getenv("EVENCON_EMAIL_ADMIN", "admin@gmail.com.br")


def criar_admin(senha: str, email: str = EMAIL_ADMIN) -> bool:
    """Devolve True se a conta foi criada e False se já existia e só a senha mudou."""
    criar_tabelas()
    with CriarSessao() as sessao:
        usuario = sessao.scalar(select(modelos.Usuario).where(modelos.Usuario.email == email))
        nova = usuario is None
        if usuario is None:
            usuario = modelos.Usuario(nome="Administradora", email=email, interesses=[])
            sessao.add(usuario)
        usuario.senha_hash = seguranca.gerar_hash_senha(senha)
        usuario.admin = True
        sessao.commit()
        return nova


if __name__ == "__main__":
    senha = os.getenv("EVENCON_SENHA_ADMIN")
    gerada = senha is None
    senha = senha or secrets.token_urlsafe(9)
    if len(senha) < 8:
        raise SystemExit("A senha precisa ter pelo menos 8 caracteres.")

    nova = criar_admin(senha)
    print(f"Conta {EMAIL_ADMIN} {'criada' if nova else 'atualizada'}.")
    if gerada:
        print(f"Senha gerada: {senha}")
        print("Guarde essa senha: ela não é mostrada de novo.")
