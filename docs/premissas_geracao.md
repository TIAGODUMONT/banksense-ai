# Premissas da geração de dados sintéticos

> **Aviso:** todos os dados do BankSense AI são **sintéticos**. Os números abaixo são escolhas
> de simulação feitas para estudo. Eles **não** são estatísticas reais de bancos brasileiros e
> nenhum resultado do projeto deve ser lido como evidência sobre o mercado.

Arquivo gerado automaticamente por `python -m banksense.dados.documentar` a partir de
`src/banksense/dados/premissas.py`. Semente padrão: **42**.

## Volume e período

- 50,000 mensagens de 12,000 clientes, de 01/01/2025 a 30/06/2026.
- Cada cliente recebe um peso sorteado de uma distribuição gama (forma 0.8):
  poucos clientes escrevem muitas mensagens, a maioria escreve poucas.

## Clientes

| Região | Probabilidade |
|---|---|
| Sudeste | 43,0% |
| Nordeste | 26,0% |
| Sul | 14,0% |
| Norte | 9,0% |
| Centro-Oeste | 8,0% |

| Segmento | Probabilidade |
|---|---|
| varejo | 70,0% |
| alta_renda | 12,0% |
| universitario | 10,0% |
| pj_mei | 8,0% |

| Faixa etária | Probabilidade |
|---|---|
| 18-24 | 18,0% |
| 25-34 | 30,0% |
| 35-44 | 24,0% |
| 45-59 | 19,0% |
| 60+ | 9,0% |

## Mensagens

| Canal | Probabilidade |
|---|---|
| app | 38,0% |
| chat | 22,0% |
| telefone | 15,0% |
| redes_sociais | 12,0% |
| email | 8,0% |
| ouvidoria | 5,0% |

| Categoria | Probabilidade |
|---|---|
| cartao_credito | 20,0% |
| pix | 18,0% |
| conta_corrente | 12,0% |
| aplicativo | 12,0% |
| emprestimo | 10,0% |
| tarifas | 9,0% |
| investimentos | 7,0% |
| atendimento | 7,0% |
| fraude_seguranca | 5,0% |

### Sentimento de referência por categoria

| Categoria | Negativo | Neutro | Positivo |
|---|---|---|---|
| cartao_credito | 50,0% | 28,0% | 22,0% |
| pix | 45,0% | 30,0% | 25,0% |
| conta_corrente | 40,0% | 35,0% | 25,0% |
| aplicativo | 50,0% | 25,0% | 25,0% |
| emprestimo | 45,0% | 33,0% | 22,0% |
| tarifas | 65,0% | 25,0% | 10,0% |
| investimentos | 25,0% | 40,0% | 35,0% |
| atendimento | 48,0% | 17,0% | 35,0% |
| fraude_seguranca | 75,0% | 18,0% | 7,0% |

### Nota de satisfação por sentimento

| Sentimento | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| negativo | 45,0% | 30,0% | 15,0% | 7,0% | 3,0% |
| neutro | 8,0% | 17,0% | 45,0% | 20,0% | 10,0% |
| positivo | 2,0% | 4,0% | 14,0% | 35,0% | 45,0% |

### Tempo de resolução

Log-normal com mediana = mediana do canal × multiplicador da categoria × 1.6
(se negativo), e desvio-padrão do log = 0.9. Multiplicadores: fraude_seguranca x1.8, emprestimo x1.5, tarifas x1.2; demais categorias x1.
Mensagens `aberta` ou `em_andamento` não têm tempo de resolução (nulo esperado, não é erro).

| Canal | Mediana (horas) |
|---|---|
| telefone | 1.5 |
| chat | 2.0 |
| app | 6.0 |
| redes_sociais | 12.0 |
| email | 30.0 |
| ouvidoria | 96.0 |

### Situação

| Situação | Probabilidade |
|---|---|
| resolvida | 78,0% |
| em_andamento | 10,0% |
| aberta | 7,0% |
| cancelada | 5,0% |

Nos últimos 10 dias do período:

| Situação (recentes) | Probabilidade |
|---|---|
| aberta | 35,0% |
| em_andamento | 25,0% |
| resolvida | 37,0% |
| cancelada | 3,0% |

## Padrões temporais

- Peso por dia da semana: seg 1.2, ter 1.1, qua 1.05, qui 1.05, sex 1.0, sáb 0.7, dom 0.6.
- Crescimento de 25,0% no volume do início ao fim do período.
- Dias 1 a 5 de cada mês: volume x1.15.
- **Evento simulado** de instabilidade no aplicativo, de 10/11/2025 a 24/11/2025:
  volume x2.5; 60,0% das mensagens viram
  aplicativo ou pix, e 80,0% delas são negativas.

## Linguagem

Ambiguidades (sorteadas dentro de cada sentimento):

- Ironia (negativo com palavras positivas): 5,0%
- Negação positiva ("não tenho do que reclamar"): 6,0%
- Mensagem mista (elogio e crítica): 8,0%
- Pergunta neutra que cita um problema: 8,0%
- Ruído de rotulagem (rótulo trocado ao acaso): 2,0%

Ruído de escrita: minúsculas 40,0%, sem acentos 25,0%,
abreviações 30,0%, erro de digitação 12,0%,
gíria 10,0%, emoji 8,0%, pontuação excessiva 10,0%,
caixa alta em negativos 5,0%.

A coluna `tipo_texto` registra como cada texto foi construído (`direto`, `ironia`, `misto`...).
Ela é um **metadado do gerador**, serve só para análise de erros e **não** é usada como variável do modelo.

## Problemas de qualidade inseridos de propósito

- Nulos: `texto` 1,5%, `canal` 2,0%, `nota_satisfacao` 3,0%, `regiao` 1,0%.
- Linhas duplicadas: 1,2%.
- Canal escrito de outro jeito (maiúsculas, espaços, sinônimos): 5,0%.
- Região inconsistente (siglas, minúsculas): 4,0%.
- Categoria inconsistente: 2,0%.
- Sentimento inconsistente (maiúsculas, espaços): 3,0%.
- Data no formato dd/mm/aaaa em vez de ISO: 5,0%.
- Nota fora da faixa 1 a 5: 0,5%.
- Tempo de resolução negativo: 0,3%.
- Tempo de resolução extremo (x50): 0,3%.
