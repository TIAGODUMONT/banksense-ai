"""Caminhos e configurações centrais do projeto."""

from __future__ import annotations

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

DIR_DADOS = RAIZ / "data"
DIR_BRUTOS = DIR_DADOS / "raw"
DIR_TRATADOS = DIR_DADOS / "processed"
DIR_MODELOS = RAIZ / "models"
DIR_RELATORIOS = RAIZ / "reports"
DIR_SQL = RAIZ / "sql"

ARQ_CLIENTES_BRUTO = DIR_BRUTOS / "clientes.csv"
ARQ_MENSAGENS_BRUTO = DIR_BRUTOS / "mensagens_brutas.csv"
ARQ_MENSAGENS_TRATADO = DIR_TRATADOS / "mensagens_tratadas.parquet"
ARQ_CLIENTES_TRATADO = DIR_TRATADOS / "clientes_tratados.parquet"

SEMENTE_PADRAO = 42


def _carregar_env() -> None:
    """Lê o arquivo .env (se existir) sem depender de bibliotecas externas."""
    arquivo = RAIZ / ".env"
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip())


_carregar_env()


def url_banco() -> str:
    """URL de conexão do SQLAlchemy para o PostgreSQL local (Docker Compose)."""
    usuario = os.getenv("POSTGRES_USER", "banksense")
    senha = os.getenv("POSTGRES_PASSWORD", "banksense_local")
    host = os.getenv("POSTGRES_HOST", "localhost")
    porta = os.getenv("POSTGRES_PORT", "5433")
    banco = os.getenv("POSTGRES_DB", "banksense")
    return f"postgresql+psycopg://{usuario}:{senha}@{host}:{porta}/{banco}"
