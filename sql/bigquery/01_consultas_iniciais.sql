-- BankSense AI no BigQuery (projeto banksense-ai, dataset banksense)
-- Tabelas: fato_mensagens (49.278 linhas) e dim_clientes (12.000 linhas), carregadas
-- a partir dos arquivos Parquet de data/processed/. Dados SINTÉTICOS.

-- 1. Reclamações e satisfação por segmento de cliente (JOIN + GROUP BY)
SELECT
  c.segmento,
  COUNT(*) AS mensagens,
  ROUND(AVG(m.nota_satisfacao), 2) AS nota_media,
  ROUND(100 * COUNTIF(m.sentimento_referencia = 'negativo') / COUNT(*), 1) AS pct_negativas
FROM `banksense-ai.banksense.fato_mensagens` AS m
JOIN `banksense-ai.banksense.dim_clientes` AS c USING (id_cliente)
GROUP BY c.segmento
ORDER BY pct_negativas DESC;

-- 2. Mensagens negativas por mês: o pico da instabilidade do app aparece em novembro de 2025
--    (resultado: 64,6% negativas e 1.320 mensagens sobre o aplicativo, contra cerca de 48% e 300 nos outros meses)
SELECT
  FORMAT_DATE('%Y-%m', DATE(data_mensagem)) AS mes,
  COUNT(*) AS total,
  COUNTIF(sentimento_referencia = 'negativo') AS negativas,
  ROUND(100 * COUNTIF(sentimento_referencia = 'negativo') / COUNT(*), 1) AS pct_negativas,
  COUNTIF(categoria = 'aplicativo') AS sobre_aplicativo
FROM `banksense-ai.banksense.fato_mensagens`
GROUP BY mes
ORDER BY mes;

-- 3. Tempo de resolução por canal, ignorando outliers sinalizados na limpeza
SELECT
  canal,
  ROUND(APPROX_QUANTILES(tempo_resolucao_horas, 2)[OFFSET(1)], 1) AS mediana_horas,
  ROUND(AVG(tempo_resolucao_horas), 1) AS media_horas
FROM `banksense-ai.banksense.fato_mensagens`
WHERE situacao = 'resolvida' AND NOT tempo_outlier
GROUP BY canal
ORDER BY mediana_horas;

-- 4. Top 3 categorias com mais reclamações em cada região (função de janela)
SELECT regiao, categoria, negativas
FROM (
  SELECT
    regiao,
    categoria,
    COUNTIF(sentimento_referencia = 'negativo') AS negativas,
    ROW_NUMBER() OVER (PARTITION BY regiao ORDER BY COUNTIF(sentimento_referencia = 'negativo') DESC) AS posicao
  FROM `banksense-ai.banksense.fato_mensagens`
  WHERE regiao IS NOT NULL
  GROUP BY regiao, categoria
)
WHERE posicao <= 3
ORDER BY regiao, negativas DESC;
