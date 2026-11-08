"""Importa os dados tratados para o PostgreSQL (substitui o conteúdo anterior).

Uso:
    python -m banksense.db.carga
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy import Engine, text

from banksense import config
from banksense.db import obter_engine
from banksense.db.migracoes import aplicar_migracoes
from banksense.logs import obter_logger

log = obter_logger("banksense.carga")

COLUNAS_MENSAGENS = ["id_mensagem", "id_cliente", "data_mensagem", "canal", "categoria", "texto",
                     "sentimento_referencia", "regiao"]
COLUNAS_ATENDIMENTOS = ["id_mensagem", "situacao", "nota_satisfacao", "tempo_resolucao_horas"]


def carregar(mensagens: pd.DataFrame, clientes: pd.DataFrame, engine: Engine | None = None) -> dict[str, int]:
    """Recria o conteúdo de clientes, mensagens e atendimentos em uma única transação."""
    engine = engine or obter_engine()
    aplicar_migracoes(engine)

    msg = mensagens[COLUNAS_MENSAGENS].copy()
    msg["data_mensagem"] = pd.to_datetime(msg["data_mensagem"]).dt.date
    atd = mensagens[COLUNAS_ATENDIMENTOS].copy()
    cli = clientes.copy()
    cli["data_cadastro"] = pd.to_datetime(cli["data_cadastro"]).dt.date

    with engine.begin() as con:
        con.execute(text("TRUNCATE atendimentos, previsoes_sentimento, mensagens, clientes RESTART IDENTITY CASCADE"))
        opcoes = {"if_exists": "append", "index": False, "method": "multi", "chunksize": 2_000}
        cli.to_sql("clientes", con, **opcoes)
        msg.to_sql("mensagens", con, **opcoes)
        atd.to_sql("atendimentos", con, **opcoes)
        contagens = {
            t: int(con.execute(text(f"SELECT count(*) FROM {t}")).scalar_one())
            for t in ("clientes", "mensagens", "atendimentos")
        }
    return contagens


def main() -> None:
    mensagens = pd.read_parquet(config.ARQ_MENSAGENS_TRATADO)
    clientes = pd.read_parquet(config.ARQ_CLIENTES_TRATADO)
    log.info("Carga iniciada: %s mensagens e %s clientes", f"{len(mensagens):,}", f"{len(clientes):,}")
    try:
        contagens = carregar(mensagens, clientes)
    except Exception:
        log.exception("Falha na carga. O PostgreSQL está rodando? (docker compose up -d)")
        raise
    for tabela, qtd in contagens.items():
        log.info("%s: %s linhas", tabela, f"{qtd:,}")


if __name__ == "__main__":
    main()
