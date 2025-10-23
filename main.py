import time
import os
import sys
import platform
import random
import configparser
import subprocess
import argparse
import locale

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

def main():
    interval, messages, mode, lang = load_config()
    print(f"Запущено напоминание (язык: {lang}) с интервалом {interval} мин, режим: {mode}")
    notify = init_notifier()
    idx = 0

    try:
        while True:
            time.sleep(interval * 60)
            msg = random.choice(messages) if mode == 'random' else messages[idx % len(messages)]
            idx += 1
            notify(msg)
    except KeyboardInterrupt:
        print("\nEyeCare остановлен пользователем.")

if __name__ == "__main__":
    main()
