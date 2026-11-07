-- Consultas de exemplo para explorar o banco (dados sintéticos)
-- Rodar com: docker exec -it banksense-postgres psql -U banksense -d banksense

-- 1. Sentimento negativo e nota média por categoria
SELECT m.categoria,
       count(*)                                                        AS total,
       round(100.0 * avg((m.sentimento_referencia = 'negativo')::int), 1) AS pct_negativo,
       round(avg(a.nota_satisfacao), 2)                                AS nota_media
FROM mensagens m
JOIN atendimentos a USING (id_mensagem)
GROUP BY m.categoria
ORDER BY pct_negativo DESC;

-- 2. Volume semanal de reclamações (mensagens negativas)
SELECT date_trunc('week', data_mensagem)::date AS semana,
       count(*)                                AS reclamacoes
FROM mensagens
WHERE sentimento_referencia = 'negativo'
GROUP BY 1
ORDER BY 1;

-- 3. Tempo mediano de resolução por canal (só atendimentos resolvidos)
SELECT m.canal,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY a.tempo_resolucao_horas) AS mediana_horas,
       count(*)                                                            AS atendimentos
FROM mensagens m
JOIN atendimentos a USING (id_mensagem)
WHERE a.situacao = 'resolvida' AND a.tempo_resolucao_horas IS NOT NULL
GROUP BY m.canal
ORDER BY mediana_horas;

-- 4. Clientes que mais escreveram e o percentual negativo de cada um
SELECT c.id_cliente, c.segmento, c.regiao,
       count(*)                                                        AS mensagens,
       round(100.0 * avg((m.sentimento_referencia = 'negativo')::int), 1) AS pct_negativo
FROM clientes c
JOIN mensagens m USING (id_cliente)
GROUP BY c.id_cliente, c.segmento, c.regiao
ORDER BY mensagens DESC
LIMIT 10;
