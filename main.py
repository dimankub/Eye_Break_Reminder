import time
import os
import platform
import sys

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
    notify = init_notifier()
    print("Запущено напоминание по правилу 20-20-20. Нажмите Ctrl+C для выхода.")
    try:
        while True:
            time.sleep(20 * 60)  # 20 минут
            notify("Встань, моргни и глянь вдаль. Глаза скажут спасибо.")
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")

if __name__ == "__main__":
    main()
