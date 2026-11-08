"""Pipeline de limpeza: dados brutos (data/raw) -> dados tratados (data/processed).

Uso:
    python -m banksense.dados.limpeza

Os dados brutos nunca são alterados. O pipeline gera:
- data/processed/mensagens_tratadas.parquet
- data/processed/clientes_tratados.parquet
- reports/qualidade_dados.md e reports/qualidade_dados.json
"""

from __future__ import annotations

import json
import unicodedata
from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd

from banksense import config
from banksense.logs import obter_logger

log = obter_logger("banksense.limpeza")

CANAIS_VALIDOS = ("app", "chat", "telefone", "redes_sociais", "email", "ouvidoria")
REGIOES_VALIDAS = ("Sudeste", "Nordeste", "Sul", "Norte", "Centro-Oeste")
CATEGORIAS_VALIDAS = ("cartao_credito", "pix", "conta_corrente", "aplicativo", "emprestimo", "tarifas",
                      "investimentos", "atendimento", "fraude_seguranca")
SENTIMENTOS_VALIDOS = ("negativo", "neutro", "positivo")
SITUACOES_VALIDAS = ("aberta", "em_andamento", "resolvida", "cancelada")

MAPA_CANAL = {
    "aplicativo": "app", "app mobile": "app", "whatsapp": "chat", "chat online": "chat", "fone": "telefone",
    "0800": "telefone", "e-mail": "email", "instagram": "redes_sociais", "redes sociais": "redes_sociais",
}
MAPA_REGIAO = {
    "se": "Sudeste", "sudeste": "Sudeste", "ne": "Nordeste", "nordeste": "Nordeste", "s": "Sul", "sul": "Sul",
    "n": "Norte", "norte": "Norte", "co": "Centro-Oeste", "centro oeste": "Centro-Oeste",
    "centro-oeste": "Centro-Oeste",
}


@dataclass
class RelatorioQualidade:
    linhas_brutas: int = 0
    linhas_tratadas: int = 0
    nulos_antes: dict[str, int] = field(default_factory=dict)
    nulos_depois: dict[str, int] = field(default_factory=dict)
    duplicatas_exatas: int = 0
    ids_repetidos_restantes: int = 0
    valores_distintos_antes: dict[str, int] = field(default_factory=dict)
    valores_distintos_depois: dict[str, int] = field(default_factory=dict)
    valores_invalidos_apos_padronizar: dict[str, int] = field(default_factory=dict)
    datas_formato_br: int = 0
    datas_invalidas: int = 0
    notas_fora_da_faixa: int = 0
    tempos_negativos: int = 0
    tempos_outliers: int = 0
    limite_outlier_horas: float = 0.0
    limites_outlier_por_canal: dict[str, float] = field(default_factory=dict)
    regioes_imputadas_pelo_cliente: int = 0
    linhas_removidas_sem_texto: int = 0


def _chave(valor: object) -> object:
    """Minúsculas, sem espaços nas pontas e sem acentos (para comparar valores sujos)."""
    if not isinstance(valor, str):
        return valor
    sem_acento = unicodedata.normalize("NFKD", valor).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.strip().lower().split())


def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """Nomes de colunas em minúsculas, sem espaços."""
    return df.rename(columns=lambda c: _chave(c).replace(" ", "_"))


def padronizar_canal(serie: pd.Series) -> pd.Series:
    chave = serie.map(_chave)
    return chave.map(lambda v: MAPA_CANAL.get(v, v.replace(" ", "_")) if isinstance(v, str) else v)


def padronizar_regiao(serie: pd.Series) -> pd.Series:
    return serie.map(_chave).map(lambda v: MAPA_REGIAO.get(v, v) if isinstance(v, str) else v)


def padronizar_categoria(serie: pd.Series) -> pd.Series:
    return serie.map(_chave).map(lambda v: v.replace(" ", "_") if isinstance(v, str) else v)


def converter_datas(serie: pd.Series) -> tuple[pd.Series, int]:
    """Aceita aaaa-mm-dd e dd/mm/aaaa. Devolve as datas e quantas estavam no formato brasileiro."""
    texto = serie.astype("string").str.strip()
    formato_br = texto.str.contains("/", na=False)
    iso = pd.to_datetime(texto.where(~formato_br), format="%Y-%m-%d", errors="coerce")
    br = pd.to_datetime(texto.where(formato_br), format="%d/%m/%Y", errors="coerce")
    return iso.fillna(br), int(formato_br.sum())


def invalidar_fora_do_dominio(serie: pd.Series, validos: tuple[str, ...]) -> tuple[pd.Series, int]:
    invalido = serie.notna() & ~serie.isin(validos)
    return serie.where(~invalido), int(invalido.sum())


def limite_outlier_log(serie: pd.Series, k: float = 3.0) -> float:
    """Limite superior de outlier pelo IQR na escala log (adequado a tempos com cauda longa)."""
    log = np.log1p(serie.dropna())
    q1, q3 = log.quantile([0.25, 0.75])
    return float(np.expm1(q3 + k * (q3 - q1)))


