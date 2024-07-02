from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from src.helpers import tempo_atendimento
from src.models import Pedido, Item


class Report(ABC):
    @abstractmethod
    def to_xlsx(self, workbook: Workbook, worksheet: Worksheet):
        pass


class ReportItens(Report):
    ticket_medio: float
    quantidade_total: int = 0
    valor_total: float = 0

    def __init__(self, de: datetime, ate: datetime, itens: List[Item]):
        self.itens = []

        for item in itens:
            if item not in self.itens:
                self.itens.append(item)
            else:
                i = self.itens.index(item)
                self.itens[i].quantidade += item.quantidade
                self.itens[i].valor_total += item.valor_total

            self.quantidade_total += item.quantidade
            self.valor_total += item.valor_total

        self.de = de
        self.ate = ate
        self.ticket_medio = (self.valor_total / self.quantidade_total) if self.quantidade_total > 0 else 0
        self.itens.sort(key=lambda x: (x.quantidade, x.valor_total, x.nome), reverse=True)

    def to_xlsx(self, workbook: Workbook, worksheet: Worksheet):
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        money_format = workbook.add_format({'num_format': 44})
        align_end_format = workbook.add_format({'align': 'right'})
        current_row = 1

        def config_worksheet():
            worksheet.freeze_panes(1, 0)
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 30)
            worksheet.set_column('C:C', 12)
            worksheet.set_column('D:D', 11)
            worksheet.set_column('E:E', 12)
            worksheet.set_column('F:F', 12)

        def write_header():
            worksheet.write('A1', 'Cód.')
            worksheet.write('B1', 'Item')
            worksheet.write('C1', 'Preço')
            worksheet.write('D1', 'Qtd. Vendida')
            worksheet.write('E1', 'Total')
            worksheet.write('F1', 'Ticket Médio')

        def write_row(item: Item):
            nonlocal current_row
            worksheet.write(f'A{current_row}', item.codigo)
            worksheet.write(f'B{current_row}', item.nome)
            worksheet.write(f'C{current_row}', item.valor_unitario, money_format)
            worksheet.write(f'D{current_row}', item.quantidade)
            worksheet.write(f'E{current_row}', item.valor_total, money_format)
            worksheet.write(f'F{current_row}', (item.valor_total / item.quantidade) if item.quantidade > 0 else 0, money_format)

        config_worksheet()
        write_header()

        for item in self.itens:
            current_row += 1
            write_row(item)

        current_row += 1
        worksheet.merge_range(f'A{current_row}:C{current_row}', 'TOTAIS:', align_end_format)
        worksheet.write(f'D{current_row}', f'=SUM(D2:D{current_row - 1})', money_format)
        worksheet.write(f'E{current_row}', f'=SUM(E2:E{current_row - 1})', money_format)


