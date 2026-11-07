"""Carga e preparação dos dados para o dashboard.

Lê do PostgreSQL quando ele está disponível; se não estiver, usa o arquivo tratado em data/processed.
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy.exc import OperationalError

from banksense import config
from banksense.db import obter_engine

CONSULTA = """
SELECT m.id_mensagem, m.id_cliente, m.data_mensagem, m.canal, m.categoria, m.texto,
       m.sentimento_referencia, m.regiao, a.situacao, a.nota_satisfacao, a.tempo_resolucao_horas,
       c.segmento, c.faixa_etaria
FROM mensagens m
JOIN atendimentos a USING (id_mensagem)
JOIN clientes c USING (id_cliente)
"""

NOMES_CATEGORIA = {
    "cartao_credito": "Cartão de crédito", "pix": "Pix", "conta_corrente": "Conta corrente",
    "aplicativo": "Aplicativo", "emprestimo": "Empréstimo", "tarifas": "Tarifas",
    "investimentos": "Investimentos", "atendimento": "Atendimento", "fraude_seguranca": "Fraude e segurança",
}
NOMES_CANAL = {
    "app": "App", "chat": "Chat", "telefone": "Telefone", "redes_sociais": "Redes sociais",
    "email": "E-mail", "ouvidoria": "Ouvidoria",
}
NOMES_SEGMENTO = {"varejo": "Varejo", "alta_renda": "Alta renda", "universitario": "Universitário",
                  "pj_mei": "PJ / MEI"}
NOMES_SITUACAO = {"aberta": "Aberta", "em_andamento": "Em andamento", "resolvida": "Resolvida",
                  "cancelada": "Cancelada"}


def _ler_banco() -> pd.DataFrame:
    with obter_engine().connect() as con:
        return pd.read_sql(CONSULTA, con)


def _ler_arquivo() -> pd.DataFrame:
    msg = pd.read_parquet(config.ARQ_MENSAGENS_TRATADO)
    cli = pd.read_parquet(config.ARQ_CLIENTES_TRATADO)[["id_cliente", "segmento", "faixa_etaria"]]
    return msg.merge(cli, on="id_cliente", how="left")


def carregar() -> tuple[pd.DataFrame, str]:
    """Devolve (dados prontos para o dashboard, origem dos dados)."""
    try:
        df, origem = _ler_banco(), "PostgreSQL"
    except OperationalError:
        df, origem = _ler_arquivo(), "arquivo tratado (PostgreSQL indisponível)"

    df["data_mensagem"] = pd.to_datetime(df["data_mensagem"])
    df["tempo_resolucao_horas"] = pd.to_numeric(df["tempo_resolucao_horas"], errors="coerce")
    df["nota_satisfacao"] = pd.to_numeric(df["nota_satisfacao"], errors="coerce")
    df["negativo"] = (df["sentimento_referencia"] == "negativo").astype(int)
    df["Categoria"] = df["categoria"].map(NOMES_CATEGORIA)
    df["Canal"] = df["canal"].map(NOMES_CANAL).fillna("Não informado")
    df["Segmento"] = df["segmento"].map(NOMES_SEGMENTO)
    df["Situação"] = df["situacao"].map(NOMES_SITUACAO)
    df["Sentimento"] = df["sentimento_referencia"].str.capitalize()
    df["Região"] = df["regiao"]
    df["Faixa etária"] = df["faixa_etaria"]
    return df, origem
