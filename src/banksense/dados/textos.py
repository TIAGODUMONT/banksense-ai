"""Vocabulário usado para montar as mensagens sintéticas.

As frases foram escritas para o estudo e não foram copiadas de clientes reais.
"""

from __future__ import annotations

import numpy as np

from banksense.dados import premissas as P

# Objeto de que o cliente fala, por categoria
OBJETOS: dict[str, list[str]] = {
    "cartao_credito": ["meu cartão", "o cartão de crédito", "a fatura do cartão", "o limite do cartão",
                       "meu cartão virtual", "a anuidade do cartão"],
    "pix": ["meu pix", "o pix", "a transferência por pix", "o pix agendado", "minha chave pix",
            "o pix que eu recebi"],
    "conta_corrente": ["minha conta", "o saldo da conta", "o extrato", "a conta corrente",
                       "meu depósito", "a abertura da conta"],
    "aplicativo": ["o aplicativo", "o app", "o login no app", "a atualização do app",
                   "a tela de pagamentos", "o reconhecimento facial do app"],
    "emprestimo": ["o empréstimo", "a parcela do empréstimo", "o consignado", "a simulação de crédito",
                   "a renegociação da dívida", "o crédito pessoal"],
    "tarifas": ["a tarifa", "a cobrança do pacote de serviços", "a taxa de saque",
                "o valor da mensalidade", "a tarifa de TED", "a cobrança de manutenção"],
    "investimentos": ["meu CDB", "a aplicação", "o rendimento", "o tesouro direto", "o resgate",
                      "a carteira de investimentos"],
    "atendimento": ["o atendimento", "o atendente", "o suporte", "o chat de atendimento",
                    "a central", "o gerente"],
    "fraude_seguranca": ["minha conta", "meu cartão", "uma compra", "o acesso à conta",
                         "uma transação", "o token de segurança"],
}

# O que deu errado, por categoria
PROBLEMAS: dict[str, list[str]] = {
    "cartao_credito": ["foi bloqueado sem aviso", "veio com cobrança errada", "teve o limite reduzido do nada",
                       "não passa em nenhuma loja", "cobrou anuidade que era isenta", "chegou com valor duplicado"],
    "pix": ["não caiu na conta", "ficou em processamento o dia todo", "foi devolvido sem motivo",
            "caiu duas vezes", "deu erro na hora de enviar", "sumiu do extrato"],
    "conta_corrente": ["está com saldo errado", "foi bloqueada sem explicação", "não mostra as movimentações",
                       "ficou negativa sem eu usar", "não atualiza", "demora dias pra liberar"],
    "aplicativo": ["trava toda hora", "não abre", "fica pedindo atualização", "deu erro de novo",
                   "desloga sozinho", "está fora do ar"],
    "emprestimo": ["veio com juros maiores que o combinado", "foi negado sem motivo", "cobrou parcela a mais",
                   "não liberou o dinheiro", "teve o contrato alterado", "demorou demais pra ser analisado"],
    "tarifas": ["veio mais cara esse mês", "foi cobrada sem eu pedir", "não estava no contrato",
                "aumentou sem aviso", "é abusiva", "apareceu duas vezes"],
    "investimentos": ["rendeu menos que o prometido", "travou o resgate", "sumiu da carteira",
                      "não aparece no app", "teve uma taxa escondida", "demorou pra cair"],
    "atendimento": ["me deixou esperando uma hora", "não resolveu nada", "desligou na minha cara",
                    "me passou informação errada", "ficou me transferindo de setor", "não responde"],
    "fraude_seguranca": ["teve uma compra que eu não fiz", "foi invadida", "recebeu um pix que não reconheço",
                         "teve um acesso estranho", "foi clonado", "teve uma transferência que eu não autorizei"],
}

