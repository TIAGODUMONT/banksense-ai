# Relatório de qualidade dos dados

> Dados **sintéticos**. Gerado por `python -m banksense.dados.limpeza`.

## Resumo

| Item | Quantidade |
|---|---|
| Linhas brutas | 50,616 |
| Duplicatas exatas removidas | 616 |
| Linhas sem texto removidas | 722 |
| **Linhas tratadas** | **49,278** |
| Datas no formato dd/mm/aaaa convertidas | 2,522 |
| Datas inválidas | 0 |
| Notas fora de 1 a 5 (viraram nulo) | 231 |
| Tempos de resolução negativos (viraram nulo) | 132 |
| Tempos sinalizados como outlier (limite por canal) | 60 |
| Regiões faltantes preenchidas pelo cadastro do cliente | 504 |
| IDs de mensagem repetidos após a limpeza | 0 |

## Valores distintos (antes e depois da padronização)

| Coluna | Antes | Depois |
|---|---|---|
| canal | 40 | 6 |
| regiao | 31 | 5 |
| categoria | 48 | 9 |
| sentimento_referencia | 15 | 3 |

Valores que continuaram fora do domínio após a padronização (viraram nulo):
`canal` 0, `regiao` 0, `categoria` 0, `sentimento_referencia` 0, `situacao` 0.

## Nulos por coluna

| Coluna | Antes | Depois |
|---|---|---|
| id_mensagem | 0 | 0 |
| id_cliente | 0 | 0 |
| data_mensagem | 0 | 0 |
| canal | 997 | 965 |
| categoria | 0 | 0 |
| texto | 729 | 0 |
| sentimento_referencia | 0 | 0 |
| nota_satisfacao | 1,524 | 1,701 |
| tempo_resolucao_horas | 9,027 | 8,936 |
| regiao | 509 | 0 |
| situacao | 0 | 0 |
| tipo_texto | 0 | 0 |

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
   Limites em horas: app 504.5, chat 94.7, email 3,326.1, ouvidoria 10,886.3, redes_sociais 1,136.9, telefone 65.0.
8. Linhas sem texto são removidas.