def limpar(mensagens: pd.DataFrame, clientes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, RelatorioQualidade]:
    """Aplica todas as regras de limpeza e devolve (mensagens, clientes, relatório)."""
    rel = RelatorioQualidade(linhas_brutas=len(mensagens))
    df = padronizar_colunas(mensagens.copy())
    cli = padronizar_colunas(clientes.copy())

    rel.nulos_antes = {k: int(v) for k, v in df.isna().sum().items()}
    rel.valores_distintos_antes = {c: int(df[c].nunique()) for c in ("canal", "regiao", "categoria",
                                                                      "sentimento_referencia")}

    # 1. Duplicatas exatas
    rel.duplicatas_exatas = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)

    # 2. Padronização de categorias
    df["canal"] = padronizar_canal(df["canal"])
    df["regiao"] = padronizar_regiao(df["regiao"])
    df["categoria"] = padronizar_categoria(df["categoria"])
    df["sentimento_referencia"] = df["sentimento_referencia"].map(_chave)
    df["situacao"] = df["situacao"].map(_chave)

    # 3. Validação: o que sobrar fora do domínio vira nulo e é contado
    for coluna, validos in (("canal", CANAIS_VALIDOS), ("regiao", REGIOES_VALIDAS),
                            ("categoria", CATEGORIAS_VALIDAS), ("sentimento_referencia", SENTIMENTOS_VALIDOS),
                            ("situacao", SITUACOES_VALIDAS)):
        df[coluna], qtd = invalidar_fora_do_dominio(df[coluna], validos)
        rel.valores_invalidos_apos_padronizar[coluna] = qtd

    # 4. Região faltante: usa a região cadastrada do cliente
    regiao_cliente = df["id_cliente"].map(cli.set_index("id_cliente")["regiao"])
    faltante = df["regiao"].isna() & regiao_cliente.notna()
    rel.regioes_imputadas_pelo_cliente = int(faltante.sum())
    df.loc[faltante, "regiao"] = regiao_cliente[faltante]

    # 5. Datas
    df["data_mensagem"], rel.datas_formato_br = converter_datas(df["data_mensagem"])
    rel.datas_invalidas = int(df["data_mensagem"].isna().sum())
    cli["data_cadastro"] = pd.to_datetime(cli["data_cadastro"], format="%Y-%m-%d")

    # 6. Nota fora de 1 a 5 é erro de registro: vira nulo
    nota = pd.to_numeric(df["nota_satisfacao"], errors="coerce")
    fora = nota.notna() & ~nota.between(1, 5)
    rel.notas_fora_da_faixa = int(fora.sum())
    df["nota_satisfacao"] = nota.where(~fora).astype("Int64")

    # 7. Tempo negativo é erro; tempo muito alto é outlier (mantido, mas sinalizado)
    tempo = pd.to_numeric(df["tempo_resolucao_horas"], errors="coerce")
    negativo = tempo < 0
    rel.tempos_negativos = int(negativo.sum())
    tempo = tempo.where(~negativo)
    df["tempo_resolucao_horas"] = tempo
    # Limite por canal: 100 h é absurdo no chat, mas normal na ouvidoria
    limite_geral = limite_outlier_log(tempo)
    limites = {c: limite_outlier_log(g) for c, g in df.groupby("canal")["tempo_resolucao_horas"]}
    rel.limites_outlier_por_canal = {c: round(v, 1) for c, v in limites.items()}
    rel.limite_outlier_horas = round(limite_geral, 1)
    limite_linha = df["canal"].map(limites).fillna(limite_geral)
    df["tempo_outlier"] = tempo > limite_linha
    rel.tempos_outliers = int(df["tempo_outlier"].sum())

    # 8. Sem texto não há o que classificar: a linha sai
    sem_texto = df["texto"].isna() | (df["texto"].astype("string").str.strip() == "")
    rel.linhas_removidas_sem_texto = int(sem_texto.sum())
    df = df[~sem_texto].copy()
    df["texto"] = df["texto"].str.strip()

    # 9. Sem sentimento de referência válido também sai (não serve para treino nem análise)
    df = df[df["sentimento_referencia"].notna() & df["categoria"].notna() & df["data_mensagem"].notna()]

    rel.ids_repetidos_restantes = int(df["id_mensagem"].duplicated().sum())
    df = df.sort_values(["data_mensagem", "id_mensagem"]).reset_index(drop=True)

    rel.linhas_tratadas = len(df)
    rel.nulos_depois = {k: int(v) for k, v in df.isna().sum().items()}
    rel.valores_distintos_depois = {c: int(df[c].nunique()) for c in ("canal", "regiao", "categoria",
                                                                       "sentimento_referencia")}
    return df, cli, rel


