-- 001: tabelas principais do BankSense AI (dados sintéticos)

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente      VARCHAR(12) PRIMARY KEY,
    regiao          VARCHAR(20) NOT NULL,
    segmento        VARCHAR(20) NOT NULL,
    faixa_etaria    VARCHAR(10) NOT NULL,
    data_cadastro   DATE        NOT NULL
);

CREATE TABLE IF NOT EXISTS mensagens (
    id_mensagem            VARCHAR(12) PRIMARY KEY,
    id_cliente             VARCHAR(12) NOT NULL REFERENCES clientes (id_cliente),
    data_mensagem          DATE        NOT NULL,
    canal                  VARCHAR(20),
    categoria              VARCHAR(30) NOT NULL,
    texto                  TEXT        NOT NULL,
    sentimento_referencia  VARCHAR(10) NOT NULL
        CHECK (sentimento_referencia IN ('negativo', 'neutro', 'positivo')),
    regiao                 VARCHAR(20)
);

-- Um atendimento por mensagem: situação, nota e tempo de resolução
CREATE TABLE IF NOT EXISTS atendimentos (
    id_atendimento         BIGSERIAL PRIMARY KEY,
    id_mensagem            VARCHAR(12) NOT NULL UNIQUE REFERENCES mensagens (id_mensagem) ON DELETE CASCADE,
    situacao               VARCHAR(15) NOT NULL
        CHECK (situacao IN ('aberta', 'em_andamento', 'resolvida', 'cancelada')),
    nota_satisfacao        SMALLINT CHECK (nota_satisfacao BETWEEN 1 AND 5),
    tempo_resolucao_horas  NUMERIC(10, 2) CHECK (tempo_resolucao_horas >= 0)
);

-- Previsões de sentimento feitas pelo modelo (API e lotes)
CREATE TABLE IF NOT EXISTS previsoes_sentimento (
    id                   BIGSERIAL PRIMARY KEY,
    id_mensagem          VARCHAR(12) REFERENCES mensagens (id_mensagem) ON DELETE SET NULL,
    texto                TEXT        NOT NULL,
    sentimento_previsto  VARCHAR(10) NOT NULL
        CHECK (sentimento_previsto IN ('negativo', 'neutro', 'positivo')),
    prob_negativo        NUMERIC(5, 4),
    prob_neutro          NUMERIC(5, 4),
    prob_positivo        NUMERIC(5, 4),
    versao_modelo        VARCHAR(40) NOT NULL,
    criado_em            TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Previsões do volume diário de reclamações
CREATE TABLE IF NOT EXISTS previsoes_volume (
    id                BIGSERIAL PRIMARY KEY,
    data_referencia   DATE           NOT NULL,
    volume_previsto   NUMERIC(10, 2) NOT NULL,
    limite_inferior   NUMERIC(10, 2),
    limite_superior   NUMERIC(10, 2),
    modelo            VARCHAR(40)    NOT NULL,
    criado_em         TIMESTAMPTZ    NOT NULL DEFAULT now()
);
