import time
import os
import sys
import platform
import random
import configparser
import subprocess
import argparse
import locale
import threading
import signal
import logging
from PIL import Image, ImageDraw
import pystray

# Словари локализации для логирования
LOG_MESSAGES = {
    'ru': {
        'startup': 'Запуск EyeCare Reminder',
        'config_created': 'Создание нового конфигурационного файла: {filename}',
        'config_loaded': 'Конфигурация загружена: язык={lang}, интервал={interval} мин, режим={mode}, сообщений={count}',
        'config_loaded_debug': 'Загружена конфигурация: интервал={interval} мин, режим={mode}, язык={lang}, сообщений={count}',
        'init_tray': 'Инициализация менеджера системного трея',
        'timer_started': 'Таймер запущен с интервалом {interval} минут',
        'timer_waiting': 'Ожидание {interval} минут до следующего уведомления...',
        'notification_sent': 'Уведомление успешно отправлено',
        'notification_sending_macos': 'Отправка уведомления через osascript: {msg}...',
        'notification_sending_linux': 'Отправка уведомления через notify-send: {msg}...',
        'notification_sending_win11': 'Отправка уведомления через win11toast: {msg}...',
        'notification_sending_win10': 'Отправка уведомления через win10toast: {msg}...',
        'notification_console': 'Вывод в консоль (fallback): {msg}',
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
        'notifier_init': 'Инициализация нотификатора для системы: {system}',
        'using_macos': 'Использование osascript для macOS уведомлений',
        'using_linux': 'Использование notify-send для Linux уведомлений',
        'using_win11': 'Использование win11toast для Windows уведомлений',
        'using_win10': 'Использование win10toast для Windows уведомлений',
        'notifier_fallback': 'Библиотеки win11toast и win10toast не найдены, используется консольный вывод',
        'unknown_system': 'Неизвестная система {system}, используется консольный вывод',
        'notify_error_macos': 'Ошибка при отправке уведомления через osascript: {error}',
        'notify_error_linux': 'Ошибка при отправке уведомления через notify-send: {error}',
        'notify_not_found_linux': 'notify-send не найден. Убедитесь, что установлен libnotify-bin',
        'notify_error_win11': 'Ошибка при отправке уведомления через win11toast: {error}',
        'notify_error_win10': 'Ошибка при отправке уведомления через win10toast: {error}',
    },
    'en': {
        'startup': 'Starting EyeCare Reminder',
        'config_created': 'Creating new configuration file: {filename}',
        'config_loaded': 'Configuration loaded: language={lang}, interval={interval} min, mode={mode}, messages={count}',
        'config_loaded_debug': 'Configuration loaded: interval={interval} min, mode={mode}, language={lang}, messages={count}',
        'init_tray': 'Initializing system tray manager',
        'timer_started': 'Timer started with {interval} minute interval',
        'timer_waiting': 'Waiting {interval} minutes until next notification...',
        'notification_sent': 'Notification sent successfully',
        'notification_sending_macos': 'Sending notification via osascript: {msg}...',
        'notification_sending_linux': 'Sending notification via notify-send: {msg}...',
        'notification_sending_win11': 'Sending notification via win11toast: {msg}...',
        'notification_sending_win10': 'Sending notification via win10toast: {msg}...',
        'notification_console': 'Console output (fallback): {msg}',
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
        'notifier_init': 'Initializing notifier for system: {system}',
        'using_macos': 'Using osascript for macOS notifications',
        'using_linux': 'Using notify-send for Linux notifications',
        'using_win11': 'Using win11toast for Windows notifications',
        'using_win10': 'Using win10toast for Windows notifications',
        'notifier_fallback': 'win11toast and win10toast libraries not found, using console output',
        'unknown_system': 'Unknown system {system}, using console output',
        'notify_error_macos': 'Error sending notification via osascript: {error}',
        'notify_error_linux': 'Error sending notification via notify-send: {error}',
        'notify_not_found_linux': 'notify-send not found. Make sure libnotify-bin is installed',
        'notify_error_win11': 'Error sending notification via win11toast: {error}',
        'notify_error_win10': 'Error sending notification via win10toast: {error}',
    }
}

# Глобальная переменная для языка логирования
_log_lang = 'en'

def set_log_language(lang):
    """Устанавливает язык для логирования"""
    global _log_lang
    _log_lang = lang if lang in LOG_MESSAGES else 'en'

def _log(key, **kwargs):
    """Возвращает локализованное сообщение для логирования"""
    return LOG_MESSAGES[_log_lang].get(key, LOG_MESSAGES['en'].get(key, key)).format(**kwargs)