# O que deu certo, por categoria
ELOGIOS: dict[str, list[str]] = {
    "cartao_credito": ["chegou rapidinho", "teve o limite aumentado", "funciona em todo lugar",
                       "tem um cashback muito bom", "foi desbloqueado na hora"],
    "pix": ["caiu na hora", "funcionou certinho", "é muito rápido", "nunca me deixou na mão",
            "foi estornado rapidinho"],
    "conta_corrente": ["foi aberta em minutos", "está sempre certinha", "não tem tarifa nenhuma",
                       "é muito prática", "liberou o depósito rápido"],
    "aplicativo": ["é muito fácil de usar", "ficou ótimo depois da atualização", "é rápido e bonito",
                   "resolve tudo sem sair de casa", "nunca travou"],
    "emprestimo": ["foi aprovado na hora", "veio com juros justos", "caiu no mesmo dia",
                   "teve uma renegociação justa", "foi bem explicado"],
    "tarifas": ["foi estornada sem burocracia", "é bem mais barata que nos outros bancos",
                "foi zerada", "é justa", "foi devolvida rapidinho"],
    "investimentos": ["está rendendo bem", "é fácil de acompanhar", "teve o resgate na hora",
                      "tem ótimas opções", "superou minhas expectativas"],
    "atendimento": ["resolveu tudo rapidinho", "foi muito educado", "me ajudou demais",
                    "foi super atencioso", "explicou tudo direitinho"],
    "fraude_seguranca": ["foi protegida na hora", "teve a compra suspeita bloqueada",
                         "foi recuperada rapidinho", "ficou segura de novo", "foi bloqueado antes do prejuízo"],
}

# Ações e dúvidas para mensagens neutras
DUVIDAS: dict[str, list[str]] = {
    "cartao_credito": ["pedir um cartão adicional", "ver a data de fechamento da fatura", "aumentar o limite",
                       "cadastrar o cartão na carteira digital"],
    "pix": ["cadastrar uma chave pix", "aumentar o limite do pix noturno", "agendar um pix",
            "trocar minha chave pix"],
    "conta_corrente": ["pegar o comprovante de residência", "emitir o extrato do ano", "mudar o endereço",
                       "encerrar a conta"],
    "aplicativo": ["atualizar o app", "ativar a biometria", "mudar a senha do app", "ativar as notificações"],
    "emprestimo": ["simular um empréstimo", "antecipar parcelas", "ver o saldo devedor",
                   "contratar o consignado"],
    "tarifas": ["ver a tabela de tarifas", "mudar de pacote de serviços", "saber quanto custa um TED",
                "pedir isenção de tarifa"],
    "investimentos": ["investir no tesouro", "ver o informe de rendimentos", "resgatar o CDB",
                      "saber o rendimento da poupança"],
    "atendimento": ["falar com o gerente", "saber o horário da central", "abrir um protocolo",
                    "acompanhar meu protocolo"],
    "fraude_seguranca": ["trocar a senha", "cadastrar um novo celular", "bloquear o cartão por precaução",
                         "ativar a confirmação em duas etapas"],
}

# Problemas leves, para perguntas neutras que citam algo ruim
PROBLEMAS_LEVES: list[str] = ["demore um pouco", "apareça como pendente", "peça a senha de novo",
                              "fique em análise", "mostre um aviso"]

ABERTURAS_NEGATIVAS = ["", "", "Péssimo! ", "Mais uma vez ", "Que absurdo, ", "Estou muito insatisfeito, ",
                       "Gente, ", "Inacreditável, ", "De novo isso? ", "Sério, "]
FECHOS_NEGATIVOS = ["", "", "Quero uma solução urgente.", "Vou cancelar minha conta.", "Ninguém resolve nada.",
                    "Já é a terceira vez.", "Vou abrir reclamação no Procon.", "Que descaso."]
ABERTURAS_POSITIVAS = ["", "", "Parabéns ao banco, ", "Adorei, ", "Muito bom, ", "Show, ", "Que alegria, ",
                       "Sinceramente, "]
FECHOS_POSITIVOS = ["", "", "Obrigado!", "Atendimento nota 10.", "Recomendo.", "Continuem assim.",
                    "Melhor banco que já tive."]
SAUDACOES = ["", "Olá, ", "Oi, ", "Bom dia, ", "Boa tarde, ", "Boa noite, ", "Por favor, "]

ABREVIACOES: dict[str, str] = {
    "você": "vc", "vocês": "vcs", "porque": "pq", "muito": "mt", "não": "n", "também": "tb",
    "para": "pra", "está": "tá", "hoje": "hj", "mensagem": "msg", "quando": "qdo", "aqui": "aq",
    "beleza": "blz", "obrigado": "obg", "por favor": "pfv",
}
GIRIAS = ["aff", "kkkk", "mds", "slc", "pfv", "tlgd", "vish", "afe"]
EMOJIS = {"negativo": ["😡", "😤", "🙄", "👎"], "neutro": ["🤔", "🙂"], "positivo": ["😍", "👏", "🙏", "👍"]}

_ACENTOS = str.maketrans("áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ", "aaaaeeiooouucAAAAEEIOOOUUC")


