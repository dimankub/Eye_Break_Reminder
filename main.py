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
from PIL import Image, ImageDraw
import pystray

def load_config(filename='config.ini'):
    # Автосоздание базового конфига с секциями сообщений
    if not os.path.exists(filename):
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', type=str, help='Language override (e.g., ru, en)')
    args, _ = parser.parse_known_args()

    lang = args.lang or lang_setting
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

    return interval, messages, mode, lang

def init_notifier():
    system = platform.system()
    if system == "Darwin":
        def notify(msg):
            safe_msg = str(msg).replace('"', '\\"').replace("\n", " ")
            subprocess.run(["osascript", "-e", f'display notification "{safe_msg}" with title "EyeCare"'])
    elif system == "Linux":
        def notify(msg):
            subprocess.run(["notify-send", "EyeCare", str(msg)])
    elif system == "Windows":
        try:
            from win11toast import toast
            def notify(msg):
                toast("EyeCare", msg)
        except ImportError:
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                def notify(msg):
                    toaster.show_toast("EyeCare", str(msg), duration=5)
            except ImportError:
                def notify(msg):
                    print(f"[EyeCare] {msg}")
    else:
        def notify(msg):
            print(f"[EyeCare] {msg}")
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
        self.notify(status)
    
    def check_now(self, icon=None, item=None):
        """Показывает уведомление немедленно"""
        msg = random.choice(self.messages) if self.mode == 'random' else self.messages[self.idx % len(self.messages)]
        self.idx += 1
        self.notify(msg)
    
    def quit_app(self, icon=None, item=None):
        """Выход из приложения"""
        self.running = False
        self.icon.stop()
    
    def shutdown(self):
        """Корректное завершение: останавливает цикл и трей, безопасно и идемпотентно"""
        if self.running:
            self.running = False
        try:
            if hasattr(self, 'icon') and self.icon is not None:
                self.icon.stop()
        except Exception:
            # Игнорируем ошибки остановки иконки (например, если уже остановлена)
            pass
    
    def run(self):
        """Запускает трей в отдельном потоке"""
        self.icon.run()
    
    def start_timer_thread(self):
        """Запускает основной таймер в отдельном потоке"""
        def timer_loop():
            interval, _, _, _ = load_config()
            while self.running:
                if not self.paused:
                    time.sleep(interval * 60)
                    if self.running and not self.paused:
                        msg = random.choice(self.messages) if self.mode == 'random' else self.messages[self.idx % len(self.messages)]
                        self.idx += 1
                        self.notify(msg)
                else:
                    time.sleep(1)  # Короткий сон при паузе
        
        timer_thread = threading.Thread(target=timer_loop, daemon=True)
        timer_thread.start()
        return timer_thread

def main():
    interval, messages, mode, lang = load_config()
    print(f"Запущено напоминание (язык: {lang}) с интервалом {interval} мин, режим: {mode}")
    notify = init_notifier()
    
    # Создаем менеджер системного трея
    tray_manager = TrayManager(notify, messages, mode, lang)
    
    # Запускаем таймер в отдельном потоке
    timer_thread = tray_manager.start_timer_thread()
    
    # Единая функция очистки ресурсов и завершения
    def cleanup():
        tray_manager.shutdown()

    # Обработчики сигналов для корректного завершения (SIGINT/SIGTERM)
    def handle_termination(signum, frame):
        reason = {
            getattr(signal, 'SIGINT', None): 'SIGINT',
            getattr(signal, 'SIGTERM', None): 'SIGTERM'
        }.get(signum, str(signum))
        print(f"\nПолучен сигнал {reason}. Завершаем...")
        cleanup()
    
    try:
        # Запускаем системный трей (блокирующий вызов)
        # Регистрируем обработчики перед запуском цикла трея
        try:
            signal.signal(signal.SIGINT, handle_termination)
        except Exception:
            pass
        try:
            signal.signal(signal.SIGTERM, handle_termination)
        except Exception:
            pass
        tray_manager.run()
    except KeyboardInterrupt:
        print("\nEyeCare остановлен пользователем.")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
