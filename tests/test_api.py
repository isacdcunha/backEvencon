from app.carga import carregar, ler

LUGAR = {
    "nome": "Pátio América",
    "tipo": "Hamburgueria · Chopp",
    "faixaPreco": 2,
    "aberto": True,
    "horario": "até 0h",
    "icone": "fa-solid fa-beer-mug-empty",
    "gradiente": "linear-gradient(135deg, #fb923c, #f472b6)",
    "categoria": "Bares",
    "bairro": "América",
    "acessivel": True,
    "petFriendly": False,
    "paraFamilia": False,
}

EVENTO = {
    "titulo": "Roda de Samba do Mercado",
    "categorias": ["Música", "Roda de samba"],
    "inicio": "2026-10-03T16:00",
    "local": "Mercado Público Municipal",
    "preco": 0,
    "rotuloPreco": "entrada",
    "distanciaKm": 1.2,
    "icone": "fa-solid fa-music",
    "bairro": "Centro",
    "petFriendly": True,
    "detalheHorario": "Até as 20h",
    "endereco": "Av. Dr. Paulo Medeiros, 200 · Centro",
    "latitude": -26.3045,
    "longitude": -48.8464,
    "organizador": "Mercado Público",
    "detalheOrganizador": "Organizador",
    "sobre": "Samba ao vivo.",
    "classificacao": "L",
    "lote": "Entrada livre",
    "linkCompra": "https://exemplo.com",
    "tempoDeCarro": "5 min de carro",
}


def test_cria_e_busca_evento_com_lugar_proximo(api):
    lugar = api.post("/lugares", json=LUGAR).json()
    resposta = api.post(
        "/eventos",
        json={**EVENTO, "lugaresProximos": [{"lugarId": lugar["id"], "distanciaKm": 0.4}]},
    )
    assert resposta.status_code == 201

    evento = api.get(f"/eventos/{resposta.json()['id']}").json()
    assert evento["titulo"] == EVENTO["titulo"]
    assert evento["rotuloPreco"] == "entrada"
    assert evento["lugaresProximos"] == [{**LUGAR, "id": lugar["id"], "distanciaKm": 0.4}]


def test_monta_os_textos_de_data_quando_nao_sao_informados(api):
    evento = api.post("/eventos", json={**EVENTO, "inicio": "2026-10-02T20:30"}).json()
    assert evento["data"] == "Sex 2 out · 20h30"
    assert evento["dataCompleta"] == "Sexta-feira, 2 de outubro · 20h30"

    informado = api.post("/eventos", json={**EVENTO, "data": "Sáb 3 out · 8h às 13h"}).json()
    assert informado["data"] == "Sáb 3 out · 8h às 13h"
    assert informado["dataCompleta"] == "Sábado, 3 de outubro · 16h"


def test_lista_em_ordem_de_data_no_formato_resumido(api):
    api.post("/eventos", json={**EVENTO, "titulo": "Depois", "inicio": "2026-10-04T10:00"})
    api.post("/eventos", json={**EVENTO, "titulo": "Antes", "inicio": "2026-10-03T10:00"})

    lista = api.get("/eventos").json()
    assert [item["titulo"] for item in lista] == ["Antes", "Depois"]
    assert "sobre" not in lista[0]
    # campos usados pelos filtros do Explorar; os não informados começam como falso
    assert lista[0]["bairro"] == "Centro"
    assert (lista[0]["acessivel"], lista[0]["petFriendly"]) == (False, True)


def test_semelhantes_prioriza_categorias_em_comum(api):
    base = api.post("/eventos", json=EVENTO).json()
    api.post("/eventos", json={**EVENTO, "titulo": "Corrida", "categorias": ["Esportes"]})
    api.post("/eventos", json={**EVENTO, "titulo": "Show", "categorias": ["Música"]})

    semelhantes = api.get(f"/eventos/{base['id']}/semelhantes").json()
    assert [item["titulo"] for item in semelhantes] == ["Show", "Corrida"]


def test_lote_nao_salva_nada_se_um_evento_for_invalido(api):
    resposta = api.post("/eventos/lote", json=[EVENTO, {**EVENTO, "preco": -5}])
    assert resposta.status_code == 422
    assert api.get("/eventos").json() == []

    lugar_inexistente = {**EVENTO, "lugaresProximos": [{"lugarId": 99, "distanciaKm": 1}]}
    resposta = api.post("/eventos/lote", json=[EVENTO, lugar_inexistente])
    assert resposta.status_code == 422
    assert api.get("/eventos").json() == []

    assert api.post("/eventos/lote", json=[EVENTO, EVENTO]).status_code == 201
    assert len(api.get("/eventos").json()) == 2


def test_erros(api):
    assert api.get("/eventos/1").status_code == 404
    assert api.get("/eventos/1/semelhantes").status_code == 404

    api.post("/lugares", json=LUGAR)
    assert api.post("/lugares", json=LUGAR).status_code == 409


def test_carga_dos_arquivos_de_dados(api):
    lugares_no_arquivo = len(ler("lugares.json"))
    eventos_no_arquivo = ler("eventos.json")
    assert carregar() == (lugares_no_arquivo, len(eventos_no_arquivo))

    eventos = api.get("/eventos").json()
    assert len(eventos) == len(eventos_no_arquivo)
    assert len(api.get("/lugares").json()) == lugares_no_arquivo

    # os lugares próximos, indicados pelo nome no arquivo, chegam ligados ao evento
    feira = next(e for e in eventos if e["titulo"] == "Feira de Sábado no Mercado Público")
    detalhe = api.get(f"/eventos/{feira['id']}").json()
    assert detalhe["data"] == "Sáb 3 out · 8h às 13h"
    assert len(detalhe["lugaresProximos"]) == 3
