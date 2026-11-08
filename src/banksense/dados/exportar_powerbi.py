"""Exporta o star schema do BankSense em CSV pronto para o Power BI.

Os rótulos viram texto legível em português ("cartao_credito" -> "Cartão de crédito") e os
números saem no formato brasileiro (separador ";" e vírgula decimal), para o Power BI
reconhecer os tipos sem ajuste manual no Power Query.

Uso:
    python -m banksense.dados.exportar_powerbi
"""

from __future__ import annotations

import pandas as pd

from banksense import config
from banksense.logs import configurar_logs, obter_logger

log = obter_logger("banksense.powerbi")

DIR_POWERBI = config.DIR_DADOS / "powerbi"

ROTULOS_CANAL = {
    "app": "Aplicativo",
    "chat": "Chat",
    "telefone": "Telefone",
    "redes_sociais": "Redes sociais",
    "email": "E-mail",
    "ouvidoria": "Ouvidoria",
}
ROTULOS_CATEGORIA = {
    "cartao_credito": "Cartão de crédito",
    "pix": "Pix",
    "aplicativo": "Aplicativo",
    "conta_corrente": "Conta corrente",
    "emprestimo": "Empréstimo",
    "tarifas": "Tarifas",
    "atendimento": "Atendimento",
    "investimentos": "Investimentos",
    "fraude_seguranca": "Fraude e segurança",
}
ROTULOS_SITUACAO = {
    "resolvida": "Resolvida",
    "em_andamento": "Em andamento",
    "aberta": "Aberta",
    "cancelada": "Cancelada",
}
ROTULOS_SEGMENTO = {
    "varejo": "Varejo",
    "alta_renda": "Alta renda",
    "universitario": "Universitário",
    "pj_mei": "PJ e MEI",
}


def _rotular(serie: pd.Series, rotulos: dict[str, str]) -> pd.Series:
    """Troca os códigos pelos rótulos; valores sem rótulo viram 'Não informado'."""
    return serie.map(rotulos).fillna(
        serie.where(serie.isna(), serie.astype(str).str.replace("_", " ").str.capitalize())
    ).fillna("Não informado")


def montar_fato(mensagens: pd.DataFrame) -> pd.DataFrame:
    fato = pd.DataFrame(
        {
            "id_mensagem": mensagens["id_mensagem"],
            "id_cliente": mensagens["id_cliente"],
            "data": mensagens["data_mensagem"].dt.date,
            "canal": _rotular(mensagens["canal"], ROTULOS_CANAL),
            "categoria": _rotular(mensagens["categoria"], ROTULOS_CATEGORIA),
            "sentimento": mensagens["sentimento_referencia"].str.capitalize(),
            "nota_satisfacao": mensagens["nota_satisfacao"],
            "tempo_resolucao_horas": mensagens["tempo_resolucao_horas"].round(2),
            "situacao": _rotular(mensagens["situacao"], ROTULOS_SITUACAO),
        }
    )
    return fato


def montar_dim_clientes(clientes: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id_cliente": clientes["id_cliente"],
            "regiao": clientes["regiao"].fillna("Não informado"),
            "segmento": _rotular(clientes["segmento"], ROTULOS_SEGMENTO),
            "faixa_etaria": clientes["faixa_etaria"].fillna("Não informado"),
            "data_cadastro": clientes["data_cadastro"].dt.date,
        }
    )


def exportar() -> None:
    if not config.ARQ_MENSAGENS_TRATADO.exists():
        log.error("Arquivo tratado não encontrado: %s. Rode antes a limpeza.", config.ARQ_MENSAGENS_TRATADO)
        raise SystemExit(1)

    mensagens = pd.read_parquet(config.ARQ_MENSAGENS_TRATADO)
    clientes = pd.read_parquet(config.ARQ_CLIENTES_TRATADO)

    DIR_POWERBI.mkdir(parents=True, exist_ok=True)
    opcoes = {"sep": ";", "decimal": ",", "index": False, "encoding": "utf-8-sig"}

    fato = montar_fato(mensagens)
    fato.to_csv(DIR_POWERBI / "fato_mensagens.csv", **opcoes)
    dim = montar_dim_clientes(clientes)
    dim.to_csv(DIR_POWERBI / "dim_clientes.csv", **opcoes)

    log.info("Power BI: %s mensagens e %s clientes exportados em %s", f"{len(fato):,}", f"{len(dim):,}", DIR_POWERBI)


def main() -> None:
    configurar_logs()
    exportar()


if __name__ == "__main__":
    main()
