# 👁️ EyeCare Reminder
A cross-platform tool that reminds you to take regular breaks for your eyes.

## 📝 Description
EyeCare helps reduce eye strain by showing desktop notifications to remind you about the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds.

## ✨ Features
Adjustable reminder interval and custom message via config.ini

Native notifications for Windows, Linux, and macOS

Lightweight and runs in the background

Multiple message rotation, including random mode

Built-in localization (English and Russian)

## ⚙️ Installation
Make sure Python 3.7+ is installed.

Download or clone this repository.

(Windows only) Install the notification library:

```bash
pip install win11toast
```

## 🛠️ Configuration
Edit the config.ini file in the same folder as the script (created on first run):

```
[Settings]
interval_minutes = 20
message_mode = random
lang = auto

[Messages.en]
default = Stand up, blink, and look into the distance.
messages =
Look 20 feet away for at least 20 seconds.
Relax your eyes and stretch.
Blink and refocus your eyes.

[Messages.ru]
default = Встань, моргни и глянь вдаль. Глаза скажут спасибо.
messages =
Потянись и посмотри вдаль.
Пройди пару шагов.
Переведи взгляд на что-то дальнее.
```
## Parameters
- `interval_minutes`: time between notifications  
- `message_mode`: how messages are selected  
  - `single` — fixed message  
  - `random` — random selection  
  - (any other) — sequential rotation  
- `lang`: language for notifications (`auto`, `en`, or `ru`)  
  - `auto` detects system language 

## 🚀 Usage
Start the script:

```bash
python main.py
```
Press Ctrl+C to stop the reminder.

## 🔔 Example Notification
💡 Take a short eye break! Look away for a bit.