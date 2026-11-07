"""Aplica as migrations SQL em ordem e registra quais já rodaram.

Uso:
    python -m banksense.db.migracoes
"""

from __future__ import annotations

from sqlalchemy import Engine, text

from banksense import config
from banksense.db import obter_engine

DIR_MIGRACOES = config.DIR_SQL / "migrations"


def aplicar_migracoes(engine: Engine | None = None) -> list[str]:
    """Aplica as migrations pendentes e devolve a lista das que foram aplicadas agora."""
    engine = engine or obter_engine()
    aplicadas_agora: list[str] = []
    with engine.begin() as con:
        con.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schema_migrations ("
                " versao VARCHAR(100) PRIMARY KEY,"
                " aplicada_em TIMESTAMPTZ NOT NULL DEFAULT now())"
            )
        )
        ja_aplicadas = {r[0] for r in con.execute(text("SELECT versao FROM schema_migrations"))}

    for arquivo in sorted(DIR_MIGRACOES.glob("*.sql")):
        if arquivo.name in ja_aplicadas:
            continue
        sql = arquivo.read_text(encoding="utf-8")
        with engine.begin() as con:  # cada migration em uma transação
            con.exec_driver_sql(sql)
            con.execute(text("INSERT INTO schema_migrations (versao) VALUES (:v)"), {"v": arquivo.name})
        aplicadas_agora.append(arquivo.name)
    return aplicadas_agora


def main() -> None:
    aplicadas = aplicar_migracoes()
    if aplicadas:
        for nome in aplicadas:
            print(f"Aplicada: {nome}")
    else:
        print("Nenhuma migration pendente.")


if __name__ == "__main__":
    main()
