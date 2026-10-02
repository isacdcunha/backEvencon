# Evencon — back-end

API do Evencon, feita em Python com FastAPI e banco SQLite. Por enquanto cuida de **eventos** e **lugares**; cadastro, login e salvos ainda ficam no front-end.

## Como rodar

Feito e testado com Python 3.14; versões mais antigas não foram testadas.

```bash
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m app.carga              # cria o banco e insere os eventos de dados/
uvicorn app.main:app --reload    # sobe a API em http://localhost:8000
```

Com a API no ar, **http://localhost:8000/docs** mostra todas as rotas e deixa testar cada uma pelo navegador.

O banco é o arquivo `evencon.db`, criado na raiz do projeto. Ele não vai para o Git: cada pessoa gera o seu com a carga.

## Rotas

| Método | Rota | O que faz |
|---|---|---|
| GET | `/eventos` | Lista os eventos em ordem de data, no formato resumido usado pelos cards |
| GET | `/eventos/{id}` | Evento completo, com os lugares próximos |
| GET | `/eventos/{id}/semelhantes?limite=3` | Outros eventos, começando pelos que têm mais categorias em comum |
| POST | `/eventos` | Cria um evento |
| POST | `/eventos/lote` | Cria vários eventos de uma vez |
| GET | `/lugares` | Lista os lugares |
| POST | `/lugares` | Cria um lugar |
| POST | `/lugares/lote` | Cria vários lugares de uma vez |

O JSON usa os mesmos nomes dos tipos do front-end (`rotuloPreco`, `distanciaKm`, `lugaresProximos`...).

As rotas de criação ainda **não pedem login**: qualquer pessoa que alcance a API consegue inserir. Isso precisa ser fechado antes de publicar.

## Inserir eventos em massa

Edite os arquivos da pasta `dados/` e rode a carga:

- `dados/lugares.json` — bares, restaurantes e afins.
- `dados/eventos.json` — eventos. Cada lugar próximo é indicado pelo **nome** do lugar:

  ```json
  "lugaresProximos": [{ "lugar": "Pátio América", "distanciaKm": 0.4 }]
  ```

```bash
python -m app.carga --recriar    # apaga o banco inteiro e carrega de novo
```

Sem `--recriar`, a carga só roda se o banco ainda não tiver eventos.

Em cada evento, `inicio` é obrigatório (`"2026-10-03T20:30"`). Os textos `data` e `dataCompleta` são opcionais: se faltarem, a API monta a partir de `inicio` ("Sáb 3 out · 20h30"). Preencha `data` à mão só quando quiser algo diferente, como "Sáb 3 out · 8h às 13h".

## Mudou uma tabela?

Ainda não há migrações. Se alguém alterar `app/modelos.py`, é preciso recriar o banco com `python -m app.carga --recriar`, e o que foi inserido fora dos arquivos de `dados/` se perde.

## Testes

```bash
python -m pytest
```

Os testes usam um banco temporário próprio e não mexem no `evencon.db`.

## Organização

```
app/
  main.py        cria a API e libera o acesso do front-end (CORS)
  banco.py       conexão com o banco
  modelos.py     tabelas
  esquemas.py    formato do JSON que entra e sai
  datas.py       textos de data em português
  carga.py       carga em massa a partir de dados/
  rotas/         eventos.py e lugares.py
dados/           eventos e lugares da carga inicial
tests/           testes da API
```

## Configuração

Tudo opcional, por variável de ambiente:

- `EVENCON_BANCO` — endereço do banco. Padrão: `sqlite:///evencon.db`.
- `EVENCON_ORIGENS` — endereços do front-end que podem chamar a API, separados por vírgula. Padrão: `http://localhost:5173`.
