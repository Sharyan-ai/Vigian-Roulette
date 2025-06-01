import logging
import random
import time
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)
from telegram.constants import UpdateType

# تنظیم لاگینگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "YOUR_BOT_TOKEN_HERE"

# متغیرهای سراسری
games = {}
bot_status = {}
no_limit_mode = {}
allow_parallel_games = {}
hourly_game_limit = {}
limit_enabled = {}
unauthorized_attempts = {}
roulette_misuse_attempts = {}
edit_lock = asyncio.Lock()

def reset_global_vars():
    """بازنشانی متغیرهای سراسری در شروع ربات"""
    global games, bot_status, no_limit_mode, allow_parallel_games, hourly_game_limit, limit_enabled, unauthorized_attempts, roulette_misuse_attempts
    games.clear()
    bot_status.clear()
    no_limit_mode.clear()
    allow_parallel_games.clear()
    hourly_game_limit.clear()
    limit_enabled.clear()
    unauthorized_attempts.clear()
    roulette_misuse_attempts.clear()
    logger.info("Global variables reset.")

async def restrict_silenced(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id in games and user.id in games[chat_id].get("silenced_users", {}):
        if time.time() < games[chat_id]["silenced_users"][user.id]:
            try:
                await asyncio.sleep(0.5)
                await update.message.delete()
            except Exception as e:
                logger.error(f"Error deleting message: {e}")
            await update.message.reply_text("شما در حالت سکوت هستید و نمی‌توانید دستور اجرا کنید.")
            return True
        else:
            del games[chat_id]["silenced_users"][user.id]
    return False

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await restrict_silenced(update, context):
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    now = time.time()
    hour = int(now // 3600)

    if limit_enabled.get(chat_id, True):
        if chat_id not in hourly_game_limit:
            hourly_game_limit[chat_id] = {}

        if hourly_game_limit[chat_id].get(hour) is None:
            hourly_game_limit[chat_id][hour] = 0

        if hourly_game_limit[chat_id][hour] >= 10:
            msg = await update.message.reply_text("در این گروه حداکثر ۱۰ بازی در ساعت مجاز است. لطفاً بعداً تلاش کنید.")
            try:
                await asyncio.sleep(0.5)
                await update.message.delete()
            except Exception as e:
                logger.error(f"Error deleting command message: {e}")
            return

        hourly_game_limit[chat_id][hour] += 1

    if bot_status.get(chat_id, True) is False:
        msg = await update.message.reply_text("ربات فعلاً غیرفعال است.")
        try:
            await asyncio.sleep(0.5)
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command message: {e}")
        return

    if update.effective_chat.type not in ['group', 'supergroup']:
        msg = await update.message.reply_text("این دستور فقط در گروه‌ها قابل استفاده است.")
        try:
            await asyncio.sleep(0.5)
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command message: {e}")
        return

    if not allow_parallel_games.get(chat_id, False):
        if chat_id in games and games[chat_id].get("active", False):
            msg = await update.message.reply_text("یه بازی در جریانه. صبر کن تموم شه.")
            try:
                await asyncio.sleep(0.5)
                await update.message.delete()
            except Exception as e:
                logger.error(f"Error deleting command message: {e}")
            return

    # شمارش تلاش‌های نادرست برای /roulette
    if chat_id not in roulette_misuse_attempts:
        roulette_misuse_attempts[chat_id] = {}
    if user.id not in roulette_misuse_attempts[chat_id]:
        roulette_misuse_attempts[chat_id][user.id] = 0

    if not update.message.reply_to_message or (update.message.reply_to_message.sender_chat and update.message.reply_to_message.sender_chat.type == 'channel'):
        roulette_misuse_attempts[chat_id][user.id] += 1
        if roulette_misuse_attempts[chat_id][user.id] >= 3:
            if chat_id not in games:
                games[chat_id] = {"silenced_users": {}}
            games[chat_id]["silenced_users"][user.id] = time.time() + 21600
            roulette_misuse_attempts[chat_id][user.id] = 0
            await update.message.reply_text(
                f"{user.mention_html()} به دلیل استفاده نادرست از دستور /roulette (بدون ریپلای یا ریپلای روی پیام کانال) برای ۶ ساعت سکوت شد!",
                parse_mode="HTML"
            )
            try:
                await asyncio.sleep(0.5)
                await update.message.delete()
            except Exception as e:
                logger.error(f"Error deleting command message: {e}")
            return
        msg = await update.message.reply_text(
            f"باید روی پیام یه نفر ریپلای بزنی، نه پیام کانال! تلاش {roulette_misuse_attempts[chat_id][user.id]}/3"
        )
        try:
            await asyncio.sleep(0.5)
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command message: {e}")
        return

    if update.message.reply_to_message.from_user.id == (await context.bot.get_me()).id:
        msg = await update.message.reply_text(f"{update.effective_user.first_name} نمیتونی با خود ربات بازی رو شروع کنی")
        try:
            await asyncio.sleep(0.5)
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command message: {e}")
        return

    opponent = update.message.reply_to_message.from_user

    if opponent.id == user.id:
        msg = await update.message.reply_text("با خودت که نمی‌تونی بازی کنی!")
        try:
            await asyncio.sleep(0.5)
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command message: {e}")
        return

    now = time.time()
    last_times = games.get(chat_id, {}).get("last_game_time", {})
    if last_times is None:
        last_times = {}

    if not no_limit_mode.get(chat_id, False) and (
        now - last_times.get(user.id, 0) < 3600 or now - last_times.get(opponent.id, 0) < 3600
    ):
        msg = await update.message.reply_text("یکی از بازیکن‌ها تو یه ساعت گذشته بازی کرده.")
        try:
            await asyncio.sleep(0.5)
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command message: {e}")
        return

    games[chat_id] = {
        "active": False,
        "requester": user,
        "opponent": opponent,
        "round": 1,
        "shots_left": 3,
        "bullet_pos": random.randint(1, 3),
        "current_turn": None,
        "silenced_users": games.get(chat_id, {}).get("silenced_users", {}),
        "last_game_time": last_times,
        "game_msg_id": None,
        "last_activity": now,
    }

    keyboard = [
        [
            InlineKeyboardButton("قبول ✅", callback_data="accept_game"),
            InlineKeyboardButton("رد ❌", callback_data="reject_game")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    msg = await update.message.reply_text(
        f"{opponent.mention_html()}، {user.mention_html()} می‌خواد باهات رولت بازی کنه!",
        parse_mode="HTML",
        reply_markup=markup
    )
    games[chat_id]["game_msg_id"] = msg.message_id
    try:
        await asyncio.sleep(0.5)
        await update.message.delete()
    except Exception as e:
        logger.error(f"Error deleting command message: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = update.effective_chat.id

    if chat_id not in games:
        await query.answer("هیچ بازی فعالی نیست.", show_alert=True)
        return

    game = games[chat_id]
    msg_id = game.get("game_msg_id")

    if query.data == "accept_game":
        if user.id != game["opponent"].id:
            await query.answer("فقط کسی که دعوت شده می‌تونه قبول کنه.", show_alert=True)
            return

        now = time.time()
        game["active"] = True
        game["current_turn"] = game["requester"]
        game["round"] = 1
        game["shots_left"] = 3
        game["bullet_pos"] = random.randint(1, 3)
        game["last_game_time"][game["requester"].id] = now
        game["last_game_time"][game["opponent"].id] = now
        game["last_activity"] = now

        await query.edit_message_text(f"بازی شروع شد! نوبت {game['current_turn'].mention_html()} است.", parse_mode="HTML")
        await edit_shot_buttons(chat_id, context, game, msg_id)

    elif query.data == "reject_game":
        if user.id != game["opponent"].id:
            await query.answer("فقط طرف مقابل می‌تونه رد کنه.", show_alert=True)
            return
        await query.edit_message_text("بازی رد شد.")
        try:
            await asyncio.sleep(300)  # 5 minutes
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            logger.error(f"Error deleting end game message: {e}")
        games.pop(chat_id)

    elif query.data.startswith("shoot_"):
        if not game["active"] or not game.get("current_turn"):
            await query.answer("بازی فعالی نیست.", show_alert=True)
            return

        if user.id != game["current_turn"].id:
            await query.answer("نوبت شما نیست!", show_alert=True)
            return

        if user.id in game.get("silenced_users", {}) and time.time() < game["silenced_users"][user.id]:
            await query.answer("شما سکوت هستید.", show_alert=True)
            return

        shot_num = int(query.data.split("_")[1])
        if shot_num > game["shots_left"]:
            await query.answer("این شلیک معتبر نیست.", show_alert=True)
            return

        game["last_activity"] = time.time()

        if shot_num == game["bullet_pos"]:
            game["active"] = False
            game["silenced_users"][user.id] = time.time() + 300
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=f"{user.mention_html()} شلیک کرد و کشته شد! 😵 برای ۵ دقیقه سکوت شد.",
                parse_mode="HTML"
            )
            try:
                await asyncio.sleep(300)  # 5 minutes
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception as e:
                logger.error(f"Error deleting end game message: {e}")
            games.pop(chat_id)
            return

        game["shots_left"] -= 1

        if game["shots_left"] == 0:
            if game["round"] >= 6:
                game["active"] = False
                await context.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="۶ راند بدون مرگ. بازی تموم شد.")
                try:
                    await asyncio.sleep(300)  # 5 minutes
                    await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                except Exception as e:
                    logger.error(f"Error deleting end game message: {e}")
                games.pop(chat_id)
            else:
                game["round"] += 1
                game["shots_left"] = 3
                game["bullet_pos"] = random.randint(1, 3)
                game["current_turn"] = game["opponent"] if user.id == game["requester"].id else game["requester"]
                game["last_activity"] = time.time()
                await edit_shot_buttons(chat_id, context, game, msg_id)
        else:
            game["current_turn"] = game["opponent"] if user.id == game["requester"].id else game["requester"]
            game["last_activity"] = time.time()
            await query.answer("بی‌خطر بود!")
            await edit_shot_buttons(chat_id, context, game, msg_id)

async def edit_shot_buttons(chat_id, context, game, msg_id):
    if game["shots_left"] == 0:
        return

    buttons = [InlineKeyboardButton(f"شلیک {i}", callback_data=f"shoot_{i}") for i in range(1, game["shots_left"] + 1)]
    keyboard = InlineKeyboardMarkup([buttons])

    text = f"راند {game['round']} شروع شد! نوبت {game['current_turn'].mention_html()} است."

    async with edit_lock:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error editing message: {e}")

async def check_silence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.edited_message
    if not msg:
        return

    chat_id = msg.chat.id
    user = msg.from_user

    if chat_id in games:
        silenced = games[chat_id].get("silenced_users", {})
        if user.id in silenced:
            if time.time() < silenced[user.id]:
                try:
                    await asyncio.sleep(0.5)
                    await msg.delete()
                except Exception as e:
                    logger.error(f"Error deleting message: {e}")
            else:
                del silenced[user.id]

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not await is_admin(context, chat_id, user.id):
        msg = await update.message.reply_text("فقط ادمین می‌تونه این کارو بکنه.")
        try:
            await asyncio.sleep(15)  # 15 seconds for non-admin
            await msg.delete()
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command or response message: {e}")
        return

    if not update.message.reply_to_message:
        msg = await update.message.reply_text("دستور رو روی پیام طرف بزن.")
        try:
            await asyncio.sleep(60)  # 1 minute for admin
            await msg.delete()
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command or response message: {e}")
        return

    target = update.message.reply_to_message.from_user
    if chat_id in games and target.id in games[chat_id].get("silenced_users", {}):
        del games[chat_id]["silenced_users"][target.id]
        msg = await update.message.reply_text(f"سکوت {target.first_name} برداشته شد.")
        try:
            await asyncio.sleep(60)  # 1 minute for admin
            await msg.delete()
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command or response message: {e}")
    else:
        msg = await update.message.reply_text("این کاربر سکوت نیست.")
        try:
            await asyncio.sleep(60)  # 1 minute for admin
            await msg.delete()
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command or response message: {e}")

async def remove_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.info(f"Executing /remove_limit by {user.username} in chat {chat_id}")
    if chat_id in games and "last_game_time" in games[chat_id]:
        games[chat_id]["last_game_time"].clear()
        msg = await update.message.reply_text("محدودیت یک‌ساعته بازی برای همه حذف شد.")
        try:
            await asyncio.sleep(60)  # 1 minute for admin
            await msg.delete()
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command or response message: {e}")
    else:
        msg = await update.message.reply_text("هیچ محدودیتی برای حذف وجود ندارد.")
        try:
            await asyncio.sleep(60)  # 1 minute for admin
            await msg.delete()
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command or response message: {e}")

async def toggle_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.info(f"Executing /toggle_limit by {user.username} in chat {chat_id}")
    no_limit_mode[chat_id] = not no_limit_mode.get(chat_id, False)
    status = "فعال شد ✅" if no_limit_mode[chat_id] else "غیرفعال شد ❌"
    msg = await update.message.reply_text(f"حالت بدون محدودیت زمانی {status}")
    try:
        await asyncio.sleep(60)  # 1 minute for admin
        await msg.delete()
        await update.message.delete()
    except Exception as e:
        logger.error(f"Error deleting command or response message: {e}")

async def toggle_parallel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.info(f"Executing /toggle_parallel by {user.username} in chat {chat_id}")
    allow_parallel_games[chat_id] = not allow_parallel_games.get(chat_id, False)
    status = "فعال شد ✅ (اجازه چند بازی همزمان)" if allow_parallel_games[chat_id] else "غیرفعال شد ❌ (فقط یک بازی در لحظه)"
    msg = await update.message.reply_text(f"حالت بازی همزمان {status}")
    try:
        await asyncio.sleep(60)  # 1 minute for admin
        await msg.delete()
        await update.message.delete()
    except Exception as e:
        logger.error(f"Error deleting command or response message: {e}")

async def enable_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.info(f"Executing /on by {user.username} in chat {chat_id}")
    bot_status[chat_id] = True
    msg = await update.message.reply_text("ربات فعال شد.")
    try:
        await asyncio.sleep(60)  # 1 minute for admin
        await msg.delete()
        await update.message.delete()
    except Exception as e:
        logger.error(f"Error deleting command or response message: {e}")

async def disable_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.info(f"Executing /off by {user.username} in chat {chat_id}")
    bot_status[chat_id] = False
    msg = await update.message.reply_text("ربات غیرفعال شد.")
    try:
        await asyncio.sleep(60)  # 1 minute for admin
        await msg.delete()
        await update.message.delete()
    except Exception as e:
        logger.error(f"Error deleting command or response message: {e}")

async def stop_all_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.info(f"Executing /stop_all_games by {user.username} in chat {chat_id}")
    if chat_id in games and games[chat_id].get("active", False):
        games[chat_id]["active"] = False
        msg = await update.message.reply_text("✅ تمام بازی‌های در جریان متوقف شدند.")
        try:
            await asyncio.sleep(300)  # 5 minutes
            await context.bot.delete_message(chat_id=chat_id, message_id=games[chat_id]["game_msg_id"])
            await msg.delete()
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command, response, or end game message: {e}")
        games.pop(chat_id)
    else:
        msg = await update.message.reply_text("هیچ بازی فعالی برای توقف وجود نداره.")
        try:
            await asyncio.sleep(60)  # 1 minute for admin
            await msg.delete()
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting command or response message: {e}")

async def toggle_hourly_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.info(f"Executing /toggle_hourly_limit by {user.username} in chat {chat_id}")
    limit_enabled[chat_id] = not limit_enabled.get(chat_id, True)
    status = "فعال" if limit_enabled[chat_id] else "غیرفعال"
    msg = await update.message.reply_text(f"محدودیت ۱۰ بازی در ساعت در این گروه {status} شد.")
    try:
        await asyncio.sleep(60)  # 1 minute for admin
        await msg.delete()
        await update.message.delete()
    except Exception as e:
        logger.error(f"Error deleting command or response message: {e}")

async def is_admin(context, chat_id, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("""
📜 راهنمای ربات رولت روسی:

🔫 /roulette — شروع بازی (ریپلای به پیام یه نفر)
🕊 /unmute — برداشتن سکوت (فقط ادمین)
🚫 /remove_limit — حذف محدودیت یک‌ساعته بازی (فقط ادمین)
🕹 /toggle_limit — فعال/غیرفعال‌سازی حالت بدون محدودیت (فقط ادمین)
🎮 /toggle_parallel — فعال/غیرفعال کردن حالت چند بازی همزمان (فقط ادمین)
📛 /stop_all_games — توقف همه بازی‌های فعال (فقط ادمین)
🟢 /on — فعال‌سازی ربات (فقط ادمین)
🔴 /off — غیرفعال‌سازی ربات (فقط ادمین)
📖 /help — راهنما
⏰ /toggle_hourly_limit — فعال/غیرفعال کردن محدودیت ۱۰ بازی در ساعت (فقط ادمین)

⏳ بعد از مرگ در بازی، بازیکن به مدت ۵ دقیقه سکوت می‌شود.
⛔ در صورت تخلف (استفاده غیرمجاز از دستورات ادمین یا استفاده نادرست از /roulette)، کاربر برای ۶ ساعت سکوت می‌شود.
⛔ در سکوت نمی‌تواند پیام دهد و پیام‌هایش حذف می‌شود.
    """)
    try:
        await asyncio.sleep(0.5)
        await update.message.delete()
    except Exception as e:
        logger.error(f"Error deleting command message: {e}")

async def check_inactive_games(context: ContextTypes.DEFAULT_TYPE):
    while True:
        now = time.time()
        for chat_id in list(games.keys()):
            game = games.get(chat_id)
            if game and game.get("active", False) and now - game.get("last_activity", 0) > 600:  # 10 minutes
                game["active"] = False
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=game["game_msg_id"],
                        text="بازی به دلیل عدم فعالیت بیش از ۱۰ دقیقه متوقف شد."
                    )
                    await asyncio.sleep(300)  # 5 minutes
                    await context.bot.delete_message(chat_id=chat_id, message_id=game["game_msg_id"])
                except Exception as e:
                    logger.error(f"Error handling inactive game in chat {chat_id}: {e}")
                games.pop(chat_id)
        await asyncio.sleep(60)  # Check every minute

def create_wrapped_handler(handler):
    async def wrapped_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await restrict_silenced(update, context):
            logger.info(f"User {update.effective_user.id} is silenced, command {handler.__name__} blocked.")
            return

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        if not await is_admin(context, chat_id, user_id):
            logger.info(f"User {update.effective_user.id} is not admin for command {handler.__name__}.")

            if chat_id not in unauthorized_attempts:
                unauthorized_attempts[chat_id] = {}
            if user_id not in unauthorized_attempts[chat_id]:
                unauthorized_attempts[chat_id][user_id] = 0

            unauthorized_attempts[chat_id][user_id] += 1

            if unauthorized_attempts[chat_id][user_id] >= 3:
                if chat_id not in games:
                    games[chat_id] = {"silenced_users": {}}
                games[chat_id]["silenced_users"][user_id] = time.time() + 21600
                unauthorized_attempts[chat_id][user_id] = 0
                await update.message.reply_text(
                    f"{update.effective_user.mention_html()} به دلیل استفاده غیرمجاز از دستورات ادمین برای ۶ ساعت سکوت شد!",
                    parse_mode="HTML"
                )
                try:
                    await asyncio.sleep(0.5)
                    await update.message.delete()
                except Exception as e:
                    logger.error(f"Error deleting command message: {e}")
                return

            msg = await update.message.reply_text(
                f"فقط ادمین‌ها می‌تونن این دستور رو اجرا کنن. تلاش {unauthorized_attempts[chat_id][user_id]}/3"
            )
            try:
                await asyncio.sleep(15)  # 15 seconds for non-admin
                await msg.delete()
                await update.message.delete()
            except Exception as e:
                logger.error(f"Error deleting command or response message: {e}")
            return

        logger.info(f"Executing command {handler.__name__} by {update.effective_user.username}")
        await handler(update, context)
    return wrapped_handler

def main():
    reset_global_vars()
    app = ApplicationBuilder().token(TOKEN).build()
    print("Bot starting...")

    restricted_commands = [
        ("remove_limit", remove_limit),
        ("toggle_limit", toggle_limit),
        ("toggle_parallel", toggle_parallel),
        ("stop_all_games", stop_all_games),
        ("on", enable_bot),
        ("off", disable_bot),
        ("toggle_hourly_limit", toggle_hourly_limit),
        ("unmute", unmute),
    ]

    for command, handler in restricted_commands:
        app.add_handler(CommandHandler(command, create_wrapped_handler(handler)))

    app.add_handler(CommandHandler("roulette", start_game))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, check_silence))
    app.add_handler(MessageHandler(filters.ALL, check_silence))
    print("Handlers registered")

    # Start the inactive games checker
    app.job_queue.run_repeating(check_inactive_games, interval=60)

    app.run_polling()

if __name__ == "__main__":
    main()
