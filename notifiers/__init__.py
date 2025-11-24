"""Фабрика для создания notifier'ов по платформам"""
import platform
import logging
from typing import Callable

from .macos import MacOSNotifier
from .linux import LinuxNotifier
from .windows import WindowsNotifier
from .console import ConsoleNotifier

# Словари локализации для логирования
LOG_MESSAGES = {
    'ru': {
        'notifier_init': 'Инициализация нотификатора для системы: {system}',
        'using_macos': 'Использование osascript для macOS уведомлений',
        'using_linux': 'Использование notify-send для Linux уведомлений',
        'using_win11': 'Использование win11toast для Windows уведомлений',
        'using_win10': 'Использование win10toast для Windows уведомлений',
        'notifier_fallback': 'Библиотеки win11toast и win10toast не найдены, используется консольный вывод',
        'unknown_system': 'Неизвестная система {system}, используется консольный вывод',
    },
    'en': {
        'notifier_init': 'Initializing notifier for system: {system}',
        'using_macos': 'Using osascript for macOS notifications',
        'using_linux': 'Using notify-send for Linux notifications',
        'using_win11': 'Using win11toast for Windows notifications',
        'using_win10': 'Using win10toast for Windows notifications',
        'notifier_fallback': 'win11toast and win10toast libraries not found, using console output',
        'unknown_system': 'Unknown system {system}, using console output',
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

def init_notifier(lang: str = 'en') -> Callable[[str], None]:
    """
    Инициализирует и возвращает функцию уведомлений для текущей платформы
    
    Args:
        lang: Язык для логирования
        
    Returns:
        Функция notify(msg: str) для отправки уведомлений
    """
    set_log_language(lang)
    system = platform.system()
    logging.debug(_log('notifier_init', system=system))
    
    if system == "Darwin":
        logging.info(_log('using_macos'))
        return MacOSNotifier().notify
    elif system == "Linux":
        logging.info(_log('using_linux'))
        return LinuxNotifier().notify
    elif system == "Windows":
        notifier = WindowsNotifier()
        if notifier.is_available():
            if notifier.is_win11():
                logging.info(_log('using_win11'))
            else:
                logging.info(_log('using_win10'))
            return notifier.notify
        else:
            logging.warning(_log('notifier_fallback'))
            return ConsoleNotifier().notify
    else:
        logging.warning(_log('unknown_system', system=system))
        return ConsoleNotifier().notify
