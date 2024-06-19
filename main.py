import locale
import logging
import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler

from src.commands import command_start, post_init, command_report

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

if __name__ == '__main__':
    application = (ApplicationBuilder()
                   .token(os.environ['TELEGRAM_TOKEN'])
                   .post_init(post_init)
                   .build())

    start_handler = CommandHandler('start', command_start)
    report_handler = CommandHandler('relatorio', command_report)
    application.add_handler(start_handler)
    application.add_handler(report_handler)

    application.run_polling()
