"""Senhas e tokens de sessão."""

import hashlib
import hmac
import secrets


def gerar_hash_senha(senha: str) -> str:
    sal = secrets.token_bytes(16)
    resumo = hashlib.scrypt(senha.encode(), salt=sal, n=2**14, r=8, p=1)
    return f"scrypt${sal.hex()}${resumo.hex()}"


def conferir_senha(senha: str, guardado: str) -> bool:
    _, sal, resumo = guardado.split("$")
    calculado = hashlib.scrypt(senha.encode(), salt=bytes.fromhex(sal), n=2**14, r=8, p=1)
    return hmac.compare_digest(calculado.hex(), resumo)


def novo_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """O banco guarda só o hash: quem ler a tabela de sessões não consegue se passar por ninguém."""
    return hashlib.sha256(token.encode()).hexdigest()
