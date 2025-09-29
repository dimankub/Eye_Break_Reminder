import time
import os
import platform
import sys
import configparser

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
            os.system(f"osascript -e 'display notification \"{msg}\" with title \"EyeCare\"'")
    elif system == "Linux":
        def notify(msg):
            os.system(f'notify-send "EyeCare" "{msg}"')
    elif system == "Windows":
        try:
            from win11toast import toast
            def notify(msg):
                toast("EyeCare", msg, duration="short")
        except ImportError:
            print("Для работы уведомлений на Windows установите пакет win11toast: pip install win11toast")
            sys.exit(1)
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
