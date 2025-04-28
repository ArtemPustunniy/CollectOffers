import re
from config import FILTER_WORDS

pattern = re.compile('|'.join(map(re.escape, FILTER_WORDS)))


def is_relevant(message_text: str) -> bool:
    message_text = message_text.lower()

    return bool(pattern.search(message_text))


def is_source_on_hh_ru(message_text: str) -> bool:
    return "hh.ru" in message_text.lower()

