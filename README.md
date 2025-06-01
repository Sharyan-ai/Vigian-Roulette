# Telegram Russian Roulette Bot

This project is a Telegram bot designed for playing Russian Roulette in Telegram groups. It allows users to engage in the game with specific rules and provides administrative controls for group admins.

## Features
- **Start Game**: Users can start a game using the `/roulette` command by replying to another user's message.
- **Game Management**: Supports time limits (one game per hour per user), hourly game limits (max 10 games), and optional parallel games.
- **User Management**: Users who misuse commands or attempt unauthorized admin actions are silenced for 6 hours.
- **Silence Mode**: After losing a game, a user is silenced for 5 minutes, preventing them from sending messages.
- **Admin Commands**:
  - `/unmute`: Remove silence from a user.
  - `/remove_limit`: Clear the one-hour game restriction.
  - `/toggle_limit`: Enable/disable no-limit mode.
  - `/toggle_parallel`: Enable/disable parallel games.
  - `/on` and `/off`: Enable or disable the bot.
  - `/stop_all_games`: Stop all active games.
  - `/toggle_hourly_limit`: Enable/disable the 10-games-per-hour limit.
- **Help**: The `/help` command displays the full bot guide.
- **Automatic Management**: Inactive games are stopped after 10 minutes of inactivity.

## Prerequisites
- Python 3.8 or higher
- `python-telegram-bot` library version 20.0 or higher
- A Telegram bot token from [BotFather](https://t.me/BotFather)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/telegram-russian-roulette-bot.git
   cd telegram-russian-roulette-bot
   ```

2. Install the required dependencies:
   ```bash
   pip install python-telegram-bot
   ```

3. Set your bot token in `bot.py`:
   ```python
   TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## Project Structure
- `bot.py`: The main bot file containing all game logic and command handling.

## Usage
1. Add the bot to a Telegram group.
2. Use the `/help` command to view the list of commands.
3. To start a game, reply to a user's message and use the `/roulette` command.
4. Admins can use management commands to control the bot and games.

## Important Notes
- The bot only works in groups and supergroups.
- Users attempting unauthorized admin commands will be silenced for 6 hours after 3 failed attempts.
- Messages from silenced users are automatically deleted.
- Ensure the bot has necessary permissions (delete messages, manage group) for optimal performance.

## Contributing
To contribute to this project:
1. Fork the repository.
2. Create a new branch for your changes.
3. Submit a Pull Request.

## License
This project is licensed under the [MIT License](LICENSE).

## Contact
For questions or issues, open an Issue on the GitHub repository or contact the developer.



# ربات رولت روسی تلگرام

این پروژه یک ربات تلگرام برای بازی رولت روسی است که در گروه‌های تلگرامی قابل استفاده است. این ربات به کاربران امکان می‌دهد بازی رولت را با قوانین مشخص انجام دهند و شامل قابلیت‌های مدیریتی برای ادمین‌های گروه است.

## ویژگی‌ها

- **شروع بازی**: کاربران می‌توانند با دستور `/roulette` و ریپلای روی پیام یک نفر، بازی را شروع کنند.
- **مدیریت بازی**: پشتیبانی از محدودیت‌های زمانی (یک بازی در ساعت برای هر کاربر)، محدودیت تعداد بازی‌ها در ساعت (حداکثر ۱۰ بازی)، و امکان بازی‌های همزمان.
- **مدیریت کاربران**: کاربرانی که تخلف کنند (استفاده نادرست از دستورات یا دستورات ادمین) برای ۶ ساعت سکوت می‌شوند.
- **حالت سکوت**: پس از مرگ در بازی، کاربر برای ۵ دقیقه از ارسال پیام محروم می‌شود.
- **دستورات ادمین**:
  - `/unmute`: برداشتن سکوت یک کاربر
  - `/remove_limit`: حذف محدودیت زمانی یک‌ساعته
  - `/toggle_limit`: فعال/غیرفعال کردن حالت بدون محدودیت زمانی
  - `/toggle_parallel`: فعال/غیرفعال کردن بازی‌های همزمان
  - `/on` و `/off`: فعال یا غیرفعال کردن ربات
  - `/stop_all_games`: توقف تمام بازی‌های فعال
  - `/toggle_hourly_limit`: فعال/غیرفعال کردن محدودیت ۱۰ بازی در ساعت
- **راهنما**: دستور `/help` برای نمایش راهنمای کامل ربات
- **مدیریت خودکار**: توقف بازی‌های غیرفعال پس از ۱۰ دقیقه عدم فعالیت

## پیش‌نیازها

- Python 3.8 یا بالاتر
- کتابخانه `python-telegram-bot` نسخه 20.0 یا بالاتر
- دسترسی به توکن ربات تلگرام از طریق BotFather

## نصب و راه‌اندازی

1. مخزن را کلون کنید:

   ```bash
   git clone https://github.com/yourusername/telegram-russian-roulette-bot.git
   cd telegram-russian-roulette-bot
   ```

2. کتابخانه‌های مورد نیاز را نصب کنید:

   ```bash
   pip install python-telegram-bot
   ```

3. توکن ربات را در فایل `bot.py` تنظیم کنید:

   ```python
   TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```

4. ربات را اجرا کنید:

   ```bash
   python bot.py
   ```

## ساختار پروژه

- `bot.py`: فایل اصلی ربات که شامل تمام منطق بازی و مدیریت دستورات است.

## استفاده

1. ربات را به یک گروه تلگرامی اضافه کنید.
2. از دستور `/help` برای مشاهده لیست دستورات استفاده کنید.
3. برای شروع بازی، روی پیام یک کاربر ریپلای کنید و دستور `/roulette` را وارد کنید.
4. ادمین‌ها می‌توانند از دستورات مدیریتی برای کنترل رفتار ربات و بازی‌ها استفاده کنند.

## نکات مهم

- ربات فقط در گروه‌ها و سوپرگروه‌ها کار می‌کند.
- کاربرانی که سعی کنند دستورات ادمین را بدون مجوز اجرا کنند، پس از ۳ تلاش ناموفق برای ۶ ساعت سکوت می‌شوند.
- پیام‌های ارسالی توسط کاربران سکوت‌شده به‌طور خودکار حذف می‌شوند.
- برای عملکرد بهتر، اطمینان حاصل کنید که ربات مجوزهای لازم (حذف پیام‌ها، مدیریت گروه) را در گروه دارد.

## مشارکت

برای مشارکت در توسعه این پروژه:

1. پروژه را فورک کنید.
2. تغییرات خود را در یک شاخه جدید اعمال کنید.
3. درخواست Pull Request ارسال کنید.

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

## تماس

 برای سؤالات یا گزارش مشکلات، می‌توانید یک Issue در مخزن گیت‌هاب باز کنید یا با توسعه‌دهنده تماس بگیرید.
