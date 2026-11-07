"""Testes das regras de limpeza com um conjunto pequeno e controlado."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from banksense.dados.limpeza import converter_datas, limpar, padronizar_canal, padronizar_regiao


@pytest.fixture
def brutos() -> tuple[pd.DataFrame, pd.DataFrame]:
    clientes = pd.DataFrame({
        "id_cliente": ["CLI-1", "CLI-2"],
        "regiao": ["Sul", "Norte"],
        "segmento": ["varejo", "varejo"],
        "faixa_etaria": ["25-34", "35-44"],
        "data_cadastro": ["2024-01-01", "2023-05-10"],
    })
    linha = {
        "id_mensagem": "MSG-1", "id_cliente": "CLI-1", "data_mensagem": "2025-03-01", "canal": "app",
        "categoria": "pix", "texto": "o pix não caiu", "sentimento_referencia": "negativo",
        "nota_satisfacao": "2", "tempo_resolucao_horas": 5.0, "regiao": "Sul", "situacao": "resolvida",
        "tipo_texto": "direto",
    }
    linhas = [
        linha,
        linha,  # duplicata exata
        {**linha, "id_mensagem": "MSG-2", "canal": " WhatsApp ", "regiao": "SE", "data_mensagem": "15/04/2025"},
        {**linha, "id_mensagem": "MSG-3", "texto": np.nan},
        {**linha, "id_mensagem": "MSG-4", "nota_satisfacao": "10", "sentimento_referencia": " Positivo"},
        {**linha, "id_mensagem": "MSG-5", "tempo_resolucao_horas": -3.0, "regiao": np.nan, "id_cliente": "CLI-2"},
        {**linha, "id_mensagem": "MSG-6", "categoria": "Cartao Credito"},
    ]
    return pd.DataFrame(linhas), clientes


def test_limpeza_completa(brutos: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    df, _, rel = limpar(*brutos)
    assert rel.duplicatas_exatas == 1
    assert rel.linhas_removidas_sem_texto == 1
    assert rel.linhas_tratadas == 5
    assert rel.datas_formato_br == 1
    assert rel.notas_fora_da_faixa == 1
    assert rel.tempos_negativos == 1
    assert rel.regioes_imputadas_pelo_cliente == 1

    por_id = df.set_index("id_mensagem")
    assert por_id.at["MSG-2", "canal"] == "chat"
    assert por_id.at["MSG-2", "regiao"] == "Sudeste"
    assert por_id.at["MSG-2", "data_mensagem"] == pd.Timestamp("2025-04-15")
    assert pd.isna(por_id.at["MSG-4", "nota_satisfacao"])
    assert por_id.at["MSG-4", "sentimento_referencia"] == "positivo"
    assert pd.isna(por_id.at["MSG-5", "tempo_resolucao_horas"])
    assert por_id.at["MSG-5", "regiao"] == "Norte"  # veio do cadastro do cliente
    assert por_id.at["MSG-6", "categoria"] == "cartao_credito"


def test_dados_brutos_nao_sao_alterados(brutos: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    mensagens, clientes = brutos
    copia = mensagens.copy()
    limpar(mensagens, clientes)
    pd.testing.assert_frame_equal(mensagens, copia)


def test_padronizacoes() -> None:
    assert padronizar_canal(pd.Series(["E-Mail", "0800", " CHAT "])).tolist() == ["email", "telefone", "chat"]
    assert padronizar_regiao(pd.Series(["centro oeste", "NE"])).tolist() == ["Centro-Oeste", "Nordeste"]


def test_converter_datas_mistas() -> None:
    datas, qtd_br = converter_datas(pd.Series(["2025-01-31", "28/02/2025", "lixo"]))
    assert qtd_br == 1
    assert datas.iloc[0] == pd.Timestamp("2025-01-31")
    assert datas.iloc[1] == pd.Timestamp("2025-02-28")
    assert pd.isna(datas.iloc[2])
