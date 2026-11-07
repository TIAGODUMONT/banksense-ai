"""Teste de integração das migrations (precisa do PostgreSQL do Docker Compose rodando)."""

from __future__ import annotations

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

from banksense.db import obter_engine
from banksense.db.migracoes import aplicar_migracoes


@pytest.fixture(scope="module")
def engine():
    eng = obter_engine()
    try:
        with eng.connect():
            pass
    except OperationalError:
        pytest.skip("PostgreSQL indisponível: rode `docker compose up -d`")
    return eng


def test_migracoes_sao_idempotentes(engine) -> None:
    aplicar_migracoes(engine)
    assert aplicar_migracoes(engine) == []


def test_tabelas_existem(engine) -> None:
    tabelas = set(inspect(engine).get_table_names())
    assert {"clientes", "mensagens", "atendimentos", "previsoes_sentimento", "previsoes_volume"} <= tabelas
