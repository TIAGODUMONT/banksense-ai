"""Premissas da geração de dados sintéticos.

TODOS os números deste arquivo são escolhas de simulação, feitas para o estudo.
Eles NÃO representam estatísticas reais de bancos brasileiros.

Este módulo é a fonte única das probabilidades: o gerador usa estes valores
e a documentação (docs/premissas_geracao.md) é gerada a partir deles.
"""

from __future__ import annotations

from datetime import date

# ---------------------------------------------------------------------------
# Volume e período
# ---------------------------------------------------------------------------
N_MENSAGENS = 50_000
N_CLIENTES = 12_000
DATA_INICIO = date(2025, 1, 1)
DATA_FIM = date(2026, 6, 30)

# ---------------------------------------------------------------------------
# Distribuições categóricas (somam 1)
# ---------------------------------------------------------------------------
REGIOES: dict[str, float] = {
    "Sudeste": 0.43,
    "Nordeste": 0.26,
    "Sul": 0.14,
    "Norte": 0.09,
    "Centro-Oeste": 0.08,
}

SEGMENTOS: dict[str, float] = {
    "varejo": 0.70,
    "alta_renda": 0.12,
    "universitario": 0.10,
    "pj_mei": 0.08,
}

FAIXAS_ETARIAS: dict[str, float] = {
    "18-24": 0.18,
    "25-34": 0.30,
    "35-44": 0.24,
    "45-59": 0.19,
    "60+": 0.09,
}

CANAIS: dict[str, float] = {
    "app": 0.38,
    "chat": 0.22,
    "telefone": 0.15,
    "redes_sociais": 0.12,
    "email": 0.08,
    "ouvidoria": 0.05,
}

CATEGORIAS: dict[str, float] = {
    "cartao_credito": 0.20,
    "pix": 0.18,
    "conta_corrente": 0.12,
    "aplicativo": 0.12,
    "emprestimo": 0.10,
    "tarifas": 0.09,
    "investimentos": 0.07,
    "atendimento": 0.07,
    "fraude_seguranca": 0.05,
}

# Sentimento de referência condicionado à categoria: (negativo, neutro, positivo)
SENTIMENTO_POR_CATEGORIA: dict[str, tuple[float, float, float]] = {
    "cartao_credito": (0.50, 0.28, 0.22),
    "pix": (0.45, 0.30, 0.25),
    "conta_corrente": (0.40, 0.35, 0.25),
    "aplicativo": (0.50, 0.25, 0.25),
    "emprestimo": (0.45, 0.33, 0.22),
    "tarifas": (0.65, 0.25, 0.10),
    "investimentos": (0.25, 0.40, 0.35),
    "atendimento": (0.48, 0.17, 0.35),
    "fraude_seguranca": (0.75, 0.18, 0.07),
}

# Nota de satisfação (1 a 5) condicionada ao sentimento
NOTA_POR_SENTIMENTO: dict[str, tuple[float, float, float, float, float]] = {
    "negativo": (0.45, 0.30, 0.15, 0.07, 0.03),
    "neutro": (0.08, 0.17, 0.45, 0.20, 0.10),
    "positivo": (0.02, 0.04, 0.14, 0.35, 0.45),
}

# ---------------------------------------------------------------------------
# Tempo de resolução (horas): log-normal
#   mediana = MEDIANA_CANAL * MULT_CATEGORIA * MULT_SENTIMENTO
# ---------------------------------------------------------------------------
MEDIANA_HORAS_POR_CANAL: dict[str, float] = {
    "telefone": 1.5,
    "chat": 2.0,
    "app": 6.0,
    "redes_sociais": 12.0,
    "email": 30.0,
    "ouvidoria": 96.0,
}
MULT_TEMPO_CATEGORIA: dict[str, float] = {
    "fraude_seguranca": 1.8,
    "emprestimo": 1.5,
    "tarifas": 1.2,
}  # demais categorias: 1.0
MULT_TEMPO_NEGATIVO = 1.6
SIGMA_LOG_TEMPO = 0.9

# Situação da reclamação
SITUACOES: dict[str, float] = {
    "resolvida": 0.78,
    "em_andamento": 0.10,
    "aberta": 0.07,
    "cancelada": 0.05,
}
# Nos últimos dias do período, muitas mensagens ainda não foram resolvidas
DIAS_RECENTES = 10
SITUACOES_RECENTES: dict[str, float] = {
    "aberta": 0.35,
    "em_andamento": 0.25,
    "resolvida": 0.37,
    "cancelada": 0.03,
}

# ---------------------------------------------------------------------------
# Padrões temporais do volume
# ---------------------------------------------------------------------------
PESO_DIA_SEMANA = (1.20, 1.10, 1.05, 1.05, 1.00, 0.70, 0.60)  # segunda .. domingo
CRESCIMENTO_NO_PERIODO = 0.25  # base de clientes cresce 25% do início ao fim
PESO_INICIO_DO_MES = 1.15  # dias 1 a 5 (pagamento de salário e faturas)

# Evento simulado: instabilidade no aplicativo
EVENTO_INICIO = date(2025, 11, 10)
EVENTO_FIM = date(2025, 11, 24)
EVENTO_MULT_VOLUME = 2.5  # no período, o volume diário fica 2,5 vezes maior
EVENTO_CATEGORIAS = ("aplicativo", "pix")
EVENTO_PROB_CATEGORIA = 0.6  # 60% das mensagens do evento são de app/pix
EVENTO_PROB_NEGATIVO = 0.80

# Distribuição de mensagens por cliente: pesos gama (poucos clientes escrevem muito)
FORMA_GAMA_CLIENTE = 0.8

# ---------------------------------------------------------------------------
# Linguagem: ambiguidade e ruído no texto
# ---------------------------------------------------------------------------
PROB_IRONIA = 0.05  # negativo escrito com palavras positivas
PROB_NEGACAO_POSITIVA = 0.06  # positivo escrito com "não" ("não tenho do que reclamar")
PROB_MISTO = 0.08  # elogio + crítica na mesma mensagem
PROB_NEUTRO_CARREGADO = 0.08  # pergunta neutra citando um problema
PROB_RUIDO_ROTULO = 0.02  # rótulo trocado ao acaso (discordância entre anotadores)

PROB_MINUSCULAS = 0.40
PROB_SEM_ACENTOS = 0.25
PROB_ABREVIACOES = 0.30
PROB_ERRO_DIGITACAO = 0.12
PROB_GIRIA = 0.10
PROB_EMOJI = 0.08
PROB_PONTUACAO_EXCESSIVA = 0.10
PROB_CAIXA_ALTA_NEGATIVO = 0.05

# ---------------------------------------------------------------------------
# Sujeira proposital nos dados brutos (para praticar Data Cleaning)
# ---------------------------------------------------------------------------
PROB_NULO: dict[str, float] = {
    "texto": 0.015,
    "canal": 0.02,
    "nota_satisfacao": 0.03,
    "regiao": 0.01,
}
PROB_LINHA_DUPLICADA = 0.012
PROB_CANAL_INCONSISTENTE = 0.05
PROB_REGIAO_INCONSISTENTE = 0.04
PROB_CATEGORIA_INCONSISTENTE = 0.02
PROB_SENTIMENTO_INCONSISTENTE = 0.03
PROB_DATA_FORMATO_BR = 0.05
PROB_NOTA_FORA_DA_FAIXA = 0.005
PROB_TEMPO_NEGATIVO = 0.003
PROB_TEMPO_EXTREMO = 0.003  # tempo multiplicado por 50 (outlier)
