import locale
import re
from datetime import datetime
from typing import List


def safe_strip(string):
    if string is not None:
        return string.strip()
    return string


def escape_message(message):
    return re.sub(r'([_*[\]()~`>#+\-=|{}.!])', '\\\\\\1', message, 0)


def formatar_real(valor):
    return locale.currency(valor, grouping=True)


def formatar_data(data: datetime) -> str:
    return data.strftime("%d/%m/%Y")


def tempo_atendimento(s: int) -> str:
    hours = s // 3600
    minutes = (s % 3600) // 60
    secs = s % 60
    return f"{int(hours)}h {int(minutes)}m {int(secs)}s"


def to_datetime(value: str) -> datetime:
    value = re.sub(r'[-_.]', '/', value)
    if len(value.split('/')[-1]) == 2:
        split = value.split('/')
        value = f'{split[0]}/{split[1]}/20{split[-1]}'
    return datetime.strptime(value, '%d/%m/%Y')


def split_message_if_needed(message: str) -> List[str]:
    limit = 4096
    if len(message) <= limit:
        return [message]

    pos = message.rfind('\n', 0, limit)

    if pos > 0:
        new_message = message[:pos]
        return [new_message] + split_message_if_needed(message[pos + 1:])

    new_message = message[:limit]
    return [new_message] + split_message_if_needed(message[limit:])


def nome_xlsx(de: datetime, ate: datetime) -> str:
    if de == ate:
        return f'relatorio_{de.strftime("%d-%m-%Y")}.xlsx'

    return f'relatorio_{de.strftime("%d-%m-%Y")}_ate_{ate.strftime("%d-%m-%Y")}.xlsx'
