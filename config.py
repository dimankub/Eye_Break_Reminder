"""Модуль для работы с конфигурацией"""
import os
import locale
import configparser
import logging

# Константы
DEFAULT_INTERVAL = 20  # Интервал по умолчанию в минутах
MAX_INTERVAL = 1440  # Максимальный интервал (24 часа)
MIN_INTERVAL = 1  # Минимальный интервал в минутах
SUPPORTED_LANGUAGES = ['auto', 'ru', 'en']
VALID_MESSAGE_MODES = ['random', 'sequential', 'single']

# Словари локализации для логирования
LOG_MESSAGES = {
    'ru': {
        'config_created': 'Создание нового конфигурационного файла: {filename}',
        'config_loaded_debug': 'Загружена конфигурация: интервал={interval} мин, режим={mode}, язык={lang}, сообщений={count}',
    },
    'en': {
        'config_created': 'Creating new configuration file: {filename}',
        'config_loaded_debug': 'Configuration loaded: interval={interval} min, mode={mode}, language={lang}, messages={count}',
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

def get_language(lang_override=None, filename='config.ini'):
    """
    Определяет язык для использования (без полной загрузки конфига)
    
    Args:
        lang_override: Принудительно установленный язык
        filename: Путь к файлу конфигурации
        
    Returns:
        Код языка ('ru' или 'en')
    """
    if lang_override:
        return lang_override
    
    if os.path.exists(filename):
        config = configparser.ConfigParser()
        config.read(filename, encoding='utf-8')
        lang_setting = config.get('Settings', 'lang', fallback=SUPPORTED_LANGUAGES[0])
        if lang_setting != SUPPORTED_LANGUAGES[0]:
            return lang_setting
    
    # Автоопределение по системной локали
    sys_lang = locale.getdefaultlocale()[0]
    return 'ru' if sys_lang and sys_lang.startswith('ru') else 'en'

def load_config(filename='config.ini', lang_override=None):
    """
    Загружает конфигурацию из файла
    
    Args:
        filename: Путь к файлу конфигурации
        lang_override: Принудительно установленный язык
        
    Returns:
        Кортеж (interval, messages, mode, lang)
    """
    # Устанавливаем язык для логирования в этом модуле
    if lang_override:
        set_log_language(lang_override)
    
    # Автосоздание базового конфига с секциями сообщений
    if not os.path.exists(filename):
        logging.info(_log('config_created', filename=filename))
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('[Settings]\n')
            f.write(f'interval_minutes = {DEFAULT_INTERVAL}\n')
            f.write(f'message_mode = {VALID_MESSAGE_MODES[0]}\n')
            f.write(f'lang = {SUPPORTED_LANGUAGES[0]}\n\n')
            f.write('[Messages.ru]\n')
            f.write('default = Встань, моргни и глянь вдаль. Глаза скажут спасибо.\n')
            f.write('messages =\n')
            f.write('    Посмотри вдаль и моргни пару раз.\n')
            f.write('    Потянись, дай глазам отдохнуть.\n')
            f.write('    Переведи взгляд на что-то дальнее.\n\n')
            f.write('[Messages.en]\n')
            f.write('default = Stand up, blink, and look into the distance. Your eyes will thank you.\n')
            f.write('messages =\n')
            f.write('    Look away from the screen for 20 seconds.\n')
            f.write('    Stretch a bit and rest your eyes.\n')
            f.write('    Blink a few times and refocus.\n')

    config = configparser.ConfigParser()
    config.read(filename, encoding='utf-8')

    # Валидация и нормализация интервала
    try:
        interval = config.getint('Settings', 'interval_minutes', fallback=DEFAULT_INTERVAL)
        if interval < MIN_INTERVAL:
            logging.warning(f"Invalid interval_minutes value: {interval}. Using default: {DEFAULT_INTERVAL}")
            interval = DEFAULT_INTERVAL
        if interval > MAX_INTERVAL:  # Максимум 24 часа
            logging.warning(f"Interval too large: {interval} minutes. Capping at {MAX_INTERVAL} minutes")
            interval = MAX_INTERVAL
    except (ValueError, TypeError) as e:
        logging.error(f"Error reading interval_minutes: {e}. Using default: {DEFAULT_INTERVAL}")
        interval = DEFAULT_INTERVAL
    
    # Валидация режима сообщений
    mode = config.get('Settings', 'message_mode', fallback=VALID_MESSAGE_MODES[0]).strip().lower()
    if mode not in VALID_MESSAGE_MODES:
        # Если режим некорректный, но не пустой, используем его как 'sequential'
        if mode:
            logging.warning(f"Unknown message_mode '{mode}'. Valid modes: {VALID_MESSAGE_MODES}. Using 'sequential'")
            mode = 'sequential'
        else:
            mode = VALID_MESSAGE_MODES[0]
    
    # Валидация языка
    lang_setting = config.get('Settings', 'lang', fallback=SUPPORTED_LANGUAGES[0]).strip().lower()
    if lang_setting not in SUPPORTED_LANGUAGES:
        logging.warning(f"Unknown lang '{lang_setting}'. Valid values: {SUPPORTED_LANGUAGES}. Using '{SUPPORTED_LANGUAGES[0]}'")
        lang_setting = SUPPORTED_LANGUAGES[0]

    # Выбор языка: аргумент > конфиг > язык системы
    lang = lang_override or lang_setting
    if lang == SUPPORTED_LANGUAGES[0]:  # 'auto'
        sys_lang = locale.getdefaultlocale()[0]
        lang = 'ru' if sys_lang and sys_lang.startswith('ru') else 'en'

    messages_section = f'Messages.{lang}'
    if not config.has_section(messages_section):
        messages_section = 'Messages.en'

    messages = []
    if config.has_option(messages_section, 'messages'):
        for line in config.get(messages_section, 'messages').splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                messages.append(line)

    default_msg = config.get(messages_section, 'default', fallback='Take a break!')
    if not messages:
        messages = [default_msg]
    else:
        messages.insert(0, default_msg)

    logging.debug(_log('config_loaded_debug', interval=interval, mode=mode, lang=lang, count=len(messages)))
    return interval, messages, mode, lang

def save_interval(interval_minutes: int, filename='config.ini'):
    """
    Сохраняет интервал в конфигурационный файл
    
    Args:
        filename: Путь к файлу конфигурации
        interval_minutes: Интервал в минутах для сохранения
    """
    try:
        config = configparser.ConfigParser()
        config.read(filename, encoding='utf-8')
        if not config.has_section('Settings'):
            config.add_section('Settings')
        config.set('Settings', 'interval_minutes', str(interval_minutes))
        with open(filename, 'w', encoding='utf-8') as f:
            config.write(f)
    except Exception as e:
        logging.error(f"Error saving interval to config: {e}")