def setup_logging(verbose=False):
    """Настройка логирования с уровнями INFO/DEBUG"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def get_language(lang_override=None, filename='config.ini'):
    """Определяет язык для использования (без полной загрузки конфига)"""
    if lang_override:
        return lang_override
    
    if os.path.exists(filename):
        config = configparser.ConfigParser()
        config.read(filename, encoding='utf-8')
        lang_setting = config.get('Settings', 'lang', fallback='auto')
        if lang_setting != 'auto':
            return lang_setting
    
    # Автоопределение по системной локали
    sys_lang = locale.getdefaultlocale()[0]
    return 'ru' if sys_lang and sys_lang.startswith('ru') else 'en'

def load_config(filename='config.ini', lang_override=None):
    # Автосоздание базового конфига с секциями сообщений
    if not os.path.exists(filename):
        logging.info(_log('config_created', filename=filename))
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('[Settings]\n')
            f.write('interval_minutes = 20\n')
            f.write('message_mode = random\n')
            f.write('lang = auto\n\n')
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

    interval = config.getint('Settings', 'interval_minutes', fallback=20)
    mode = config.get('Settings', 'message_mode', fallback='random')
    lang_setting = config.get('Settings', 'lang', fallback='auto')

    # Выбор языка: аргумент > конфиг > язык системы
    lang = lang_override or lang_setting
    if lang == 'auto':
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

def init_notifier():
    system = platform.system()
    logging.debug(_log('notifier_init', system=system))
    
    if system == "Darwin":
        logging.info(_log('using_macos'))
        def notify(msg):
            safe_msg = str(msg).replace('"', '\\"').replace("\n", " ")
            logging.debug(_log('notification_sending_macos', msg=msg[:50]))
            try:
                subprocess.run(["osascript", "-e", f'display notification "{safe_msg}" with title "EyeCare"'], check=True)
                logging.debug(_log('notification_sent'))
            except subprocess.CalledProcessError as e:
                logging.error(_log('notify_error_macos', error=e))
    elif system == "Linux":
        logging.info(_log('using_linux'))
        def notify(msg):
            logging.debug(_log('notification_sending_linux', msg=msg[:50]))
            try:
                subprocess.run(["notify-send", "EyeCare", str(msg)], check=True)
                logging.debug(_log('notification_sent'))
            except subprocess.CalledProcessError as e:
                logging.error(_log('notify_error_linux', error=e))
            except FileNotFoundError:
                logging.error(_log('notify_not_found_linux'))
    elif system == "Windows":
        try:
            from win11toast import toast
            logging.info(_log('using_win11'))
            def notify(msg):
                logging.debug(_log('notification_sending_win11', msg=msg[:50]))
                try:
                    toast("EyeCare", msg)
                    logging.debug(_log('notification_sent'))
                except Exception as e:
                    logging.error(_log('notify_error_win11', error=e))
        except ImportError:
            try:
                from win10toast import ToastNotifier
                logging.info(_log('using_win10'))
                toaster = ToastNotifier()
                def notify(msg):
                    logging.debug(_log('notification_sending_win10', msg=msg[:50]))
                    try:
                        toaster.show_toast("EyeCare", str(msg), duration=5)
                        logging.debug(_log('notification_sent'))
                    except Exception as e:
                        logging.error(_log('notify_error_win10', error=e))
            except ImportError:
                logging.warning(_log('notifier_fallback'))
                def notify(msg):
                    print(f"[EyeCare] {msg}")
                    logging.debug(_log('notification_console', msg=msg))
    else:
        logging.warning(_log('unknown_system', system=system))
        def notify(msg):
            print(f"[EyeCare] {msg}")
            logging.debug(_log('notification_console', msg=msg))
    return notify

def create_tray_icon():
    """Создает простую иконку для системного трея"""
    # Создаем изображение 64x64 с прозрачным фоном
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Рисуем простую иконку глаза
    # Внешний круг (глаз)
    draw.ellipse([8, 16, 56, 48], fill=(100, 150, 200, 255), outline=(50, 100, 150, 255), width=2)
    # Внутренний круг (зрачок)
    draw.ellipse([24, 28, 40, 36], fill=(50, 50, 50, 255))
    # Блик
    draw.ellipse([28, 30, 32, 32], fill=(255, 255, 255, 255))
    
    return image

class TrayManager:
    def __init__(self, notify_func, messages, mode, lang):
        self.notify = notify_func
        self.messages = messages
        self.mode = mode
        self.lang = lang
        self.idx = 0
        self.paused = False
        self.running = True
        
        # Создаем меню трея
        self.menu = pystray.Menu(
            pystray.MenuItem("Pause" if lang == 'en' else "Пауза", self.toggle_pause),
            pystray.MenuItem("Check now" if lang == 'en' else "Проверить сейчас", self.check_now),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit" if lang == 'en' else "Выход", self.quit_app)
        )
        
        # Создаем иконку трея
        self.icon = pystray.Icon(
            "EyeCare",
            create_tray_icon(),
            "EyeCare Reminder",
            self.menu
        )
    
    def toggle_pause(self, icon=None, item=None):
        """Переключает состояние паузы"""
        self.paused = not self.paused
        status = "Paused" if self.lang == 'en' else "Приостановлено"
        if not self.paused:
            status = "Resumed" if self.lang == 'en' else "Возобновлено"
        logging.info(_log('pause_enabled' if self.paused else 'pause_disabled'))
        self.notify(status)
    
    def check_now(self, icon=None, item=None):
        """Показывает уведомление немедленно"""
        msg = random.choice(self.messages) if self.mode == 'random' else self.messages[self.idx % len(self.messages)]
        self.idx += 1
        logging.info(_log('manual_check'))
        self.notify(msg)
    
    def quit_app(self, icon=None, item=None):
        """Выход из приложения"""
        logging.info(_log('quitting'))
        self.running = False
        self.icon.stop()
    
    def shutdown(self):
        """Корректное завершение: останавливает цикл и трей, безопасно и идемпотентно"""
        logging.debug(_log('shutdown_start'))
        if self.running:
            self.running = False
        try:
            if hasattr(self, 'icon') and self.icon is not None:
                self.icon.stop()
                logging.debug(_log('shutdown_tray'))
        except Exception as e:
            # Игнорируем ошибки остановки иконки (например, если уже остановлена)
            logging.debug(_log('shutdown_tray_error', error=e))
    
    def run(self):
        """Запускает трей в отдельном потоке"""
        self.icon.run()
    
    def start_timer_thread(self, interval):
        """Запускает основной таймер в отдельном потоке"""
        def timer_loop():
            logging.info(_log('timer_started', interval=interval))
            while self.running:
                if not self.paused:
                    logging.debug(_log('timer_waiting', interval=interval))
                    time.sleep(interval * 60)
                    if self.running and not self.paused:
                        msg = random.choice(self.messages) if self.mode == 'random' else self.messages[self.idx % len(self.messages)]
                        self.idx += 1
                        logging.info(_log('auto_notification', num=self.idx, msg=msg[:50]))
                        self.notify(msg)
                else:
                    time.sleep(1)  # Короткий сон при паузе
        
        timer_thread = threading.Thread(target=timer_loop, daemon=True)
        timer_thread.start()
        logging.debug(_log('timer_thread_started'))
        return timer_thread

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='EyeCare Reminder - напоминания для здоровья глаз')
    parser.add_argument('--lang', type=str, help='Язык интерфейса (ru, en, auto)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробное логирование (DEBUG уровень)')
    args = parser.parse_args()
    
    # Определяем язык до настройки логирования
    lang = get_language(lang_override=args.lang)
    set_log_language(lang)
    
    # Настройка логирования
    setup_logging(verbose=args.verbose)
    logging.info("=" * 50)
    logging.info(_log('startup'))
    logging.info("=" * 50)
    
    interval, messages, mode, lang = load_config(lang_override=args.lang)
    logging.info(_log('config_loaded', lang=lang, interval=interval, mode=mode, count=len(messages)))
    
    notify = init_notifier()
    
    # Создаем менеджер системного трея
    logging.info(_log('init_tray'))
    tray_manager = TrayManager(notify, messages, mode, lang)
    
    # Запускаем таймер в отдельном потоке
    timer_thread = tray_manager.start_timer_thread(interval)
    
    # Единая функция очистки ресурсов и завершения
    def cleanup():
        logging.info(_log('cleanup'))
        tray_manager.shutdown()

    # Обработчики сигналов для корректного завершения (SIGINT/SIGTERM)
    def handle_termination(signum, frame):
        reason = {
            getattr(signal, 'SIGINT', None): 'SIGINT',
            getattr(signal, 'SIGTERM', None): 'SIGTERM'
        }.get(signum, str(signum))
        logging.info(_log('signal_received', signal=reason))
        cleanup()
    
    try:
        # Запускаем системный трей (блокирующий вызов)
        # Регистрируем обработчики перед запуском цикла трея
        logging.info(_log('signal_registration'))
        try:
            signal.signal(signal.SIGINT, handle_termination)
        except Exception as e:
            logging.debug(_log('signal_error', signal='SIGINT', error=e))
        try:
            signal.signal(signal.SIGTERM, handle_termination)
        except Exception as e:
            logging.debug(_log('signal_error', signal='SIGTERM', error=e))
        
        logging.info(_log('tray_starting'))
        tray_manager.run()
    except KeyboardInterrupt:
        logging.info(_log('keyboard_interrupt'))
    except Exception as e:
        logging.error(_log('critical_error', error=e), exc_info=True)
    finally:
        cleanup()
        logging.info(_log('app_exited'))

if __name__ == "__main__":
    main()
