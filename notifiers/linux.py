"""Notifier для Linux используя notify-send"""
import subprocess
import logging
from typing import Callable

from .base import BaseNotifier

LOG_MESSAGES = {
    'ru': {
        'notification_sending': 'Отправка уведомления через notify-send: {msg}...',
        'notification_sent': 'Уведомление успешно отправлено',
        'notify_error': 'Ошибка при отправке уведомления через notify-send: {error}',
        'notify_not_found': 'notify-send не найден. Убедитесь, что установлен libnotify-bin',
    },
    'en': {
        'notification_sending': 'Sending notification via notify-send: {msg}...',
        'notification_sent': 'Notification sent successfully',
        'notify_error': 'Error sending notification via notify-send: {error}',
        'notify_not_found': 'notify-send not found. Make sure libnotify-bin is installed',
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

class LinuxNotifier(BaseNotifier):
    """Notifier для Linux используя notify-send"""
    
    def notify(self, msg: str) -> None:
        """
        Отправляет уведомление через notify-send
        
        Args:
            msg: Текст уведомления
        """
        logging.debug(_log('notification_sending', msg=msg[:50]))
        try:
            subprocess.run(["notify-send", "EyeCare", str(msg)], check=True)
            logging.debug(_log('notification_sent'))
        except subprocess.CalledProcessError as e:
            logging.error(_log('notify_error', error=e))
        except FileNotFoundError:
            logging.error(_log('notify_not_found'))
