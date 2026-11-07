-- 002: índices para as consultas mais comuns do dashboard e das análises

CREATE INDEX IF NOT EXISTS idx_mensagens_data        ON mensagens (data_mensagem);
CREATE INDEX IF NOT EXISTS idx_mensagens_categoria   ON mensagens (categoria);
CREATE INDEX IF NOT EXISTS idx_mensagens_cliente     ON mensagens (id_cliente);
CREATE INDEX IF NOT EXISTS idx_mensagens_sentimento  ON mensagens (sentimento_referencia);
CREATE INDEX IF NOT EXISTS idx_mensagens_data_categ  ON mensagens (data_mensagem, categoria);
CREATE INDEX IF NOT EXISTS idx_atendimentos_situacao ON atendimentos (situacao);
CREATE INDEX IF NOT EXISTS idx_prev_sent_criado      ON previsoes_sentimento (criado_em);
CREATE INDEX IF NOT EXISTS idx_prev_volume_data      ON previsoes_volume (data_referencia, modelo);
