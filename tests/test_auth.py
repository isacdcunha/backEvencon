from app.criar_admin import EMAIL_ADMIN
from tests.conftest import SENHA_ADMIN
from tests.test_api import EVENTO, LUGAR

CONTA = {"nome": " Isa Cunha ", "email": "Isa@Email.com", "senha": "Senha123"}


def cabecalho(resposta):
    return {"Authorization": f"Bearer {resposta.json()['token']}"}


def test_cadastro_login_e_sessao(visitante):
    cadastro = visitante.post("/auth/cadastro", json=CONTA)
    assert cadastro.status_code == 201
    assert cadastro.json()["usuario"] == {
        "id": cadastro.json()["usuario"]["id"],
        "nome": "Isa Cunha",
        "email": "isa@email.com",
        "interesses": [],
        "admin": False,
    }

    assert visitante.post("/auth/cadastro", json=CONTA).status_code == 409
    assert visitante.post("/auth/cadastro", json={**CONTA, "email": "a@b.co", "senha": "curta"}).status_code == 422

    errado = visitante.post("/auth/login", json={"email": "isa@email.com", "senha": "outra-senha"})
    assert errado.status_code == 401
    assert errado.json()["detail"] == "E-mail ou senha incorretos."

    login = visitante.post("/auth/login", json={"email": "ISA@email.com", "senha": "Senha123"})
    assert visitante.get("/auth/eu", headers=cabecalho(login)).json()["nome"] == "Isa Cunha"

    assert visitante.get("/auth/eu").status_code == 401
    assert visitante.get("/auth/eu", headers={"Authorization": "Bearer inventado"}).status_code == 401


def test_interesses_ficam_salvos_na_conta(visitante):
    conta = cabecalho(visitante.post("/auth/cadastro", json=CONTA))
    resposta = visitante.put("/auth/eu/interesses", json={"interesses": ["Música", "Dança"]}, headers=conta)
    assert resposta.json()["interesses"] == ["Música", "Dança"]
    assert visitante.get("/auth/eu", headers=conta).json()["interesses"] == ["Música", "Dança"]


def test_sair_invalida_so_aquele_login(visitante):
    primeiro = cabecalho(visitante.post("/auth/cadastro", json=CONTA))
    segundo = cabecalho(visitante.post("/auth/login", json={"email": CONTA["email"], "senha": CONTA["senha"]}))

    assert visitante.post("/auth/sair", headers=primeiro).status_code == 204
    assert visitante.get("/auth/eu", headers=primeiro).status_code == 401
    assert visitante.get("/auth/eu", headers=segundo).status_code == 200


def test_a_senha_nao_fica_guardada_em_texto(visitante):
    from sqlalchemy import select

    from app import modelos
    from app.banco import CriarSessao

    resposta = visitante.post("/auth/cadastro", json=CONTA)
    with CriarSessao() as sessao:
        usuario = sessao.scalar(select(modelos.Usuario).where(modelos.Usuario.email == "isa@email.com"))
        login = sessao.scalars(select(modelos.Sessao)).one()
    assert "Senha123" not in usuario.senha_hash
    assert login.token_hash != resposta.json()["token"]


def test_so_a_administracao_cria_e_apaga(visitante):
    admin = cabecalho(visitante.post("/auth/login", json={"email": EMAIL_ADMIN, "senha": SENHA_ADMIN}))
    comum = cabecalho(visitante.post("/auth/cadastro", json=CONTA))
    assert visitante.get("/auth/eu", headers=admin).json()["admin"] is True

    for caminho, corpo in [("/eventos", EVENTO), ("/eventos/lote", [EVENTO]), ("/lugares", LUGAR), ("/lugares/lote", [LUGAR])]:
        assert visitante.post(caminho, json=corpo).status_code == 401
        assert visitante.post(caminho, json=corpo, headers=comum).status_code == 403

    evento = visitante.post("/eventos", json=EVENTO, headers=admin)
    assert evento.status_code == 201
    id = evento.json()["id"]

    assert visitante.delete(f"/eventos/{id}").status_code == 401
    assert visitante.delete(f"/eventos/{id}", headers=comum).status_code == 403
    assert visitante.get(f"/eventos/{id}").status_code == 200

    assert visitante.delete(f"/eventos/{id}", headers=admin).status_code == 204
    assert visitante.get(f"/eventos/{id}").status_code == 404
    assert visitante.delete(f"/eventos/{id}", headers=admin).status_code == 404


def test_apagar_evento_leva_junto_a_ligacao_com_os_lugares(api):
    lugar = api.post("/lugares", json=LUGAR).json()
    evento = api.post("/eventos", json={**EVENTO, "lugaresProximos": [{"lugarId": lugar["id"], "distanciaKm": 0.4}]}).json()

    assert api.delete(f"/eventos/{evento['id']}").status_code == 204
    assert [item["nome"] for item in api.get("/lugares").json()] == [LUGAR["nome"]]


def test_a_carga_preserva_as_contas(api):
    from app.carga import carregar

    api.post("/auth/cadastro", json=CONTA)
    carregar()
    carregar(recriar=True)
    assert api.post("/auth/login", json={"email": CONTA["email"], "senha": CONTA["senha"]}).status_code == 200
    assert api.get("/auth/eu").json()["admin"] is True
