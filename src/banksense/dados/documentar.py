"""Gera docs/premissas_geracao.md a partir de premissas.py (fonte única dos números).

Uso:
    python -m banksense.dados.documentar
"""

from __future__ import annotations

from banksense import config
from banksense.dados import premissas as P


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%".replace(".", ",")


def _tabela(titulo_chave: str, dist: dict[str, float]) -> str:
    linhas = [f"| {titulo_chave} | Probabilidade |", "|---|---|"]
    linhas += [f"| {k} | {_pct(v)} |" for k, v in dist.items()]
    return "\n".join(linhas)


def gerar_markdown() -> str:
    sent = ["| Categoria | Negativo | Neutro | Positivo |", "|---|---|---|---|"]
    sent += [f"| {c} | {_pct(a)} | {_pct(b)} | {_pct(d)} |" for c, (a, b, d) in P.SENTIMENTO_POR_CATEGORIA.items()]
    notas = ["| Sentimento | 1 | 2 | 3 | 4 | 5 |", "|---|---|---|---|---|---|"]
    notas += [f"| {s} | " + " | ".join(_pct(x) for x in ps) + " |" for s, ps in P.NOTA_POR_SENTIMENTO.items()]
    tempo = ["| Canal | Mediana (horas) |", "|---|---|"]
    tempo += [f"| {c} | {h} |" for c, h in P.MEDIANA_HORAS_POR_CANAL.items()]
    mult = ", ".join(f"{c} x{m}" for c, m in P.MULT_TEMPO_CATEGORIA.items())
    nulos = ", ".join(f"`{c}` {_pct(p)}" for c, p in P.PROB_NULO.items())
    dias = ", ".join(f"{d} {p}" for d, p in zip(["seg", "ter", "qua", "qui", "sex", "sáb", "dom"], P.PESO_DIA_SEMANA))

    return f"""# Premissas da geração de dados sintéticos

> **Aviso:** todos os dados do BankSense AI são **sintéticos**. Os números abaixo são escolhas
> de simulação feitas para estudo. Eles **não** são estatísticas reais de bancos brasileiros e
> nenhum resultado do projeto deve ser lido como evidência sobre o mercado.

Arquivo gerado automaticamente por `python -m banksense.dados.documentar` a partir de
`src/banksense/dados/premissas.py`. Semente padrão: **{config.SEMENTE_PADRAO}**.

## Volume e período

- {P.N_MENSAGENS:,} mensagens de {P.N_CLIENTES:,} clientes, de {P.DATA_INICIO:%d/%m/%Y} a {P.DATA_FIM:%d/%m/%Y}.
- Cada cliente recebe um peso sorteado de uma distribuição gama (forma {P.FORMA_GAMA_CLIENTE}):
  poucos clientes escrevem muitas mensagens, a maioria escreve poucas.

## Clientes

{_tabela("Região", P.REGIOES)}

{_tabela("Segmento", P.SEGMENTOS)}

{_tabela("Faixa etária", P.FAIXAS_ETARIAS)}

## Mensagens

{_tabela("Canal", P.CANAIS)}

{_tabela("Categoria", P.CATEGORIAS)}

### Sentimento de referência por categoria

{chr(10).join(sent)}

### Nota de satisfação por sentimento

{chr(10).join(notas)}

### Tempo de resolução

Log-normal com mediana = mediana do canal × multiplicador da categoria × {P.MULT_TEMPO_NEGATIVO}
(se negativo), e desvio-padrão do log = {P.SIGMA_LOG_TEMPO}. Multiplicadores: {mult}; demais categorias x1.
Mensagens `aberta` ou `em_andamento` não têm tempo de resolução (nulo esperado, não é erro).

{chr(10).join(tempo)}

### Situação

{_tabela("Situação", P.SITUACOES)}

Nos últimos {P.DIAS_RECENTES} dias do período:

{_tabela("Situação (recentes)", P.SITUACOES_RECENTES)}

## Padrões temporais

- Peso por dia da semana: {dias}.
- Crescimento de {_pct(P.CRESCIMENTO_NO_PERIODO)} no volume do início ao fim do período.
- Dias 1 a 5 de cada mês: volume x{P.PESO_INICIO_DO_MES}.
- **Evento simulado** de instabilidade no aplicativo, de {P.EVENTO_INICIO:%d/%m/%Y} a {P.EVENTO_FIM:%d/%m/%Y}:
  volume x{P.EVENTO_MULT_VOLUME}; {_pct(P.EVENTO_PROB_CATEGORIA)} das mensagens viram
  {" ou ".join(P.EVENTO_CATEGORIAS)}, e {_pct(P.EVENTO_PROB_NEGATIVO)} delas são negativas.

## Linguagem

Ambiguidades (sorteadas dentro de cada sentimento):

- Ironia (negativo com palavras positivas): {_pct(P.PROB_IRONIA)}
- Negação positiva ("não tenho do que reclamar"): {_pct(P.PROB_NEGACAO_POSITIVA)}
- Mensagem mista (elogio e crítica): {_pct(P.PROB_MISTO)}
- Pergunta neutra que cita um problema: {_pct(P.PROB_NEUTRO_CARREGADO)}
- Ruído de rotulagem (rótulo trocado ao acaso): {_pct(P.PROB_RUIDO_ROTULO)}

Ruído de escrita: minúsculas {_pct(P.PROB_MINUSCULAS)}, sem acentos {_pct(P.PROB_SEM_ACENTOS)},
abreviações {_pct(P.PROB_ABREVIACOES)}, erro de digitação {_pct(P.PROB_ERRO_DIGITACAO)},
gíria {_pct(P.PROB_GIRIA)}, emoji {_pct(P.PROB_EMOJI)}, pontuação excessiva {_pct(P.PROB_PONTUACAO_EXCESSIVA)},
caixa alta em negativos {_pct(P.PROB_CAIXA_ALTA_NEGATIVO)}.

A coluna `tipo_texto` registra como cada texto foi construído (`direto`, `ironia`, `misto`...).
Ela é um **metadado do gerador**, serve só para análise de erros e **não** é usada como variável do modelo.

## Problemas de qualidade inseridos de propósito

- Nulos: {nulos}.
- Linhas duplicadas: {_pct(P.PROB_LINHA_DUPLICADA)}.
- Canal escrito de outro jeito (maiúsculas, espaços, sinônimos): {_pct(P.PROB_CANAL_INCONSISTENTE)}.
- Região inconsistente (siglas, minúsculas): {_pct(P.PROB_REGIAO_INCONSISTENTE)}.
- Categoria inconsistente: {_pct(P.PROB_CATEGORIA_INCONSISTENTE)}.
- Sentimento inconsistente (maiúsculas, espaços): {_pct(P.PROB_SENTIMENTO_INCONSISTENTE)}.
- Data no formato dd/mm/aaaa em vez de ISO: {_pct(P.PROB_DATA_FORMATO_BR)}.
- Nota fora da faixa 1 a 5: {_pct(P.PROB_NOTA_FORA_DA_FAIXA)}.
- Tempo de resolução negativo: {_pct(P.PROB_TEMPO_NEGATIVO)}.
- Tempo de resolução extremo (x50): {_pct(P.PROB_TEMPO_EXTREMO)}.
"""


def main() -> None:
    destino = config.RAIZ / "docs" / "premissas_geracao.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(gerar_markdown(), encoding="utf-8")
    print(f"Documentação gerada em {destino}")


if __name__ == "__main__":
    main()
