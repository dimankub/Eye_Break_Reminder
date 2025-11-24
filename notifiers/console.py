"""Fallback notifier для консольного вывода"""
import logging
from typing import Callable

from .base import BaseNotifier

LOG_MESSAGES = {
    'ru': {
        'notification_console': 'Вывод в консоль (fallback): {msg}',
    },
    'en': {
        'notification_console': 'Console output (fallback): {msg}',
    }
}

_log_lang = 'en'

def set_log_language(lang: str):
    """Устанавливает язык для логирования"""
    global _log_lang
    _log_lang = lang if lang in LOG_MESSAGES else 'en'

def _log(key: str, **kwargs) -> str:
    """Возвращает локализованное сообщение для логирования"""
    return LOG_MESSAGES[_log_lang].get(key, LOG_MESSAGES['en'].get(key, key)).format(**kwargs)

class ConsoleNotifier(BaseNotifier):
    """Fallback notifier для консольного вывода"""
    
    def notify(self, msg: str) -> None:
        """
        Выводит уведомление в консоль
        
        Args:
            msg: Текст уведомления
        """
        print(f"[EyeCare] {msg}")
        logging.debug(_log('notification_console', msg=msg))
