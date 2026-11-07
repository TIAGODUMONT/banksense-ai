"""Acesso ao PostgreSQL: conexão, migrations e carga de dados."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from banksense import config


@lru_cache(maxsize=1)
def obter_engine() -> Engine:
    """Engine única do SQLAlchemy para o banco local."""
    return create_engine(config.url_banco(), pool_pre_ping=True)
