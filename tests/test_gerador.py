"""Testes do gerador de dados sintéticos."""

from __future__ import annotations

import pandas as pd
import pytest

from banksense.dados import premissas as P
from banksense.dados.gerador import gerar

N_TESTE = 3_000


@pytest.fixture(scope="module")
def dados() -> tuple[pd.DataFrame, pd.DataFrame]:
    return gerar(n=N_TESTE, semente=123)


def test_distribuicoes_somam_um() -> None:
    for dist in (P.REGIOES, P.SEGMENTOS, P.FAIXAS_ETARIAS, P.CANAIS, P.CATEGORIAS, P.SITUACOES,
                 P.SITUACOES_RECENTES):
        assert sum(dist.values()) == pytest.approx(1.0)
    for probs in (*P.SENTIMENTO_POR_CATEGORIA.values(), *P.NOTA_POR_SENTIMENTO.values()):
        assert sum(probs) == pytest.approx(1.0)
    assert set(P.SENTIMENTO_POR_CATEGORIA) == set(P.CATEGORIAS)


def test_reprodutivel_com_mesma_semente() -> None:
    _, a = gerar(n=500, semente=7)
    _, b = gerar(n=500, semente=7)
    pd.testing.assert_frame_equal(a, b)


def test_sementes_diferentes_geram_dados_diferentes() -> None:
    _, a = gerar(n=500, semente=7)
    _, b = gerar(n=500, semente=8)
    assert not a["texto"].equals(b["texto"])


def test_colunas_esperadas(dados: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    clientes, mensagens = dados
    assert list(clientes.columns) == ["id_cliente", "regiao", "segmento", "faixa_etaria", "data_cadastro"]
    assert {"id_mensagem", "id_cliente", "data_mensagem", "canal", "categoria", "texto",
            "sentimento_referencia", "nota_satisfacao", "tempo_resolucao_horas", "regiao",
            "situacao"} <= set(mensagens.columns)


def test_volume_inclui_duplicatas(dados: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    _, mensagens = dados
    assert len(mensagens) > N_TESTE  # duplicatas propositais
    assert mensagens.duplicated().sum() == len(mensagens) - N_TESTE


def test_sujeira_foi_inserida(dados: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    _, m = dados
    assert m["texto"].isna().sum() > 0
    assert m["canal"].isna().sum() > 0
    assert (~m["canal"].dropna().isin(P.CANAIS)).sum() > 0  # variações de escrita
    assert m["data_mensagem"].str.contains("/").sum() > 0  # datas dd/mm/aaaa
    assert m["nota_satisfacao"].isna().sum() > 0


def test_sentimentos_validos_apos_normalizar(dados: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    _, m = dados
    normalizado = m["sentimento_referencia"].str.strip().str.lower()
    assert set(normalizado.unique()) == {"negativo", "neutro", "positivo"}


def test_tempo_nulo_quando_nao_resolvida(dados: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    _, m = dados
    nao_resolvidas = m[m["situacao"].isin(["aberta", "em_andamento"])]
    assert nao_resolvidas["tempo_resolucao_horas"].isna().all()


def test_clientes_das_mensagens_existem(dados: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    clientes, m = dados
    assert m["id_cliente"].isin(clientes["id_cliente"]).all()
