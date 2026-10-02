import os
import tempfile

# Os testes usam um banco próprio, separado do evencon.db de desenvolvimento.
# Precisa ser definido antes de importar o app.
os.environ["EVENCON_BANCO"] = f"sqlite:///{tempfile.mkdtemp()}/teste.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.banco import Base, criar_tabelas, motor  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def api():
    Base.metadata.drop_all(motor)
    criar_tabelas()
    with TestClient(app) as cliente:
        yield cliente
