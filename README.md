# Evencon — back-end

API do Evencon, feita em Python com FastAPI e banco SQLite. Cuida de **eventos**, **lugares** e **contas** (cadastro, login e a conta de administração). Os eventos salvos ainda ficam no front-end.

## Como rodar

Feito e testado com Python 3.14; versões mais antigas não foram testadas.

```bash
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m app.carga              # cria o banco e insere os eventos de dados/
python -m app.criar_admin        # cria a conta de administração e mostra a senha
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
| POST | `/eventos` | Cria um evento (só administração) |
| POST | `/eventos/lote` | Cria vários eventos de uma vez (só administração) |
| DELETE | `/eventos/{id}` | Apaga um evento (só administração) |
| GET | `/lugares` | Lista os lugares |
| POST | `/lugares` | Cria um lugar (só administração) |
| POST | `/lugares/lote` | Cria vários lugares de uma vez (só administração) |
| POST | `/auth/cadastro` | Cria uma conta e já devolve o login |
| POST | `/auth/login` | Entra com e-mail e senha |
| GET | `/auth/eu` | Dados da conta logada |
| PUT | `/auth/eu/interesses` | Atualiza os interesses da conta logada |
| POST | `/auth/sair` | Encerra o login atual |

O JSON usa os mesmos nomes dos tipos do front-end (`rotuloPreco`, `distanciaKm`, `lugaresProximos`...).

## Contas e administração

O cadastro e o login devolvem um `token`. As rotas que pedem login esperam esse token no cabeçalho `Authorization: Bearer <token>`. As senhas são guardadas com hash (scrypt), nunca em texto.

Criar e apagar eventos e lugares só funciona para a conta de administração, `admin@gmail.com.br`. Ela não é criada pelo cadastro comum:

```bash
python -m app.criar_admin
```

O comando cria a conta e mostra uma senha gerada na hora, **uma única vez**. Rodar de novo redefine a senha. Para escolher a senha, use a variável `EVENCON_SENHA_ADMIN`:

```bash
EVENCON_SENHA_ADMIN="uma-senha-so-sua" python -m app.criar_admin
```

Como o banco não vai para o Git, cada pessoa do grupo cria a própria conta de administração na sua máquina.

## Inserir eventos em massa

Edite os arquivos da pasta `dados/` e rode a carga:

- `dados/lugares.json` — bares, restaurantes e afins.
- `dados/eventos.json` — eventos. Cada lugar próximo é indicado pelo **nome** do lugar:

  ```json
  "lugaresProximos": [{ "lugar": "Pátio América", "distanciaKm": 0.4 }]
  ```

```bash
python -m app.carga --recriar    # apaga eventos e lugares e carrega de novo (as contas ficam)
```

Sem `--recriar`, a carga só roda se o banco ainda não tiver eventos.

Em cada evento, `inicio` é obrigatório (`"2026-10-03T20:30"`). Os textos `data` e `dataCompleta` são opcionais: se faltarem, a API monta a partir de `inicio` ("Sáb 3 out · 20h30"). Preencha `data` à mão só quando quiser algo diferente, como "Sáb 3 out · 8h às 13h".

## Mudou uma tabela?

Ainda não há migrações. Se alguém alterar `app/modelos.py`, é preciso recriar as tabelas. Para eventos e lugares, `python -m app.carga --recriar` resolve, e o que foi inserido fora dos arquivos de `dados/` se perde. Para mudanças na tabela de contas, é preciso apagar o arquivo `evencon.db`, e aí todas as contas se perdem.

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
  seguranca.py   hash de senha e tokens de login
  carga.py       carga em massa a partir de dados/
  criar_admin.py cria a conta de administração
  rotas/         auth.py, eventos.py e lugares.py
dados/           eventos e lugares da carga inicial
tests/           testes da API
```

## Configuração

Tudo opcional, por variável de ambiente:

- `EVENCON_BANCO` — endereço do banco. Padrão: `sqlite:///evencon.db`.
- `EVENCON_SENHA_ADMIN` e `EVENCON_EMAIL_ADMIN` — usadas só pelo `criar_admin`.
- `EVENCON_ORIGENS` — endereços do front-end que podem chamar a API, separados por vírgula. Padrão: `http://localhost:5173`.
