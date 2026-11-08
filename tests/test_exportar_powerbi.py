import pandas as pd

from banksense.dados.exportar_powerbi import montar_dim_clientes, montar_fato


def test_fato_traduz_rotulos_e_preenche_canal_vazio():
    mensagens = pd.DataFrame(
        {
            "id_mensagem": ["MSG-1", "MSG-2"],
            "id_cliente": ["CLI-1", "CLI-2"],
            "data_mensagem": pd.to_datetime(["2025-01-01", "2025-11-15"]),
            "canal": ["app", None],
            "categoria": ["cartao_credito", "pix"],
            "sentimento_referencia": ["negativo", "positivo"],
            "nota_satisfacao": pd.array([1, None], dtype="Int64"),
            "tempo_resolucao_horas": [12.346, None],
            "situacao": ["em_andamento", "resolvida"],
        }
    )
    fato = montar_fato(mensagens)
    assert fato["canal"].tolist() == ["Aplicativo", "Não informado"]
    assert fato["categoria"].tolist() == ["Cartão de crédito", "Pix"]
    assert fato["sentimento"].tolist() == ["Negativo", "Positivo"]
    assert fato["situacao"].tolist() == ["Em andamento", "Resolvida"]
    assert fato["tempo_resolucao_horas"].iloc[0] == 12.35


def test_dim_clientes_traduz_segmento():
    clientes = pd.DataFrame(
        {
            "id_cliente": ["CLI-1", "CLI-2"],
            "regiao": ["Sul", "Norte"],
            "segmento": ["pj_mei", "alta_renda"],
            "faixa_etaria": ["25-34", "60+"],
            "data_cadastro": pd.to_datetime(["2020-01-01", "2024-06-20"]),
        }
    )
    dim = montar_dim_clientes(clientes)
    assert dim["segmento"].tolist() == ["PJ e MEI", "Alta renda"]
