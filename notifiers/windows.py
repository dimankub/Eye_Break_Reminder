"""Notifier для Windows используя win11toast или win10toast"""
import logging
from typing import Callable, Optional

from .base import BaseNotifier

LOG_MESSAGES = {
    'ru': {
        'notification_sending_win11': 'Отправка уведомления через win11toast: {msg}...',
        'notification_sending_win10': 'Отправка уведомления через win10toast: {msg}...',
        'notification_sent': 'Уведомление успешно отправлено',
        'notify_error_win11': 'Ошибка при отправке уведомления через win11toast: {error}',
        'notify_error_win10': 'Ошибка при отправке уведомления через win10toast: {error}',
    },
    'en': {
        'notification_sending_win11': 'Sending notification via win11toast: {msg}...',
        'notification_sending_win10': 'Sending notification via win10toast: {msg}...',
        'notification_sent': 'Notification sent successfully',
        'notify_error_win11': 'Error sending notification via win11toast: {error}',
        'notify_error_win10': 'Error sending notification via win10toast: {error}',
    }
}

NOTIFICATION_TIMEOUT = 5  # Таймаут для отправки уведомлений в секундах

_log_lang = 'en'

def set_log_language(lang: str):
    """Устанавливает язык для логирования"""
    global _log_lang
    _log_lang = lang if lang in LOG_MESSAGES else 'en'

def _log(key: str, **kwargs) -> str:
    """Возвращает локализованное сообщение для логирования"""
    return LOG_MESSAGES[_log_lang].get(key, LOG_MESSAGES['en'].get(key, key)).format(**kwargs)

class WindowsNotifier(BaseNotifier):
    """Notifier для Windows используя win11toast или win10toast"""
    
    def __init__(self):
        self._win11toast = None
        self._win10toast = None
        self._toaster = None
        self._is_win11 = False
        self._available = False
        
        # Пытаемся загрузить win11toast
        try:
            from win11toast import toast
            self._win11toast = toast
            self._is_win11 = True
            self._available = True
        except ImportError:
            # Пытаемся загрузить win10toast
            try:
                from win10toast import ToastNotifier
                self._win10toast = ToastNotifier
                self._toaster = ToastNotifier()
                self._available = True
            except ImportError:
                self._available = False
    
    def is_available(self) -> bool:
        """Проверяет, доступен ли notifier"""
        return self._available
    
    def is_win11(self) -> bool:
        """Проверяет, используется ли win11toast"""
        return self._is_win11
    
    def notify(self, msg: str) -> None:
        """
        Отправляет уведомление через win11toast или win10toast
        
        Args:
            msg: Текст уведомления
        """
        if not self._available:
            return
        
        if self._is_win11 and self._win11toast:
            logging.debug(_log('notification_sending_win11', msg=msg[:50]))
            try:
                self._win11toast("EyeCare", msg)
                logging.debug(_log('notification_sent'))
            except Exception as e:
                logging.error(_log('notify_error_win11', error=e))
        elif self._toaster:
            logging.debug(_log('notification_sending_win10', msg=msg[:50]))
            try:
                self._toaster.show_toast("EyeCare", str(msg), duration=NOTIFICATION_TIMEOUT)
                logging.debug(_log('notification_sent'))
            except Exception as e:
                logging.error(_log('notify_error_win10', error=e))
