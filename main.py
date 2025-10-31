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

def setup_logging(verbose=False):
    """Настройка логирования с уровнями INFO/DEBUG"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def load_config(filename='config.ini', lang_override=None):
    # Автосоздание базового конфига с секциями сообщений
    if not os.path.exists(filename):
        logging.info(f"Создание нового конфигурационного файла: {filename}")
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

    logging.debug(f"Загружена конфигурация: интервал={interval} мин, режим={mode}, язык={lang}, сообщений={len(messages)}")
    return interval, messages, mode, lang

def init_notifier():
    system = platform.system()
    logging.debug(f"Инициализация нотификатора для системы: {system}")
    
    if system == "Darwin":
        logging.info("Использование osascript для macOS уведомлений")
        def notify(msg):
            safe_msg = str(msg).replace('"', '\\"').replace("\n", " ")
            logging.debug(f"Отправка уведомления через osascript: {msg[:50]}...")
            try:
                subprocess.run(["osascript", "-e", f'display notification "{safe_msg}" with title "EyeCare"'], check=True)
                logging.debug("Уведомление успешно отправлено")
            except subprocess.CalledProcessError as e:
                logging.error(f"Ошибка при отправке уведомления через osascript: {e}")
    elif system == "Linux":
        logging.info("Использование notify-send для Linux уведомлений")
        def notify(msg):
            logging.debug(f"Отправка уведомления через notify-send: {msg[:50]}...")
            try:
                subprocess.run(["notify-send", "EyeCare", str(msg)], check=True)
                logging.debug("Уведомление успешно отправлено")
            except subprocess.CalledProcessError as e:
                logging.error(f"Ошибка при отправке уведомления через notify-send: {e}")
            except FileNotFoundError:
                logging.error("notify-send не найден. Убедитесь, что установлен libnotify-bin")
    elif system == "Windows":
        try:
            from win11toast import toast
            logging.info("Использование win11toast для Windows уведомлений")
            def notify(msg):
                logging.debug(f"Отправка уведомления через win11toast: {msg[:50]}...")
                try:
                    toast("EyeCare", msg)
                    logging.debug("Уведомление успешно отправлено")
                except Exception as e:
                    logging.error(f"Ошибка при отправке уведомления через win11toast: {e}")
        except ImportError:
            try:
                from win10toast import ToastNotifier
                logging.info("Использование win10toast для Windows уведомлений")
                toaster = ToastNotifier()
                def notify(msg):
                    logging.debug(f"Отправка уведомления через win10toast: {msg[:50]}...")
                    try:
                        toaster.show_toast("EyeCare", str(msg), duration=5)
                        logging.debug("Уведомление успешно отправлено")
                    except Exception as e:
                        logging.error(f"Ошибка при отправке уведомления через win10toast: {e}")
            except ImportError:
                logging.warning("Библиотеки win11toast и win10toast не найдены, используется консольный вывод")
                def notify(msg):
                    print(f"[EyeCare] {msg}")
                    logging.debug(f"Вывод в консоль (fallback): {msg}")
    else:
        logging.warning(f"Неизвестная система {system}, используется консольный вывод")
        def notify(msg):
            print(f"[EyeCare] {msg}")
            logging.debug(f"Вывод в консоль (fallback): {msg}")
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
        logging.info(f"Пауза {'включена' if self.paused else 'выключена'}")
        self.notify(status)
    
    def check_now(self, icon=None, item=None):
        """Показывает уведомление немедленно"""
        msg = random.choice(self.messages) if self.mode == 'random' else self.messages[self.idx % len(self.messages)]
        self.idx += 1
        logging.info(f"Ручная проверка: отправка уведомления")
        self.notify(msg)
    
    def quit_app(self, icon=None, item=None):
        """Выход из приложения"""
        logging.info("Завершение работы по запросу пользователя")
        self.running = False
        self.icon.stop()
    
    def shutdown(self):
        """Корректное завершение: останавливает цикл и трей, безопасно и идемпотентно"""
        logging.debug("Начало процедуры завершения работы")
        if self.running:
            self.running = False
        try:
            if hasattr(self, 'icon') and self.icon is not None:
                self.icon.stop()
                logging.debug("Иконка трея остановлена")
        except Exception as e:
            # Игнорируем ошибки остановки иконки (например, если уже остановлена)
            logging.debug(f"Ошибка при остановке иконки (игнорируется): {e}")
    
    def run(self):
        """Запускает трей в отдельном потоке"""
        self.icon.run()
    
    def start_timer_thread(self, interval):
        """Запускает основной таймер в отдельном потоке"""
        def timer_loop():
            logging.info(f"Таймер запущен с интервалом {interval} минут")
            while self.running:
                if not self.paused:
                    logging.debug(f"Ожидание {interval} минут до следующего уведомления...")
                    time.sleep(interval * 60)
                    if self.running and not self.paused:
                        msg = random.choice(self.messages) if self.mode == 'random' else self.messages[self.idx % len(self.messages)]
                        self.idx += 1
                        logging.info(f"Автоматическое уведомление (сообщение #{self.idx}): {msg[:50]}...")
                        self.notify(msg)
                else:
                    time.sleep(1)  # Короткий сон при паузе
        
        timer_thread = threading.Thread(target=timer_loop, daemon=True)
        timer_thread.start()
        logging.debug("Поток таймера запущен")
        return timer_thread

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='EyeCare Reminder - напоминания для здоровья глаз')
    parser.add_argument('--lang', type=str, help='Язык интерфейса (ru, en, auto)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробное логирование (DEBUG уровень)')
    args = parser.parse_args()
    
    # Настройка логирования
    setup_logging(verbose=args.verbose)
    logging.info("=" * 50)
    logging.info("Запуск EyeCare Reminder")
    logging.info("=" * 50)
    
    interval, messages, mode, lang = load_config(lang_override=args.lang)
    logging.info(f"Конфигурация загружена: язык={lang}, интервал={interval} мин, режим={mode}, сообщений={len(messages)}")
    
    notify = init_notifier()
    
    # Создаем менеджер системного трея
    logging.info("Инициализация менеджера системного трея")
    tray_manager = TrayManager(notify, messages, mode, lang)
    
    # Запускаем таймер в отдельном потоке
    timer_thread = tray_manager.start_timer_thread(interval)
    
    # Единая функция очистки ресурсов и завершения
    def cleanup():
        logging.info("Очистка ресурсов и завершение работы")
        tray_manager.shutdown()

    # Обработчики сигналов для корректного завершения (SIGINT/SIGTERM)
    def handle_termination(signum, frame):
        reason = {
            getattr(signal, 'SIGINT', None): 'SIGINT',
            getattr(signal, 'SIGTERM', None): 'SIGTERM'
        }.get(signum, str(signum))
        logging.info(f"Получен сигнал {reason}. Завершаем работу...")
        cleanup()
    
    try:
        # Запускаем системный трей (блокирующий вызов)
        # Регистрируем обработчики перед запуском цикла трея
        logging.info("Регистрация обработчиков сигналов")
        try:
            signal.signal(signal.SIGINT, handle_termination)
        except Exception as e:
            logging.debug(f"Не удалось зарегистрировать SIGINT (возможно, Windows): {e}")
        try:
            signal.signal(signal.SIGTERM, handle_termination)
        except Exception as e:
            logging.debug(f"Не удалось зарегистрировать SIGTERM (возможно, Windows): {e}")
        
        logging.info("Запуск системного трея (приложение работает в фоновом режиме)")
        tray_manager.run()
    except KeyboardInterrupt:
        logging.info("EyeCare остановлен пользователем (KeyboardInterrupt)")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        cleanup()
        logging.info("EyeCare завершил работу")

if __name__ == "__main__":
    main()
