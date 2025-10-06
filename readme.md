# 👁️ EyeCare Reminder
A cross-platform tool that reminds you to take regular breaks for your eyes.
Кроссплатформенный инструмент для напоминаний о перерывах для глаз.

## 📝 Description
EyeCare helps reduce eye strain by showing desktop notifications to remind you about the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds.

## ✨ Features
Adjustable reminder interval and custom message via config.ini
Native notifications for Windows, Linux, and macOS
Lightweight and runs in the background

## ⚙️ Installation
Make sure Python 3.7+ is installed.
Download or clone this repository.
(Windows only) Install the notification library:

```bash
pip install win11toast
```

## 🛠️ Configuration
To customize, create or edit the config.ini in the same folder:

> [Settings]
> interval_minutes = 20
> message = Take a short eye break! Look away for a bit.


## 🚀 Usage
Start the script:

```bash
python eyecare.py
```
Press Ctrl+C to stop the reminder.

## 🔔 Example Notification
💡 Take a short eye break! Look away for a bit.