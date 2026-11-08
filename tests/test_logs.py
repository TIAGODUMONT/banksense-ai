"""Testes da configuração de logs."""

import logging

from banksense.logs import obter_logger


def test_logger_fica_sob_banksense_e_registra(caplog):
    log = obter_logger("banksense.teste")
    raiz = logging.getLogger("banksense")
    raiz.addHandler(caplog.handler)  # o logger do projeto não propaga para a raiz
    try:
        log.info("mensagem de teste")
    finally:
        raiz.removeHandler(caplog.handler)
    assert "mensagem de teste" in caplog.text


def test_configuracao_nao_duplica_manipuladores():
    obter_logger("banksense.a")
    antes = len(logging.getLogger("banksense").handlers)
    obter_logger("banksense.b")
    assert len(logging.getLogger("banksense").handlers) == antes
