import time
import os
import platform
import sys
import configparser
import subprocess
import random

def load_config(filename='config.ini'):
    # Автосоздание конфига при первом запуске
    if not os.path.exists(filename):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'interval_minutes': '20',
            'message_mode': 'single',
            'message': 'Встань, моргни и глянь вдаль. Глаза скажут спасибо.',
            'messages': '\n# Дополнительные сообщения:\n# Ещё немного — и глаза скажут спасибо!\n# Встань, потянись и посмотри вдаль.'
        }
        with open(filename, 'w', encoding='utf-8') as f:
            config.write(f)

    config = configparser.ConfigParser()
    config.read(filename, encoding='utf-8')

    interval = 20
    messages = ["Встань, моргни и глянь вдаль. Глаза скажут спасибо."]
    message_mode = 'single'

    if 'Settings' in config:
        interval = config.getint('Settings', 'interval_minutes', fallback=20)
        message_mode = config.get('Settings', 'message_mode', fallback='single').lower()

        raw_messages = []
        if config.has_option('Settings', 'messages'):
            val = config.get('Settings', 'messages')
            for line in val.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    raw_messages.append(line)
        # добавляем одиночное сообщение, если нет списка
        if config.has_option('Settings', 'message'):
            raw_messages.insert(0, config.get('Settings', 'message'))
        if raw_messages:
            messages = raw_messages

    return interval, messages, message_mode

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
    interval, messages, mode = load_config()
    print(f"Запущено напоминание по правилу 20-20-20 с интервалом {interval} минут в режиме {mode}. Нажмите Ctrl+C для выхода.")
    try:
        notify = init_notifier()
        idx = 0
        while True:
            time.sleep(interval * 60)
            if len(messages) == 1:
                msg = messages[0]
            elif mode == 'random':
                msg = random.choice(messages)
            else:
                msg = messages[idx % len(messages)]
                idx += 1
            notify(msg)
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")

if __name__ == "__main__":
    main()
