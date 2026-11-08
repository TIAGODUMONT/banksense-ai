"""Configuração de logs do projeto: mensagens no terminal e no arquivo logs/banksense.log.

Uso em qualquer módulo:
    from banksense.logs import obter_logger
    log = obter_logger(__name__)
    log.info("Mensagem")
"""

from __future__ import annotations

import logging
import os
import sys

from banksense import config

DIR_LOGS = config.RAIZ / "logs"
ARQ_LOG = DIR_LOGS / "banksense.log"
FORMATO = "%(asctime)s %(levelname)-7s %(name)s | %(message)s"
FORMATO_DATA = "%Y-%m-%d %H:%M:%S"

_configurado = False


def configurar_logs(nivel: str | None = None) -> None:
    """Liga os logs uma única vez. O nível vem de BANKSENSE_LOG (padrão INFO)."""
    global _configurado
    if _configurado:
        return
    nivel = (nivel or os.getenv("BANKSENSE_LOG", "INFO")).upper()
    formatador = logging.Formatter(FORMATO, FORMATO_DATA)

    terminal = logging.StreamHandler(sys.stdout)
    terminal.setFormatter(formatador)
    manipuladores: list[logging.Handler] = [terminal]

    try:  # em ambientes sem permissão de escrita (ex.: deploy), fica só o terminal
        DIR_LOGS.mkdir(parents=True, exist_ok=True)
        arquivo = logging.FileHandler(ARQ_LOG, encoding="utf-8")
        arquivo.setFormatter(formatador)
        manipuladores.append(arquivo)
    except OSError:
        pass

    raiz = logging.getLogger("banksense")
    raiz.setLevel(nivel)
    for m in manipuladores:
        raiz.addHandler(m)
    raiz.propagate = False
    _configurado = True


def obter_logger(nome: str) -> logging.Logger:
    """Devolve o logger do módulo, já com a configuração do projeto."""
    configurar_logs()
    return logging.getLogger(nome)
