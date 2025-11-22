"""Главный модуль приложения EyeCare Reminder"""
import time
import random
import signal
import threading
import logging
from PIL import Image, ImageDraw
import pystray

from cli import parse_args
from config import get_language, load_config, save_interval, MIN_INTERVAL, MAX_INTERVAL, set_log_language as set_config_log_language
from notifiers import init_notifier, set_log_language as set_notifier_log_language
from logging_config import setup_logging, set_log_language, log

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
    """Менеджер системного трея"""
    
    def __init__(self, notify_func, messages, mode, lang):
        self.notify = notify_func
        self.messages = messages
        self.mode = mode
        self.lang = lang
        self.idx = 0
        self.paused = False
        self.running = True
        self.interval_minutes = None  # будет присвоено в start_timer_thread
        self._seconds_left = None
        self._lock = threading.Lock()
        
        # Подменю выбора интервала
        preset_intervals = [10, 15, 20, 30, 45, 60]
        def make_interval_item(minutes):
            label = f"{minutes} min" if self.lang == 'en' else f"{minutes} мин"
            def on_select(icon, item):
                self.set_interval(minutes)
            def is_checked(item):
                return self.interval_minutes == minutes
            return pystray.MenuItem(label, on_select, checked=is_checked)

        interval_submenu = pystray.Menu(*[make_interval_item(m) for m in preset_intervals])

        # Создаем меню трея
        self.menu = pystray.Menu(
            pystray.MenuItem("Pause" if lang == 'en' else "Пауза", self.toggle_pause),
            pystray.MenuItem("Check now" if lang == 'en' else "Проверить сейчас", self.check_now),
            pystray.MenuItem("Interval" if lang == 'en' else "Интервал", interval_submenu),
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
        logging.info(log('pause_enabled' if self.paused else 'pause_disabled'))
        self.notify(status)
    
    def check_now(self, icon=None, item=None):
        """Показывает уведомление немедленно"""
        msg = random.choice(self.messages) if self.mode == 'random' else self.messages[self.idx % len(self.messages)]
        self.idx += 1
        logging.info(log('manual_check'))
        self.notify(msg)
    
    def quit_app(self, icon=None, item=None):
        """Выход из приложения"""
        logging.info(log('quitting'))
        self.running = False
        self.icon.stop()

    def set_interval(self, minutes):
        """Устанавливает новый интервал (в минутах), сохраняет в конфиг и сбрасывает таймер"""
        try:
            minutes = int(minutes)
        except Exception:
            return
        if minutes < MIN_INTERVAL:
            minutes = MIN_INTERVAL
        if minutes > MAX_INTERVAL:
            minutes = MAX_INTERVAL
        with self._lock:
            self.interval_minutes = minutes
            self._seconds_left = minutes * 60
        # Сохраняем в config.ini
        save_interval(minutes)
        # Уведомляем пользователя
        msg = (f"Interval set to {minutes} min" if self.lang == 'en' else f"Интервал установлен: {minutes} мин")
        self.notify(msg)
    
    def shutdown(self):
        """Корректное завершение: останавливает цикл и трей, безопасно и идемпотентно"""
        logging.debug(log('shutdown_start'))
        if self.running:
            self.running = False
        try:
            if hasattr(self, 'icon') and self.icon is not None:
                self.icon.stop()
                logging.debug(log('shutdown_tray'))
        except Exception as e:
            # Игнорируем ошибки остановки иконки (например, если уже остановлена)
            logging.debug(log('shutdown_tray_error', error=e))
    
    def run(self):
        """Запускает трей в отдельном потоке"""
        self.icon.run()
    
    def start_timer_thread(self, interval):
        """Запускает основной таймер в отдельном потоке с динамическим интервалом"""
        with self._lock:
            self.interval_minutes = interval
            self._seconds_left = interval * 60

        def timer_loop():
            logging.info(log('timer_started', interval=self.interval_minutes))
            while self.running:
                if self.paused:
                    time.sleep(1)
                    continue

                # Тик раз в секунду, учитывая возможное изменение интервала
                time.sleep(1)
                with self._lock:
                    if self._seconds_left is None:
                        self._seconds_left = self.interval_minutes * 60
                    else:
                        self._seconds_left = max(0, self._seconds_left - 1)

                    seconds_left = self._seconds_left
                    current_interval = self.interval_minutes

                if seconds_left % 60 == 0:
                    logging.debug(log('timer_waiting', interval=current_interval))

                if seconds_left == 0 and self.running and not self.paused:
                    msg = random.choice(self.messages) if self.mode == 'random' else self.messages[self.idx % len(self.messages)]
                    self.idx += 1
                    logging.info(log('auto_notification', num=self.idx, msg=msg[:50]))
                    self.notify(msg)
                    with self._lock:
                        self._seconds_left = self.interval_minutes * 60

        timer_thread = threading.Thread(target=timer_loop, daemon=True)
        timer_thread.start()
        logging.debug(log('timer_thread_started'))
        return timer_thread

def main():
    """Главная функция приложения"""
    # Парсинг аргументов командной строки
    args = parse_args()
    
    # Определяем язык до настройки логирования
    lang = get_language(lang_override=args.lang)
    # Устанавливаем язык для всех модулей логирования
    set_log_language(lang)
    set_config_log_language(lang)
    set_notifier_log_language(lang)
    
    # Настройка логирования
    setup_logging(verbose=args.verbose)
    logging.info("=" * 50)
    logging.info(log('startup'))
    logging.info("=" * 50)
    
    # Загрузка конфигурации
    interval, messages, mode, lang = load_config(lang_override=args.lang)
    logging.info(log('config_loaded', lang=lang, interval=interval, mode=mode, count=len(messages)))
    
    # Инициализация notifier'а
    notify = init_notifier(lang=lang)
    
    # Создаем менеджер системного трея
    logging.info(log('init_tray'))
    tray_manager = TrayManager(notify, messages, mode, lang)
    
    # Запускаем таймер в отдельном потоке
    timer_thread = tray_manager.start_timer_thread(interval)
    
    # Единая функция очистки ресурсов и завершения
    def cleanup():
        logging.info(log('cleanup'))
        tray_manager.shutdown()

    # Обработчики сигналов для корректного завершения (SIGINT/SIGTERM)
    def handle_termination(signum, frame):
        reason = {
            getattr(signal, 'SIGINT', None): 'SIGINT',
            getattr(signal, 'SIGTERM', None): 'SIGTERM'
        }.get(signum, str(signum))
        logging.info(log('signal_received', signal=reason))
        cleanup()
    
    try:
        # Запускаем системный трей (блокирующий вызов)
        # Регистрируем обработчики перед запуском цикла трея
        logging.info(log('signal_registration'))
        try:
            signal.signal(signal.SIGINT, handle_termination)
        except Exception as e:
            logging.debug(log('signal_error', signal='SIGINT', error=e))
        try:
            signal.signal(signal.SIGTERM, handle_termination)
        except Exception as e:
            logging.debug(log('signal_error', signal='SIGTERM', error=e))
        
        logging.info(log('tray_starting'))
        tray_manager.run()
    except KeyboardInterrupt:
        logging.info(log('keyboard_interrupt'))
    except Exception as e:
        logging.error(log('critical_error', error=e), exc_info=True)
    finally:
        cleanup()
        logging.info(log('app_exited'))

if __name__ == "__main__":
    main()
