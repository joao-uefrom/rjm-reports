from src.helpers import escape_message, formatar_real, formatar_data, tempo_atendimento
from src.reports import ReportItens, ReportPedidos


def message_report_itens(relatorio: ReportItens):
    if relatorio.de == relatorio.ate:
        message = f'de {formatar_data(relatorio.de)}:\n\n'
    else:
        message = f'entre {formatar_data(relatorio.de)} e {formatar_data(relatorio.ate)}:\n\n'

    for i, item in enumerate(relatorio.itens, start=1):
        message += f'#{i} - {item.nome}\n{item.quantidade} x {formatar_real(item.valor_unitario)} = {formatar_real(item.valor_total)} ~ {formatar_real(item.valor_total / item.quantidade)}\n\n'

    message = '*Produtos Mais Vendidos* ' + escape_message(message)
    message += f'*Total de Itens:* {relatorio.quantidade_total}\n*Valor Total:* {escape_message(formatar_real(relatorio.valor_total))}\n*Ticket Médio:* {escape_message(formatar_real(relatorio.ticket_medio))}'

    return message


def message_report_pedidos(relatorio: ReportPedidos):
    if relatorio.de == relatorio.ate:
        message = f'*Pedidos* de {escape_message(formatar_data(relatorio.de))}:\n\n'
    else:
        message = f'*Pedidos* entre {escape_message(formatar_data(relatorio.de))} e {escape_message(formatar_data(relatorio.ate))}:\n\n'

    message += '_*iFood*:_'
    message += escape_message(f"""
Qtd. de pedidos: {relatorio.qtd_ifood}
Total vendido: {formatar_real(relatorio.valor_ifood)}
Ticket médio: {formatar_real(relatorio.ticket_medio_ifood)}
Duração média: {tempo_atendimento(relatorio.tempo_medio_ifood)}\n\n""")

    message += '_*Bot*:_'
    message += escape_message(f"""
Qtd. de pedidos: {relatorio.qtd_bot}
Total vendido: {formatar_real(relatorio.valor_bot)}
Ticket médio: {formatar_real(relatorio.ticket_medio_bot)}
Duração média: {tempo_atendimento(relatorio.tempo_medio_bot)}\n\n""")

    message += '_*Delivery*:_'
    message += escape_message(f"""
Qtd. de pedidos: {relatorio.qtd_delivery}
Total vendido: {formatar_real(relatorio.valor_delivery)}
Ticket médio: {formatar_real(relatorio.ticket_medio_delivery)}
Duração média: {tempo_atendimento(relatorio.tempo_medio_delivery)}\n\n""")

    message += '_*Presencial*:_'
    message += escape_message(f"""
Qtd. de pedidos: {relatorio.qtd_local}
Total vendido: {formatar_real(relatorio.valor_local)}
Ticket médio: {formatar_real(relatorio.ticket_medio_local)}
Duração média: {tempo_atendimento(relatorio.tempo_medio_local)}\n\n""")

    message += '*Total Geral:*'
    message += escape_message(f"""
Qtd. de pedidos: {relatorio.qtd_total}
Total vendido: {formatar_real(relatorio.valor_total)}
Total fiado: {formatar_real(relatorio.valor_fiado)}
Ticket médio: {formatar_real(relatorio.ticket_medio)}
Duração média: {tempo_atendimento(relatorio.tempo_medio)}""")

    return message
