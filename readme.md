# 👁️ EyeCare Reminder
A cross-platform tool that reminds you to take regular breaks for your eyes.

## 📝 Description
EyeCare helps reduce eye strain by showing desktop notifications to remind you about the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds.

## ✨ Features
Adjustable reminder interval and custom message via config.ini.

Native notifications for Windows, Linux, and macOS.

System tray integration with pause/test/interval/quit menu.

Change interval from tray (10/15/20/30/45/60 min), applies instantly and is saved to config.ini.

Lightweight and runs in the background.

Multiple message rotation, including random mode.

Built-in localization (English and Russian).

## ⚙️ Installation
Make sure Python 3.7+ is installed.

Download or clone this repository.

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install win11toast pystray Pillow
```

## 🛠️ Configuration
Edit the config.ini file in the same folder as the script (created on first run):

```
[Settings]
interval_minutes = 20
message_mode = random
lang = auto

[Messages.ru]
default = Встань, моргни и глянь вдаль. Глаза скажут спасибо.
messages =
    Посмотри вдаль и моргни пару раз.
    Потянись, дай глазам отдохнуть.
    Переведи взгляд на что-то дальнее.

[Messages.en]
default = Stand up, blink, and look into the distance. Your eyes will thank you.
messages =
    Look away from the screen for 20 seconds.
    Stretch a bit and rest your eyes.
    Blink a few times and refocus.
```
## Parameters
- `interval_minutes`: time between notifications (in minutes).
- `message_mode`: how messages are selected.
  - `single` — fixed message.
  - `random` — random selection.
  - any other — sequential rotation.
- `lang`: language for notifications (`auto`, `en`, or `ru`)
  - `auto` detects system language automatically 

## 🚀 Usage
Start the script:

```bash
python main.py
```

The application will run in the background with a system tray icon. Right-click the tray icon to access the menu:

- **Pause/Resume**: Temporarily stop or resume reminders.
- **Check now**: Trigger an immediate reminder.
- **Interval**: Choose a preset interval (10/15/20/30/45/60 min). The new value is applied immediately and saved to `config.ini`.
- **Exit**: Close the application.

You can also stop the application by pressing Ctrl+C in the terminal or using the Exit option in the tray menu.

## 🔔 Example Notification
💡 Stand up, blink, and look into the distance. Your eyes will thank you.