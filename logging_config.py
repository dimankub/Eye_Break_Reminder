"""Модуль для настройки логирования"""
import logging

# Словари локализации для логирования
LOG_MESSAGES = {
    'ru': {
        'startup': 'Запуск EyeCare Reminder',
        'config_loaded': 'Конфигурация загружена: язык={lang}, интервал={interval} мин, режим={mode}, сообщений={count}',
        'init_tray': 'Инициализация менеджера системного трея',
        'timer_started': 'Таймер запущен с интервалом {interval} минут',
        'timer_waiting': 'Ожидание {interval} минут до следующего уведомления...',
        'auto_notification': 'Автоматическое уведомление (сообщение #{num}): {msg}...',
        'manual_check': 'Ручная проверка: отправка уведомления',
        'pause_enabled': 'Пауза включена',
        'pause_disabled': 'Пауза выключена',
        'quitting': 'Завершение работы по запросу пользователя',
        'cleanup': 'Очистка ресурсов и завершение работы',
        'shutdown_start': 'Начало процедуры завершения работы',
        'shutdown_tray': 'Иконка трея остановлена',
        'shutdown_tray_error': 'Ошибка при остановке иконки (игнорируется): {error}',
        'timer_thread_started': 'Поток таймера запущен',
        'signal_received': 'Получен сигнал {signal}. Завершаем работу...',
        'signal_registration': 'Регистрация обработчиков сигналов',
        'signal_error': 'Не удалось зарегистрировать {signal} (возможно, Windows): {error}',
        'tray_starting': 'Запуск системного трея (приложение работает в фоновом режиме)',
        'keyboard_interrupt': 'EyeCare остановлен пользователем (KeyboardInterrupt)',
        'critical_error': 'Критическая ошибка: {error}',
        'app_exited': 'EyeCare завершил работу',
    },
    'en': {
        'startup': 'Starting EyeCare Reminder',
        'config_loaded': 'Configuration loaded: language={lang}, interval={interval} min, mode={mode}, messages={count}',
        'init_tray': 'Initializing system tray manager',
        'timer_started': 'Timer started with {interval} minute interval',
        'timer_waiting': 'Waiting {interval} minutes until next notification...',
        'auto_notification': 'Automatic notification (message #{num}): {msg}...',
        'manual_check': 'Manual check: sending notification',
        'pause_enabled': 'Pause enabled',
        'pause_disabled': 'Pause disabled',
        'quitting': 'Exiting by user request',
        'cleanup': 'Cleaning up resources and shutting down',
        'shutdown_start': 'Starting shutdown procedure',
        'shutdown_tray': 'Tray icon stopped',
        'shutdown_tray_error': 'Error stopping tray icon (ignored): {error}',
        'timer_thread_started': 'Timer thread started',
        'signal_received': 'Received signal {signal}. Shutting down...',
        'signal_registration': 'Registering signal handlers',
        'signal_error': 'Failed to register {signal} (possibly Windows): {error}',
        'tray_starting': 'Starting system tray (application running in background)',
        'keyboard_interrupt': 'EyeCare stopped by user (KeyboardInterrupt)',
        'critical_error': 'Critical error: {error}',
        'app_exited': 'EyeCare has exited',
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

def setup_logging(verbose: bool = False):
    """
    Настройка логирования с уровнями INFO/DEBUG
    
    Args:
        verbose: Если True, устанавливает уровень DEBUG, иначе INFO
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def log(key: str, **kwargs) -> str:
    """
    Возвращает локализованное сообщение для логирования
    
    Args:
        key: Ключ сообщения
        **kwargs: Параметры для форматирования
        
    Returns:
        Отформатированное сообщение
    """
    return _log(key, **kwargs)

