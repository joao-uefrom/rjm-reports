from datetime import datetime, timedelta
import io
import os

import fdb
from telegram import Update, BotCommand
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, Application
from xlsxwriter import Workbook

from src.helpers import to_datetime, split_message_if_needed, nome_xlsx
from src.messages import message_report_itens, message_report_pedidos
from src.queries import get_itens, get_pedidos
from src.reports import ReportPedidos, ReportItens


async def post_init(application: Application):
    await application.bot.set_my_commands(
        [
            BotCommand("/relatorio", "Relatório de Pedidos e Vendas")
        ]
    )


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Escolha uma ação no menu!')


async def command_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) == 0:
            de = datetime.now()
            ate = de
        elif context.args[0].lower() == 'ontem' or context.args[0] == '-1':
            de = datetime.now() - timedelta(days=1)
            ate = de
        elif 0 < len(context.args) < 2:
            de = to_datetime(context.args[0])
            ate = de
        else:
            de = to_datetime(context.args[0])
            ate = to_datetime(context.args[1])

        if de > ate:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Período de datas inválido.')
            return

        with fdb.connect(
                host=os.environ['DB_HOST'],
                port=int(os.environ['DB_PORT']),
                database=os.environ['DB_PATH'],
                user=os.environ['DB_USER'],
                password=os.environ['DB_PASSWORD'],
                charset='UTF8') as con:
            cur = con.cursor()

            reportPedidos = ReportPedidos(de=de, ate=ate, pedidos=get_pedidos(cur, de=de, ate=ate))
            reportItens = ReportItens(de=de, ate=ate, itens=get_itens(cur, de=de, ate=ate))

        output = io.BytesIO()
        with Workbook(output) as workbook:
            worksheet1 = workbook.add_worksheet('Pedidos')
            worksheet2 = workbook.add_worksheet('Vendas')
            reportPedidos.to_xlsx(workbook, worksheet1)
            reportItens.to_xlsx(workbook, worksheet2)
        output.seek(0)

        itens_messages = split_message_if_needed(message_report_itens(reportItens))
        for message in itens_messages:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.MARKDOWN_V2)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_report_pedidos(reportPedidos), parse_mode=ParseMode.MARKDOWN_V2)
        await context.bot.send_document(chat_id=update.effective_chat.id, document=output.getvalue(), filename=nome_xlsx(de, ate))
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Algo deu errado, tente novamente.\n{e}')
