import os
import tempfile

# Os testes usam um banco próprio, separado do evencon.db de desenvolvimento.
# Precisa ser definido antes de importar o app.
os.environ["EVENCON_BANCO"] = f"sqlite:///{tempfile.mkdtemp()}/teste.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.banco import Base, criar_tabelas, motor  # noqa: E402
from app.criar_admin import EMAIL_ADMIN, criar_admin  # noqa: E402
from app.main import app  # noqa: E402

SENHA_ADMIN = "senha-de-teste"


@pytest.fixture
def visitante():
    """Cliente sem login, com o banco zerado e só a conta de administração criada."""
    Base.metadata.drop_all(motor)
    criar_tabelas()
    criar_admin(SENHA_ADMIN)
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def api(visitante):
    """Cliente já logado como administração, para os testes que criam eventos e lugares."""
    login = visitante.post("/auth/login", json={"email": EMAIL_ADMIN, "senha": SENHA_ADMIN})
    visitante.headers["Authorization"] = f"Bearer {login.json()['token']}"
    return visitante
