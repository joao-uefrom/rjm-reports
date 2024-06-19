from src.helpers import escape_message, formatar_real, formatar_data
from src.reports import ReportItens, ReportPedidos


def message_report_itens(relatorio: ReportItens):
    message = f'entre {formatar_data(relatorio.de)} e {formatar_data(relatorio.ate)}:\n\n'

    for i, item in enumerate(relatorio.itens, start=1):
        message += f'#{i} - {item.nome}\n{item.quantidade} x {formatar_real(item.valor_unitario)} = {formatar_real(item.valor_total)} ~ {formatar_real(item.valor_total / item.quantidade)}\n\n'

    message = '*Produtos Mais Vendidos* ' + escape_message(message)
    message += f'*Total de Itens:* {relatorio.quantidade_total}\n*Valor Total:* {escape_message(formatar_real(relatorio.valor_total))}\n*Ticket Médio:* {escape_message(formatar_real(relatorio.ticket_medio))}'

    return message


def message_report_pedidos(relatorio: ReportPedidos):
    message = f'*Pedidos* entre {escape_message(formatar_data(relatorio.de))} e {escape_message(formatar_data(relatorio.ate))}:\n\n'
    message += '_*iFood*:_'
    message += escape_message(f"""
Qtd. de pedidos: {relatorio.quantidade_ifood}
Total vendido: {formatar_real(relatorio.total_ifood)}
Ticket médio: {formatar_real(relatorio.ticket_medio_ifood)}\n\n""")

    message += '_*WhatsApp*:_'
    message += escape_message(f"""
Qtd. de pedidos: {relatorio.quantidade_whatsapp}
Total vendido: {formatar_real(relatorio.total_whatsapp)}
Ticket médio: {formatar_real(relatorio.ticket_medio_whatsapp)}\n\n""")

    message += '_*Presencial*:_'
    message += escape_message(f"""
Qtd. de pedidos: {relatorio.quantidade_local}
Total vendido: {formatar_real(relatorio.total_local)}
Ticket médio: {formatar_real(relatorio.ticket_medio_local)}\n\n""")

    message += '*Total Geral:*'
    message += escape_message(f"""
Qtd. de pedidos: {relatorio.quantidade_total}
Total vendido: {formatar_real(relatorio.valor_total)}
Ticket médio: {formatar_real(relatorio.ticket_medio)}""")

    return message
