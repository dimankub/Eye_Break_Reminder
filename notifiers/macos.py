"""Notifier для macOS используя osascript"""
import subprocess
import logging
from typing import Callable

from .base import BaseNotifier

LOG_MESSAGES = {
    'ru': {
        'notification_sending': 'Отправка уведомления через osascript: {msg}...',
        'notification_sent': 'Уведомление успешно отправлено',
        'notify_error': 'Ошибка при отправке уведомления через osascript: {error}',
    },
    'en': {
        'notification_sending': 'Sending notification via osascript: {msg}...',
        'notification_sent': 'Notification sent successfully',
        'notify_error': 'Error sending notification via osascript: {error}',
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

class MacOSNotifier(BaseNotifier):
    """Notifier для macOS используя osascript"""
    
    def notify(self, msg: str) -> None:
        """
        Отправляет уведомление через osascript
        
        Args:
            msg: Текст уведомления
        """
        safe_msg = str(msg).replace('"', '\\"').replace("\n", " ")
        logging.debug(_log('notification_sending', msg=msg[:50]))
        try:
            subprocess.run(
                ["osascript", "-e", f'display notification "{safe_msg}" with title "EyeCare"'],
                check=True
            )
            logging.debug(_log('notification_sent'))
        except subprocess.CalledProcessError as e:
            logging.error(_log('notify_error', error=e))