def relatorio_markdown(rel: RelatorioQualidade) -> str:
    """Relatório de qualidade legível, com antes e depois."""
    linhas_nulos = "\n".join(
        f"| {c} | {rel.nulos_antes.get(c, 0):,} | {rel.nulos_depois.get(c, 0):,} |"
        for c in rel.nulos_antes
    )
    linhas_dist = "\n".join(
        f"| {c} | {rel.valores_distintos_antes[c]} | {rel.valores_distintos_depois[c]} |"
        for c in rel.valores_distintos_antes
    )
    return f"""# Relatório de qualidade dos dados

> Dados **sintéticos**. Gerado por `python -m banksense.dados.limpeza`.

## Resumo

| Item | Quantidade |
|---|---|
| Linhas brutas | {rel.linhas_brutas:,} |
| Duplicatas exatas removidas | {rel.duplicatas_exatas:,} |
| Linhas sem texto removidas | {rel.linhas_removidas_sem_texto:,} |
| **Linhas tratadas** | **{rel.linhas_tratadas:,}** |
| Datas no formato dd/mm/aaaa convertidas | {rel.datas_formato_br:,} |
| Datas inválidas | {rel.datas_invalidas:,} |
| Notas fora de 1 a 5 (viraram nulo) | {rel.notas_fora_da_faixa:,} |
| Tempos de resolução negativos (viraram nulo) | {rel.tempos_negativos:,} |
| Tempos sinalizados como outlier (limite por canal) | {rel.tempos_outliers:,} |
| Regiões faltantes preenchidas pelo cadastro do cliente | {rel.regioes_imputadas_pelo_cliente:,} |
| IDs de mensagem repetidos após a limpeza | {rel.ids_repetidos_restantes:,} |

## Valores distintos (antes e depois da padronização)

| Coluna | Antes | Depois |
|---|---|---|
{linhas_dist}

Valores que continuaram fora do domínio após a padronização (viraram nulo):
{", ".join(f"`{c}` {q}" for c, q in rel.valores_invalidos_apos_padronizar.items())}.

## Nulos por coluna

| Coluna | Antes | Depois |
|---|---|---|
{linhas_nulos}

`tempo_resolucao_horas` continua com nulos porque mensagens `aberta` e `em_andamento`
ainda não foram resolvidas: é um nulo **esperado**, não um erro.

## Regras aplicadas

1. Duplicatas exatas removidas.
2. Canal, região, categoria, sentimento e situação padronizados (minúsculas, sem acento,
   sinônimos como `whatsapp` -> `chat` e siglas como `SE` -> `Sudeste`).
3. Valores fora do domínio após a padronização viram nulo.
4. Região faltante preenchida com a região do cadastro do cliente.
5. Datas aceitas em `aaaa-mm-dd` e `dd/mm/aaaa`.
6. Nota fora de 1 a 5 vira nulo (erro de registro).
7. Tempo negativo vira nulo; tempo alto demais é **mantido** e sinalizado em `tempo_outlier`
   (critério: acima de Q3 + 3 × IQR na escala log, calculado **por canal**).
   Limites em horas: {", ".join(f"{c} {v:,.1f}" for c, v in rel.limites_outlier_por_canal.items())}.
8. Linhas sem texto são removidas.
"""


def main() -> None:
    if not config.ARQ_MENSAGENS_BRUTO.exists():
        log.error("Arquivo bruto não encontrado: %s. Rode antes: python -m banksense.dados.gerador",
                  config.ARQ_MENSAGENS_BRUTO)
        raise SystemExit(1)
    mensagens = pd.read_csv(config.ARQ_MENSAGENS_BRUTO, dtype={"nota_satisfacao": "string"})
    clientes = pd.read_csv(config.ARQ_CLIENTES_BRUTO)
    log.info("Limpeza iniciada: %s mensagens brutas", f"{len(mensagens):,}")
    df, cli, rel = limpar(mensagens, clientes)
    log.info("Duplicatas exatas removidas: %s", f"{rel.duplicatas_exatas:,}")
    log.info("Linhas sem texto removidas: %s", f"{rel.linhas_removidas_sem_texto:,}")
    if rel.datas_invalidas:
        log.warning("Datas inválidas: %s", f"{rel.datas_invalidas:,}")
    if rel.notas_fora_da_faixa or rel.tempos_negativos:
        log.warning("Valores fora da faixa viraram nulo: %s notas, %s tempos negativos",
                    f"{rel.notas_fora_da_faixa:,}", f"{rel.tempos_negativos:,}")
    if rel.ids_repetidos_restantes:
        log.warning("IDs de mensagem ainda repetidos após a limpeza: %s", f"{rel.ids_repetidos_restantes:,}")

    config.DIR_TRATADOS.mkdir(parents=True, exist_ok=True)
    config.DIR_RELATORIOS.mkdir(parents=True, exist_ok=True)
    df.to_parquet(config.ARQ_MENSAGENS_TRATADO, index=False)
    cli.to_parquet(config.ARQ_CLIENTES_TRATADO, index=False)
    (config.DIR_RELATORIOS / "qualidade_dados.json").write_text(
        json.dumps(asdict(rel), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (config.DIR_RELATORIOS / "qualidade_dados.md").write_text(relatorio_markdown(rel), encoding="utf-8")
    log.info("Limpeza concluída: %s brutas -> %s tratadas", f"{rel.linhas_brutas:,}", f"{rel.linhas_tratadas:,}")
    log.info("Relatório: %s", config.DIR_RELATORIOS / "qualidade_dados.md")


if __name__ == "__main__":
    main()