def escolher(rng: np.random.Generator, opcoes: list[str]) -> str:
    return opcoes[int(rng.integers(len(opcoes)))]


def montar_texto(rng: np.random.Generator, categoria: str, sentimento: str) -> tuple[str, str]:
    """Monta o texto da mensagem e devolve (texto, tipo_de_construcao)."""
    obj = escolher(rng, OBJETOS[categoria])
    sorteio = rng.random()

    if sentimento == "negativo":
        prob = escolher(rng, PROBLEMAS[categoria])
        if sorteio < P.PROB_IRONIA:
            return f"Ótimo, {obj} {prob} de novo. Parabéns, hein.", "ironia"
        if sorteio < P.PROB_IRONIA + P.PROB_MISTO:
            elogio_outra = escolher(rng, ELOGIOS["aplicativo"])
            return f"O app até {elogio_outra}, mas {obj} {prob}. Assim não dá.", "misto"
        texto = f"{escolher(rng, ABERTURAS_NEGATIVAS)}{obj} {prob}. {escolher(rng, FECHOS_NEGATIVOS)}"
        return texto, "direto"

    if sentimento == "positivo":
        elogio = escolher(rng, ELOGIOS[categoria])
        if sorteio < P.PROB_NEGACAO_POSITIVA:
            return f"Não tenho do que reclamar, {obj} {elogio}. Não esperava tanto.", "negacao_positiva"
        if sorteio < P.PROB_NEGACAO_POSITIVA + P.PROB_MISTO:
            return f"Demorou um pouco no começo, mas {obj} {elogio}. Valeu.", "misto"
        texto = f"{escolher(rng, ABERTURAS_POSITIVAS)}{obj} {elogio}. {escolher(rng, FECHOS_POSITIVOS)}"
        return texto, "direto"

    # neutro
    if sorteio < P.PROB_NEUTRO_CARREGADO:
        leve = escolher(rng, PROBLEMAS_LEVES)
        return f"{escolher(rng, SAUDACOES)}é normal que {obj} {leve}?", "neutro_carregado"
    duvida = escolher(rng, DUVIDAS[categoria])
    modelos = [
        f"{escolher(rng, SAUDACOES)}como faço para {duvida}?",
        f"{escolher(rng, SAUDACOES)}gostaria de {duvida}.",
        f"{escolher(rng, SAUDACOES)}queria uma informação sobre {obj}.",
        f"{escolher(rng, SAUDACOES)}onde vejo como {duvida} no app?",
    ]
    return escolher(rng, modelos), "direto"


def _primeira_maiuscula(texto: str) -> str:
    texto = texto.strip()
    return texto[:1].upper() + texto[1:] if texto else texto


def aplicar_ruido(rng: np.random.Generator, texto: str, sentimento: str, p: dict[str, float]) -> str:
    """Aplica abreviações, gírias, erros e outros ruídos de linguagem natural."""
    texto = _primeira_maiuscula(texto)

    if rng.random() < p["abreviacoes"]:
        for original, abrev in ABREVIACOES.items():
            if original in texto and rng.random() < 0.6:
                texto = texto.replace(original, abrev)

    if rng.random() < p["erro_digitacao"]:
        palavras = texto.split()
        candidatas = [i for i, w in enumerate(palavras) if len(w) > 4 and w.isalpha()]
        if candidatas:
            i = candidatas[int(rng.integers(len(candidatas)))]
            w = palavras[i]
            j = int(rng.integers(1, len(w) - 2))
            palavras[i] = w[:j] + w[j + 1] + w[j] + w[j + 2:]
            texto = " ".join(palavras)

    if rng.random() < p["sem_acentos"]:
        texto = texto.translate(_ACENTOS)
    if rng.random() < p["minusculas"]:
        texto = texto.lower()
    if sentimento == "negativo" and rng.random() < p["caixa_alta_negativo"]:
        texto = texto.upper()
    if rng.random() < p["pontuacao_excessiva"]:
        texto = texto.rstrip(".!?") + ("!!!" if sentimento != "neutro" else "???")
    if rng.random() < p["giria"]:
        texto = f"{escolher(rng, GIRIAS)} {texto}" if rng.random() < 0.5 else f"{texto} {escolher(rng, GIRIAS)}"
    if rng.random() < p["emoji"]:
        texto = f"{texto} {escolher(rng, EMOJIS[sentimento])}"

    return " ".join(texto.split())
