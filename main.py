import time
import os
import platform
import sys
import configparser
import subprocess

def load_config(filename='config.ini'):
    config = configparser.ConfigParser()
    config.read(filename)
    interval = 20
    message = "Встань, моргни и глянь вдаль. Глаза скажут спасибо."
    if 'Settings' in config:
        interval = config.getint('Settings', 'interval_minutes', fallback=20)
        message = config.get('Settings', 'message', fallback=message)
    return interval, message

def init_notifier():
    system = platform.system()
    if system == "Darwin":
        def notify(msg):
            safe_msg = str(msg).replace('"', '\\"').replace("\n", " ")
            script = f'display notification "{safe_msg}" with title "EyeCare"'
            subprocess.run(["osascript", "-e", script], check=False)
    elif system == "Linux":
        def notify(msg):
            subprocess.run(["notify-send", "EyeCare", str(msg)], check=False)
    elif system == "Windows":
        try:
            from win11toast import toast
            def notify(msg):
                toast("EyeCare", msg, duration="short")
        except ImportError:
            try:
                from win10toast import ToastNotifier
                _toaster = ToastNotifier()
                def notify(msg):
                    _toaster.show_toast("EyeCare", str(msg), duration=5)
            except ImportError:
                print("Уведомления Windows: установите win11toast или win10toast (pip install win11toast win10toast). Используется консольный режим.")
                def notify(msg):
                    print(f"[EyeCare] {msg}")
    else:
        print(f"Неизвестная ОС: {system}. Уведомления не поддерживаются.")
        sys.exit(1)
    return notify

def main():
    interval, message = load_config()
    print(f"Запущено напоминание по правилу 20-20-20 с интервалом {interval} минут. Нажмите Ctrl+C для выхода.")
    try:
        notify = init_notifier()
        while True:
            time.sleep(interval * 60)
            notify(message)
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")

if __name__ == "__main__":
    main()