class ReportPedidos(Report):
    tempo_medio: int = 0
    ticket_medio: float
    qtd_total: int = 0
    valor_total: float = 0
    valor_fiado: float = 0

    tempo_medio_ifood: int = 0
    ticket_medio_ifood: float
    qtd_ifood: int = 0
    valor_ifood: float = 0

    tempo_medio_bot: int = 0
    ticket_medio_bot: float
    qtd_bot: int = 0
    valor_bot: float = 0

    tempo_medio_delivery: int = 0
    ticket_medio_delivery: float
    qtd_delivery: int = 0
    valor_delivery: float = 0

    tempo_medio_local: int = 0
    ticket_medio_local: float
    qtd_local: int = 0
    valor_local: float = 0

    def __init__(self, de: datetime, ate: datetime, pedidos: List[Pedido]):
        self.de = de
        self.ate = ate
        self.pedidos = pedidos
        self.qtd_total = len(pedidos)

        for pedido in pedidos:
            self.valor_total += pedido.valor_total
            self.tempo_medio += pedido.tempo_atendimento

            if pedido.eh_fiado:
                self.valor_fiado += pedido.valor_total

            if pedido.tipo_atendimento == 'iFood':
                self.tempo_medio_ifood += pedido.tempo_atendimento
                self.valor_ifood += pedido.valor_total
                self.qtd_ifood += 1
            elif pedido.tipo_atendimento == 'Bot':
                self.tempo_medio_bot += pedido.tempo_atendimento
                self.valor_bot += pedido.valor_total
                self.qtd_bot += 1
            elif pedido.tipo_atendimento == 'Delivery':
                self.tempo_medio_delivery += pedido.tempo_atendimento
                self.valor_delivery += pedido.valor_total
                self.qtd_delivery += 1
            else:
                self.tempo_medio_local += pedido.tempo_atendimento
                self.valor_local += pedido.valor_total
                self.qtd_local += 1

        self.tempo_medio /= self.qtd_total
        self.tempo_medio_ifood /= self.qtd_ifood
        self.tempo_medio_bot /= self.qtd_bot
        self.tempo_medio_delivery /= self.qtd_delivery
        self.tempo_medio_local /= self.qtd_local
        self.ticket_medio = (self.valor_total / self.qtd_total) if self.qtd_total > 0 else 0
        self.ticket_medio_ifood = (self.valor_ifood / self.qtd_ifood) if self.qtd_ifood > 0 else 0
        self.ticket_medio_bot = (self.valor_bot / self.qtd_bot) if self.qtd_bot > 0 else 0
        self.ticket_medio_delivery = (self.valor_delivery / self.qtd_delivery) if self.qtd_delivery > 0 else 0
        self.ticket_medio_local = (self.valor_local / self.qtd_local) if self.qtd_local > 0 else 0
        self.pedidos.sort(key=lambda x: x.codigo)

    def to_xlsx(self, workbook: Workbook, worksheet: Worksheet):
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})
        money_format = workbook.add_format({'num_format': 44})
        money_format2 = workbook.add_format({'num_format': 44, 'border': 1})
        border_format = workbook.add_format({'border': 1})
        align_end_format = workbook.add_format({'align': 'right'})
        current_row = 1

        def config_worksheet():
            worksheet.freeze_panes(1, 0)
            worksheet.outline_settings(visible=1, symbols_below=False)
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 6)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 20)
            worksheet.set_column('F:F', 11)
            worksheet.set_column('G:G', 16)
            worksheet.set_column('H:H', 16)
            worksheet.set_column('I:I', 11)
            worksheet.set_column('J:J', 12)
            worksheet.set_column('K:K', 12)
            worksheet.set_column('L:L', 12)
            worksheet.set_column('M:M', 12)

        def write_header():
            worksheet.write('A1', 'Nº')
            worksheet.write('B1', 'Cód.')
            worksheet.write('C1', 'Atendente')
            worksheet.write('D1', 'Entregador')
            worksheet.write('E1', 'Cliente')
            worksheet.write('F1', 'Origem')
            worksheet.write('G1', 'Data de Inicio')
            worksheet.write('H1', 'Data de Fim')
            worksheet.write('I1', 'Duração')
            worksheet.write('J1', 'Qtd. Itens')
            worksheet.write('K1', 'Valor Entrega')
            worksheet.write('L1', 'Valor Total')
            worksheet.write('M1', 'Valor Fiado')

        def write_row(n: int, pedido: Pedido):
            nonlocal current_row
            worksheet.write(f'A{current_row}', n)
            worksheet.write(f'B{current_row}', pedido.codigo)
            worksheet.write(f'C{current_row}', pedido.atendente)
            worksheet.write(f'D{current_row}', pedido.entregador)
            worksheet.write(f'E{current_row}', pedido.cliente)
            worksheet.write(f'F{current_row}', pedido.tipo_atendimento)
            worksheet.write(f'G{current_row}', pedido.data_abertura, date_format)
            worksheet.write(f'H{current_row}', pedido.data_fechamento, date_format)
            worksheet.write(f'I{current_row}', tempo_atendimento(pedido.tempo_atendimento))
            worksheet.write(f'J{current_row}', pedido.quantidade_itens)
            worksheet.write(f'K{current_row}', pedido.valor_entrega, money_format)
            worksheet.write(f'L{current_row}', pedido.valor_total, money_format)
            worksheet.write(f'M{current_row}', pedido.valor_total + pedido.valor_entrega if pedido.eh_fiado else 0, money_format)

        def write_subtable(itens: List[Item]):
            nonlocal current_row
            worksheet.write(f'B{current_row}', 'Cód.', border_format)
            worksheet.write(f'C{current_row}', 'Item', border_format)
            worksheet.write(f'D{current_row}', 'Qtd.', border_format)
            worksheet.write(f'E{current_row}', 'Valor', border_format)
            worksheet.write(f'F{current_row}', 'Total', border_format)
            worksheet.set_row(current_row - 1, None, None, {'level': 1, 'hidden': True})

            for item in itens:
                current_row += 1
                worksheet.write(f'B{current_row}', item.codigo, border_format)
                worksheet.write(f'C{current_row}', item.nome, border_format)
                worksheet.write(f'D{current_row}', item.quantidade, border_format)
                worksheet.write(f'E{current_row}', item.valor_cobrado, money_format2)
                worksheet.write(f'F{current_row}', item.valor_total, money_format2)
                worksheet.set_row(current_row - 1, None, None, {'level': 1, 'hidden': True})

            worksheet.set_row(current_row, None, None, {'collapsed': True})

        config_worksheet()
        write_header()

        for i, pedido in enumerate(self.pedidos, start=1):
            current_row += 1
            write_row(i, pedido)
            current_row += 1
            write_subtable(pedido.itens)

        current_row += 1
        worksheet.merge_range(f'A{current_row}:I{current_row}', 'TOTAIS:', align_end_format)
        worksheet.write(f'J{current_row}', f'=SUM(J2:J{current_row - 1})')
        worksheet.write(f'K{current_row}', f'=SUM(K2:K{current_row - 1})', money_format)
        worksheet.write(f'L{current_row}', f'=SUM(L2:L{current_row - 1})', money_format)
        worksheet.write(f'M{current_row}', f'=SUM(M2:M{current_row - 1})', money_format)
