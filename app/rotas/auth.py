from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import esquemas, modelos, seguranca
from app.banco import obter_sessao

rotas = APIRouter(prefix="/auth", tags=["Contas"])

esquema_token = HTTPBearer(auto_error=False)


def normalizar_email(email: str) -> str:
    return email.strip().lower()


def abrir_sessao(sessao: Session, usuario: modelos.Usuario) -> esquemas.SessaoAberta:
    token = seguranca.novo_token()
    sessao.add(modelos.Sessao(token_hash=seguranca.hash_token(token), usuario_id=usuario.id))
    sessao.commit()
    return esquemas.SessaoAberta(token=token, usuario=esquemas.Usuario.model_validate(usuario))


def sessao_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(esquema_token),
    sessao: Session = Depends(obter_sessao),
) -> modelos.Sessao:
    login = credenciais and sessao.get(modelos.Sessao, seguranca.hash_token(credenciais.credentials))
    if not login:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Entre na sua conta para continuar.")
    return login


def usuario_atual(login: modelos.Sessao = Depends(sessao_atual)) -> modelos.Usuario:
    return login.usuario


def exigir_admin(usuario: modelos.Usuario = Depends(usuario_atual)) -> modelos.Usuario:
    if not usuario.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só a administração pode fazer isso.")
    return usuario


@rotas.post("/cadastro", response_model=esquemas.SessaoAberta, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: esquemas.CadastroEntrada, sessao: Session = Depends(obter_sessao)):
    email = normalizar_email(dados.email)
    if sessao.scalar(select(modelos.Usuario).where(modelos.Usuario.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma conta com esse e-mail.")

    usuario = modelos.Usuario(
        nome=dados.nome.strip(),
        email=email,
        senha_hash=seguranca.gerar_hash_senha(dados.senha),
        interesses=[],
    )
    sessao.add(usuario)
    sessao.commit()
    return abrir_sessao(sessao, usuario)


@rotas.post("/login", response_model=esquemas.SessaoAberta)
def entrar(dados: esquemas.LoginEntrada, sessao: Session = Depends(obter_sessao)):
    usuario = sessao.scalar(
        select(modelos.Usuario).where(modelos.Usuario.email == normalizar_email(dados.email))
    )
    if not usuario or not seguranca.conferir_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos.")
    return abrir_sessao(sessao, usuario)


@rotas.get("/eu", response_model=esquemas.Usuario)
def quem_sou_eu(usuario: modelos.Usuario = Depends(usuario_atual)):
    return usuario


@rotas.put("/eu/interesses", response_model=esquemas.Usuario)
def atualizar_interesses(
    dados: esquemas.InteressesEntrada,
    usuario: modelos.Usuario = Depends(usuario_atual),
    sessao: Session = Depends(obter_sessao),
):
    usuario = sessao.merge(usuario)
    usuario.interesses = dados.interesses
    sessao.commit()
    return usuario


@rotas.post("/sair", status_code=status.HTTP_204_NO_CONTENT)
def sair(login: modelos.Sessao = Depends(sessao_atual), sessao: Session = Depends(obter_sessao)):
    sessao.delete(sessao.merge(login))
    sessao.commit()
