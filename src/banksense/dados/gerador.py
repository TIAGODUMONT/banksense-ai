"""Gerador reproduzível de mensagens sintéticas de clientes de um banco digital fictício.

Uso:
    python -m banksense.dados.gerador            # 50.000 mensagens, semente 42
    python -m banksense.dados.gerador --n 5000   # amostra menor

Os dados são SINTÉTICOS. As premissas estão em banksense/dados/premissas.py
e documentadas em docs/premissas_geracao.md.
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta

import numpy as np
import pandas as pd

from banksense import config
from banksense.dados import premissas as P
from banksense.dados.textos import aplicar_ruido, montar_texto
from banksense.logs import obter_logger

log = obter_logger("banksense.gerador")

SENTIMENTOS = ("negativo", "neutro", "positivo")

PROBS_RUIDO_TEXTO = {
    "minusculas": P.PROB_MINUSCULAS,
    "sem_acentos": P.PROB_SEM_ACENTOS,
    "abreviacoes": P.PROB_ABREVIACOES,
    "erro_digitacao": P.PROB_ERRO_DIGITACAO,
    "giria": P.PROB_GIRIA,
    "emoji": P.PROB_EMOJI,
    "pontuacao_excessiva": P.PROB_PONTUACAO_EXCESSIVA,
    "caixa_alta_negativo": P.PROB_CAIXA_ALTA_NEGATIVO,
}


def _sortear(rng: np.random.Generator, distribuicao: dict[str, float], n: int) -> np.ndarray:
    chaves = list(distribuicao)
    pesos = np.array(list(distribuicao.values()), dtype=float)
    return rng.choice(chaves, size=n, p=pesos / pesos.sum())


def gerar_clientes(rng: np.random.Generator, n: int = P.N_CLIENTES) -> pd.DataFrame:
    """Gera a tabela de clientes sintéticos."""
    dias_cadastro = rng.integers(0, 365 * 6, size=n)
    return pd.DataFrame(
        {
            "id_cliente": [f"CLI-{i:06d}" for i in range(1, n + 1)],
            "regiao": _sortear(rng, P.REGIOES, n),
            "segmento": _sortear(rng, P.SEGMENTOS, n),
            "faixa_etaria": _sortear(rng, P.FAIXAS_ETARIAS, n),
            "data_cadastro": [P.DATA_INICIO - timedelta(days=int(d)) for d in dias_cadastro],
        }
    )


def _pesos_diarios() -> tuple[list[date], np.ndarray]:
    """Peso de volume de cada dia: dia da semana x crescimento x início do mês x evento."""
    total_dias = (P.DATA_FIM - P.DATA_INICIO).days + 1
    dias = [P.DATA_INICIO + timedelta(days=i) for i in range(total_dias)]
    pesos = np.empty(total_dias)
    for i, d in enumerate(dias):
        peso = P.PESO_DIA_SEMANA[d.weekday()]
        peso *= 1 + P.CRESCIMENTO_NO_PERIODO * i / (total_dias - 1)
        if d.day <= 5:
            peso *= P.PESO_INICIO_DO_MES
        if P.EVENTO_INICIO <= d <= P.EVENTO_FIM:
            peso *= P.EVENTO_MULT_VOLUME
        pesos[i] = peso
    return dias, pesos / pesos.sum()


def _sentimento(rng: np.random.Generator, categoria: str, no_evento: bool) -> str:
    if no_evento and categoria in P.EVENTO_CATEGORIAS:
        if rng.random() < P.EVENTO_PROB_NEGATIVO:
            return "negativo"
        _, neu, pos = P.SENTIMENTO_POR_CATEGORIA[categoria]
        return "neutro" if rng.random() < neu / (neu + pos) else "positivo"
    probs = P.SENTIMENTO_POR_CATEGORIA[categoria]
    return SENTIMENTOS[int(rng.choice(3, p=probs))]


def _tempo_resolucao(rng: np.random.Generator, canal: str, categoria: str, sentimento: str) -> float:
    mediana = P.MEDIANA_HORAS_POR_CANAL[canal] * P.MULT_TEMPO_CATEGORIA.get(categoria, 1.0)
    if sentimento == "negativo":
        mediana *= P.MULT_TEMPO_NEGATIVO
    return round(float(rng.lognormal(np.log(mediana), P.SIGMA_LOG_TEMPO)), 2)


def gerar_mensagens_limpas(
    rng: np.random.Generator, clientes: pd.DataFrame, n: int = P.N_MENSAGENS
) -> pd.DataFrame:
    """Gera as mensagens sem sujeira (a versão "verdadeira" antes dos problemas de qualidade)."""
    dias, pesos = _pesos_diarios()
    idx_dias = rng.choice(len(dias), size=n, p=pesos)
    datas = [dias[i] for i in idx_dias]

    pesos_clientes = rng.gamma(P.FORMA_GAMA_CLIENTE, 1.0, size=len(clientes))
    idx_clientes = rng.choice(len(clientes), size=n, p=pesos_clientes / pesos_clientes.sum())
    canais = _sortear(rng, P.CANAIS, n)
    categorias_base = _sortear(rng, P.CATEGORIAS, n)

    registros = []
    limite_recente = P.DATA_FIM - timedelta(days=P.DIAS_RECENTES)
    for i in range(n):
        d = datas[i]
        no_evento = P.EVENTO_INICIO <= d <= P.EVENTO_FIM
        categoria = str(categorias_base[i])
        if no_evento and rng.random() < P.EVENTO_PROB_CATEGORIA:
            categoria = P.EVENTO_CATEGORIAS[int(rng.integers(len(P.EVENTO_CATEGORIAS)))]

        sentimento = _sentimento(rng, categoria, no_evento)
        texto, tipo = montar_texto(rng, categoria, sentimento)
        texto = aplicar_ruido(rng, texto, sentimento, PROBS_RUIDO_TEXTO)

        rotulo = sentimento
        if rng.random() < P.PROB_RUIDO_ROTULO:
            rotulo = str(rng.choice([s for s in SENTIMENTOS if s != sentimento]))
            tipo = "rotulo_ruidoso"

        nota = int(rng.choice(5, p=P.NOTA_POR_SENTIMENTO[sentimento])) + 1
        dist_situacao = P.SITUACOES_RECENTES if d > limite_recente else P.SITUACOES
        situacao = str(_sortear(rng, dist_situacao, 1)[0])
        canal = str(canais[i])
        tempo = (
            _tempo_resolucao(rng, canal, categoria, sentimento)
            if situacao in ("resolvida", "cancelada")
            else np.nan
        )
        cliente = clientes.iloc[idx_clientes[i]]
        registros.append(
            {
                "id_mensagem": f"MSG-{i + 1:07d}",
                "id_cliente": cliente["id_cliente"],
                "data_mensagem": d.isoformat(),
                "canal": canal,
                "categoria": categoria,
                "texto": texto,
                "sentimento_referencia": rotulo,
                "nota_satisfacao": nota,
                "tempo_resolucao_horas": tempo,
                "regiao": cliente["regiao"],
                "situacao": situacao,
                "tipo_texto": tipo,  # metadado do gerador: não existe em dados reais
            }
        )
    return pd.DataFrame(registros)


def _variacao_texto(rng: np.random.Generator, valor: str, extras: list[str]) -> str:
    """Escolhe uma variação suja de um valor categórico (maiúsculas, espaços, sinônimos)."""
    opcoes = [valor.upper(), valor.title(), f" {valor} ", f"{valor.capitalize()} ", *extras]
    return opcoes[int(rng.integers(len(opcoes)))]


SINONIMOS_CANAL = {"app": ["aplicativo", "App Mobile"], "chat": ["whatsapp", "Chat Online"],
                   "telefone": ["fone", "0800"], "email": ["e-mail", "E-Mail"],
                   "redes_sociais": ["instagram", "Redes Sociais"], "ouvidoria": ["Ouvidoria "]}
SIGLAS_REGIAO = {"Sudeste": ["SE", "sudeste"], "Nordeste": ["NE", "nordeste"], "Sul": ["S", "sul"],
                 "Norte": ["N", "norte"], "Centro-Oeste": ["CO", "centro oeste", "Centro Oeste"]}


def sujar_dados(rng: np.random.Generator, df: pd.DataFrame) -> pd.DataFrame:
    """Insere problemas de qualidade controlados: nulos, duplicatas e inconsistências."""
    df = df.copy()
    n = len(df)
    df["nota_satisfacao"] = df["nota_satisfacao"].astype("float")

    def mascara(prob: float) -> np.ndarray:
        return rng.random(n) < prob

    for i in np.where(mascara(P.PROB_CANAL_INCONSISTENTE))[0]:
        v = df.at[i, "canal"]
        df.at[i, "canal"] = _variacao_texto(rng, v, SINONIMOS_CANAL.get(v, []))
    for i in np.where(mascara(P.PROB_REGIAO_INCONSISTENTE))[0]:
        v = df.at[i, "regiao"]
        df.at[i, "regiao"] = _variacao_texto(rng, v, SIGLAS_REGIAO.get(v, []))
    for i in np.where(mascara(P.PROB_CATEGORIA_INCONSISTENTE))[0]:
        v = df.at[i, "categoria"]
        df.at[i, "categoria"] = _variacao_texto(rng, v, [v.replace("_", " ")])
    for i in np.where(mascara(P.PROB_SENTIMENTO_INCONSISTENTE))[0]:
        df.at[i, "sentimento_referencia"] = _variacao_texto(rng, df.at[i, "sentimento_referencia"], [])
    for i in np.where(mascara(P.PROB_DATA_FORMATO_BR))[0]:
        df.at[i, "data_mensagem"] = date.fromisoformat(df.at[i, "data_mensagem"]).strftime("%d/%m/%Y")

    fora = mascara(P.PROB_NOTA_FORA_DA_FAIXA)
    df.loc[fora, "nota_satisfacao"] = rng.choice([0, 6, 10, -1], size=int(fora.sum()))

    tem_tempo = df["tempo_resolucao_horas"].notna().to_numpy()
    neg = mascara(P.PROB_TEMPO_NEGATIVO) & tem_tempo
    df.loc[neg, "tempo_resolucao_horas"] = -df.loc[neg, "tempo_resolucao_horas"]
    extremo = mascara(P.PROB_TEMPO_EXTREMO) & tem_tempo & ~neg
    df.loc[extremo, "tempo_resolucao_horas"] = (df.loc[extremo, "tempo_resolucao_horas"] * 50).round(2)

    for coluna, prob in P.PROB_NULO.items():
        df.loc[mascara(prob), coluna] = np.nan

    duplicar = df[mascara(P.PROB_LINHA_DUPLICADA)]
    df = pd.concat([df, duplicar], ignore_index=True)
    return df.sample(frac=1.0, random_state=int(rng.integers(1_000_000))).reset_index(drop=True)


def gerar(n: int = P.N_MENSAGENS, semente: int = config.SEMENTE_PADRAO) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gera (clientes, mensagens_brutas) de forma reproduzível."""
    rng = np.random.default_rng(semente)
    clientes = gerar_clientes(rng)
    mensagens = gerar_mensagens_limpas(rng, clientes, n)
    return clientes, sujar_dados(rng, mensagens)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera os dados sintéticos do BankSense AI.")
    parser.add_argument("--n", type=int, default=P.N_MENSAGENS, help="quantidade de mensagens")
    parser.add_argument("--semente", type=int, default=config.SEMENTE_PADRAO)
    args = parser.parse_args()

    log.info("Geração iniciada: %s mensagens, semente %s", f"{args.n:,}", args.semente)
    clientes, mensagens = gerar(args.n, args.semente)
    config.DIR_BRUTOS.mkdir(parents=True, exist_ok=True)
    clientes.to_csv(config.ARQ_CLIENTES_BRUTO, index=False, encoding="utf-8")
    mensagens.to_csv(config.ARQ_MENSAGENS_BRUTO, index=False, encoding="utf-8")
    log.info("Clientes: %s -> %s", f"{len(clientes):,}", config.ARQ_CLIENTES_BRUTO)
    log.info("Mensagens brutas: %s -> %s", f"{len(mensagens):,}", config.ARQ_MENSAGENS_BRUTO)


if __name__ == "__main__":
    main()
