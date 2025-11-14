import json,re
import os
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup,ReactionTypeEmoji
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ChatMemberHandler,CallbackQueryHandler
)
from telegram import ChatPermissions,ChatMember
from telegram.error import NetworkError, TimedOut, RetryAfter,Forbidden,BadRequest
import asyncio
from dotenv import load_dotenv
#----------------------------------------TIMESTAMP DEFINE-------------------------------------

def to_timestamp(time_value):
    """Converts a datetime object or string to timestamp (float)."""
    if isinstance(time_value, (int, float)):
        return float(time_value)
    elif isinstance(time_value, datetime):
        return time_value.timestamp()
    elif isinstance(time_value, str):
        try:
            return datetime.fromisoformat(time_value).timestamp()
        except Exception:
            return float(time_value)
    else:
        raise TypeError(f"Unsupported time type: {type(time_value)}")
#------------------ FORMAT DURATION----------
def format_duration(seconds):
    """Converts seconds into a readable duration like '2h 15m 5s'."""
    seconds = int(seconds)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    duration_parts = []
    if hours > 0:
        duration_parts.append(f"{hours}h")
    if minutes > 0:
        duration_parts.append(f"{minutes}m")
    if seconds > 0 or not duration_parts:
        duration_parts.append(f"{seconds}s")

    return " ".join(duration_parts)

# ================== CONFIG ==================
AFK_FILE = "group_afk.json"
BOT_FILE = "bot_data.json"
DEVELOPER_ID = 8122079391   # Your Telegram ID
SUDO_USERS = []    # Add sudo IDs here
BOT_USERNAME = "Nex_afk56_bot"  # Replace without @
SUPPORT_GROUP = "https://t.me/+L6IFLg-87uIxOTA9"

START_TIME = time.time()

# ================== DATA ==================
afk_data = {}
bot_data = {"groups": [], "users": {}, "owner": DEVELOPER_ID, "sudo_users": SUDO_USERS}

# Load AFK data
if os.path.exists(AFK_FILE):
    with open(AFK_FILE, "r") as f:
        afk_data = json.load(f)

# Load bot data
if os.path.exists(BOT_FILE):
    with open(BOT_FILE, "r") as f:
        bot_data = json.load(f)

def save_afk():
    with open(AFK_FILE, "w") as f:
        json.dump(afk_data, f, indent=4)

def save_bot():
    with open(BOT_FILE, "w") as f:
        json.dump(bot_data, f, indent=4)

ANTIINVITE_FILE = "antiinvite.json"
INVITE_LOG_FILE = "invite_log.txt"

# Load or create settings
if os.path.exists(ANTIINVITE_FILE):
    with open(ANTIINVITE_FILE, "r") as f:
        antiinvite_settings = json.load(f)
else:
    antiinvite_settings = {}
def save_antiinvite():
    with open(ANTIINVITE_FILE, "w") as f:
        json.dump(antiinvite_settings, f, indent=4)
# ======================= FEEDBACK HANDLER ========================
COMPLAINTS_FILE = "complaints.json"
BOT_OWNER_ID = 8122079391  # ⚠️ Replace with your Telegram user ID

# -------- Storage Helpers --------
def load_complaints():
    if os.path.exists(COMPLAINTS_FILE):
        try:
            with open(COMPLAINTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_complaints(data):
    tmp = COMPLAINTS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, COMPLAINTS_FILE)

complaints = load_complaints()
# =======================CHAT SESSION ==========================
CHAT_SESSION_FILE = "chat_sessions.json"

def load_chat_sessions():
    """Load active chat sessions from JSON file."""
    if os.path.exists(CHAT_SESSION_FILE):
        try:
            with open(CHAT_SESSION_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ChatMode] Failed to load chat sessions: {e}")
            return {}
    return {}

def save_chat_sessions():
    """Save current chat sessions to JSON file."""
    try:
        with open(CHAT_SESSION_FILE, "w") as f:
            json.dump(chat_mode_sessions, f, indent=2)
    except Exception as e:
        print(f"[ChatMode] Failed to save chat sessions: {e}")

# ✅ Global variable — lives in memory while the bot runs
chat_mode_sessions = load_chat_sessions()
# ================== EXTRA ==========================
with open("bot_data.json", "r") as f:
    bot_data = json.load(f)

OWNER_ID = bot_data.get("owner")
SUDO_USERS = bot_data.get("sudo_users", [])
# =================== EXTRA2 ===========================
BOT_DATA_FILE = "bot_data.json"


def load_bot_data():
    with open(BOT_DATA_FILE, "r") as f:
        return json.load(f)


def save_bot_data(data):
    with open(BOT_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================== ERROR HANDLER ==================
def safe_handler(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await func(update, context)
        except (NetworkError, TimedOut, RetryAfter) as e:
            print(f"[WARNING] Network issue in {func.__name__}: {e}")
            await time.sleep(5)
        except Exception as e:
            print(f"[ERROR] Exception in {func.__name__}: {e}")
    return wrapper

# ================== START ==================
@safe_handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import json, os, time
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    chat_type = update.effective_chat.type
    user = update.effective_user
    msg = update.message

    record_path = "start_records.json"

    # Ensure record file exists
    if not os.path.exists(record_path):
        with open(record_path, "w") as f:
            json.dump({}, f)

    with open(record_path, "r") as f:
        start_records = json.load(f)

    key = str(msg.chat_id)  # Use chat_id to identify per chat

    # Delete old /start message from this chat
    try:
        old_msg_id = start_records.get(key)
        if old_msg_id:
            await context.bot.delete_message(chat_id=msg.chat_id, message_id=old_msg_id)
    except Exception:
        pass

    # --------------------------- PRIVATE CHAT ----------------------------
    if chat_type == "private":
        keyboard = [
            [InlineKeyboardButton("𝔸𝕕𝕕 𝕄𝕖 𝕥𝕠 𝕘𝕣𝕠𝕦𝕡", url="https://t.me/Shadow_AFK_987_robot?startgroup=true")],
            [
                InlineKeyboardButton("𝔻𝕖𝕧𝕖𝕝𝕠𝕡𝕖𝕣", url="https://t.me/Ks_0892"),
                InlineKeyboardButton("𝕊𝕦𝕡𝕡𝕠𝕣𝕥", url=SUPPORT_GROUP),
            ],
            [InlineKeyboardButton("𝕊𝕦𝕡𝕡𝕠𝕣𝕥 𝕘𝕣𝕠𝕦𝕡", url="https://t.me/+LLAiSO5k2JUwM2Fl")],
            [InlineKeyboardButton("ℙ𝕣𝕚𝕧𝕒𝕔𝕪 ℙ𝕠𝕝𝕚𝕔𝕪", url="https://telegra.ph/Privacy-Policy-11-09-402")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent = await msg.reply_video(
            video="BAACAgUAAxkBAAIBL2kOmtgdilE1pjdS2rdY2aC5dsvnAALwFwAC3gx5VBJXvCsO2Ct1NgQ",
            caption=(
                f"👋 Hey there {user.first_name}!\n\n"
                "I’m Shadow AFK Bot, here to keep your Telegram chats updated while you’re away.\n\n"
                "Just activate me before you go AFK, and I’ll automatically reply to anyone who messages you letting them know you’ll get back soon.\n\n"
                "No more missed messages or awkward delays!\n\n"
                "Simple, handy, and ready 24/7 to keep your friends and groups in the loop.\n\n"
                "Just set your AFK status, and relax! ✨\n\n"
                "Use /help to get commands of bot."
            ),
            reply_markup=reply_markup,
        )

        # Save new message ID
        start_records[key] = sent.message_id
        with open(record_path, "w") as f:
            json.dump(start_records, f, indent=4)

    # --------------------------- GROUP CHAT ----------------------------
    else:
        uptime = time.time() - START_TIME
        hrs, rem = divmod(int(uptime), 3600)
        mins, secs = divmod(rem, 60)

        sent = await msg.reply_text(
            f"ʜᴇʟʟᴏ,ꜱʜᴀᴅᴏᴡ ʙᴏᴛ ɪꜱ ᴀʟɪᴠᴇ ꜱɪɴᴄᴇ: {hrs}h {mins}m {secs}s"
        )

        # Save message ID for that group
        start_records[key] = sent.message_id
        with open(record_path, "w") as f:
            json.dump(start_records, f, indent=4)
# ================== HELP ==================
@safe_handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Help Menu:\n\n"
        "/afk - 𝕊𝕖𝕥 𝕪𝕠𝕦𝕣𝕤𝕖𝕝𝕗 𝔸𝔽𝕂\n\n"
        "/afklist - 𝕊𝕙𝕠𝕨 𝕝𝕚𝕤𝕥 𝕠𝕗 𝕦𝕤𝕖𝕣𝕤 𝕨𝕙𝕠 𝕒𝕣𝕖 𝔸𝔽𝕂 (𝕒𝕕𝕞𝕚𝕟𝕤 𝕠𝕟𝕝𝕪)\n\n"
        "/ping - 𝔹𝕠𝕥 𝕦𝕡𝕥𝕚𝕞𝕖\n\n"
        "/botstats - 𝔹𝕠𝕥 𝕊𝕥𝕒𝕥𝕚𝕥𝕚𝕔𝕤(𝕆𝕨𝕟𝕖𝕣 & 𝕊𝕦𝕕𝕠 𝕆𝕟𝕝𝕪)\n\n"
        "/broadcast <groups/users/all> - ℝ𝕖𝕡𝕝𝕪 𝕥𝕠 𝕞𝕖𝕤𝕤𝕒𝕘𝕖 𝕥𝕠 𝔹𝕣𝕠𝕒𝕕𝕔𝕒𝕤𝕥 𝕒 𝕞𝕖𝕤𝕤𝕒𝕘𝕖 𝕥𝕠 𝕥𝕙𝕖 𝕘𝕣𝕠𝕦𝕡𝕤/𝕦𝕤𝕖𝕣/𝕓𝕠𝕥𝕙(𝔸𝕕𝕞𝕚𝕟 & 𝕊𝕦𝕕𝕠 𝕠𝕟𝕝𝕪)\n\n"
        "/pinall - ℝ𝕖𝕡𝕝𝕪 𝕥𝕙𝕖 𝕞𝕖𝕤𝕤𝕒𝕘𝕖 𝕨𝕚𝕥𝕙 𝕥𝕙𝕚𝕤 𝕔𝕠𝕞𝕞𝕒𝕟𝕕 𝕥𝕠 𝕡𝕚𝕟 𝕥𝕙𝕖 𝕞𝕖𝕤𝕤𝕒𝕘𝕖 𝕚𝕟 𝕖𝕧𝕖𝕣𝕪 𝕔𝕙𝕒𝕥 (𝕆𝕨𝕟𝕖𝕣 & 𝕊𝕦𝕕𝕠 𝕠𝕟𝕝𝕪)\n\n"
        "/sendto <groupid/userid> - ℝ𝕖𝕡𝕝𝕪 𝕥𝕠 𝕒𝕟𝕪 𝕞𝕖𝕤𝕤𝕒𝕘𝕖 𝕗𝕠𝕣 𝕥𝕒𝕣𝕘𝕖𝕥𝕖𝕕 𝕓𝕣𝕠𝕒𝕕𝕔𝕒𝕤𝕥 (𝕆𝕨𝕟𝕖𝕣 & 𝕊𝕦𝕕𝕠 𝕠𝕟𝕝𝕪)\n\n"
        "/start - 𝕊𝕥𝕒𝕣𝕥 𝕥𝕙𝕖 𝕓𝕠𝕥"
    )

# ================== AFK ==================
@safe_handler
async def afk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ /afk works only in groups!")
        return

    user = update.effective_user
    chat_id = str(update.effective_chat.id)
    user_id = str(user.id)
    reason = " ".join(context.args) if context.args else "No reason given"

    if chat_id not in afk_data:
        afk_data[chat_id] = {}

    if user_id in afk_data[chat_id]:
        await update.message.reply_text(f"⚠️ {user.mention_html()} you are already AFK!", parse_mode="HTML")
        return

    afk_data[chat_id][user_id] = {"since": time.time(), "reason": reason, "count": 0}
    save_afk()
    await update.message.reply_text(f"💤 {user.mention_html()} is now AFK!\nReason: {reason}", parse_mode="HTML")

# ================== AFK LIST ==================
@safe_handler
async def afklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    member = await chat.get_member(user.id)
    if not (member.status in ["administrator", "creator"]):
        await update.message.reply_text("❌ Only admins can use /afklist")
        return

    chat_id = str(chat.id)
    if chat_id not in afk_data or not afk_data[chat_id]:
        await update.message.reply_text("✅ No AFK users in this group")
        return

    msg_lines = ["📋 <b>AFK Users in this group:</b>\n"]
    for uid, data in afk_data[chat_id].items():
        since_ts = to_timestamp(data.get("since"))
        duration_seconds = time.time() - since_ts
        dur = format_duration(duration_seconds)
        reason = data.get("reason", "No reason given")
        user_obj = await context.bot.get_chat(uid)
        msg_lines.append(f"👤 {user_obj.mention_html()}\n   ⏳ {dur}\n   📝 {reason}\n")

    msg = "\n".join(msg_lines)
    await update.message.reply_text(msg, parse_mode="HTML")
#=================== REPLY MENTION ====================
@safe_handler
async def replymention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply to a specific message in a group using bot DM (supports text or replied media)."""
    msg = update.message
    if not msg:
        return


    # Restrict usage
    if msg.from_user.id !=bot_data["owner"] and msg.from_user.id not in bot_data["sudo_users"]:
        await msg.reply_text("❌ Only owner or sudo users can use this command.")
        return

    # Expect format: /replymention <group_id> <message_id> [optional text]
    if len(context.args) < 2:
        await msg.reply_text(
            "Usage:\n`/replymention <group_id> <message_id> [text]`\n\n"
            "If you don't include text, reply to a message to send it.",
            parse_mode="Markdown",
        )
        return

    group_id = int(context.args[0])
    message_id = int(context.args[1])
    reply_text = " ".join(context.args[2:]) if len(context.args) > 2 else None

    try:
        # --- CASE 1: Text is provided with the command
        if reply_text:
            await context.bot.send_message(
                chat_id=group_id,
                text=reply_text,
                reply_to_message_id=message_id,
                parse_mode="Markdown",
            )
            await msg.reply_text("✅ Text reply sent successfully!")
            return

        # --- CASE 2: No text provided, check if replied to a message
        if not msg.reply_to_message:
            await msg.reply_text("⚠️ You must reply to a message or include text to send.")
            return

        reply = msg.reply_to_message
        caption = reply.caption or ""

        # Send based on message type
        if reply.photo:
            await context.bot.send_photo(
                chat_id=group_id,
                photo=reply.photo[-1].file_id,
                caption=caption,
                reply_to_message_id=message_id,
            )
        elif reply.video:
            await context.bot.send_video(
                chat_id=group_id,
                video=reply.video.file_id,
                caption=caption,
                reply_to_message_id=message_id,
            )
        elif reply.document:
            await context.bot.send_document(
                chat_id=group_id,
                document=reply.document.file_id,
                caption=caption,
                reply_to_message_id=message_id,
            )
        elif reply.audio:
            await context.bot.send_audio(
                chat_id=group_id,
                audio=reply.audio.file_id,
                caption=caption,
                reply_to_message_id=message_id,
            )
        elif reply.voice:
            await context.bot.send_voice(
                chat_id=group_id,
                voice=reply.voice.file_id,
                caption=caption,
                reply_to_message_id=message_id,
            )
        elif reply.sticker:
            await context.bot.send_sticker(
                chat_id=group_id,
                sticker=reply.sticker.file_id,
                reply_to_message_id=message_id,
            )
        elif reply.text:
            await context.bot.send_message(
                chat_id=group_id,
                text=reply.text,
                reply_to_message_id=message_id,
                parse_mode="Markdown",
            )
        else:
            await msg.reply_text("⚠️ Unsupported or empty message type.")
            return

        await msg.reply_text("✅ Reply sent successfully!")

    except Exception as e:
        await msg.reply_text(f"❌ Failed to send reply:\n`{e}`", parse_mode="Markdown")
# ================== ACCEPT REQUEST ==================
@safe_handler
async def accept_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /accept <group_id> <user_id>")
        return

    group_id = int(context.args[0])
    user_id = int(context.args[1])

    try:
        await context.bot.approve_chat_join_request(chat_id=group_id, user_id=user_id)
        await update.message.reply_text(f"✅ Approved join request for user {user_id} in group {group_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to approve: {e}")

# ================== REPLY GROUP ==========================
@safe_handler
async def replygroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message to a group replying to a specific user."""
    user = update.effective_user

    # Only owner/sudo can use this
    if user.id != bot_data["owner"] and user.id not in bot_data["sudo_users"]:
        await update.message.reply_text("❌ Only owner/sudo can use this command.")
        return

    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage: `/replygroup <group_id> <user_id> <message>`",
            parse_mode="Markdown"
        )
        return

    chat_id = int(context.args[0])
    user_id = int(context.args[1])
    message_text = " ".join(context.args[2:])

    mention = f"[User](tg://user?id={user_id})"
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{mention}, {message_text}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Message sent successfully.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: `{e}`", parse_mode="Markdown")
# 
@safe_handler
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    # If used in a group, show group id too
    if chat.type in ["group", "supergroup"]:
        await update.message.reply_text(
            f"👥 <b>Group ID:</b> <code>{chat.id}</code>\n"
            f"🙋‍♂️ <b>Your ID:</b> <code>{user.id}</code>",
            parse_mode="HTML",
        )
    else:
        await update.message.reply_text(
            f"🙋‍♂️ <b>Your ID:</b> <code>{user.id}</code>",
            parse_mode="HTML",
        )
# /info → show info about a user (by reply or self)
@safe_handler
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: User = None

    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    else:
        user = update.effective_user

    info_text = (
        f"👤 <b>User Information</b>\n\n"
        f"🧾 <b>Name:</b> {user.full_name}\n"
        f"🏷 <b>Username:</b> @{user.username if user.username else 'N/A'}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"🕵️ <b>Is Bot:</b> {'Yes' if user.is_bot else 'No'}\n"
        f"🌐 <b>Language:</b> {user.language_code or 'Unknown'}"
    )

    await update.message.reply_text(info_text, parse_mode="HTML")
# ─── /whisper command ──────────────────────────────────────
@safe_handler
async def whisper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    user_id = user.id

    # Group whisper (everyone can use)
    if chat.type in ["group", "supergroup"]:
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
            target_id = target.id
            content = " ".join(context.args)
        else:
            if len(context.args) < 2:
                await update.message.reply_text("Usage: reply or `/whisper <target> <message>`", parse_mode="Markdown")
                return
            target = context.args[0]
            content = " ".join(context.args[1:])
            try:
                if target.startswith("@"):
                    user_data = await context.bot.get_chat(target)
                    target_id = user_data.id
                else:
                    target_id = int(target)
            except Exception:
                await update.message.reply_text("⚠️ Invalid or unreachable user.")
                return

        if not content.strip():
            await update.message.reply_text("⚠️ Please include a message.")
            return

        # Encode whisper data
        payload = f"{target_id}|{content}"
        encoded = base64.urlsafe_b64encode(payload.encode()).decode()

        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("💌 View Whisper", callback_data=f"whisper_{encoded}")]]
        )

        await update.message.reply_text(
            f"🤫 A secret whisper was sent to [{target.first_name if hasattr(target, 'first_name') else target}] — only they can open it!",
            reply_markup=button,
        )
        return
# DM whisper (only owner/sudo)
    elif chat.type == "private":
        if user_id != OWNER_ID and user_id not in SUDO_USERS:
            await update.message.reply_text("🚫 Only owner/sudo can send whispers from DM.")
            return

        if len(context.args) < 3:
            await update.message.reply_text("Usage: `/whisper <group_id> <target_id> <message>`", parse_mode="Markdown")
            return

        group_id = context.args[0]
        try:
            target_id = int(context.args[1])
        except ValueError:
            await update.message.reply_text("⚠️ Invalid target ID.")
            return

        content = " ".join(context.args[2:])
        if not content.strip():
            await update.message.reply_text("⚠️ Please include a message.")
            return

        payload = f"{target_id}|{content}"
        encoded = base64.urlsafe_b64encode(payload.encode()).decode()

        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("💌 View Whisper", callback_data=f"whisper_{encoded}")]]
        )

        try:
            await context.bot.send_message(
                chat_id=group_id,
                text=f"💬 Whisper sent to `{target_id}` by admin.",
                reply_markup=button,
                parse_mode="Markdown",
            )
            await update.message.reply_text("✅ Whisper sent successfully.")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Failed to send whisper:\n`{e}`", parse_mode="Markdown")

# ==================WHISPHER HANDLER  =======================
async def whisper_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    data = query.data
    if not data.startswith("whisper_"):
        return

    try:
        encoded = data.split("whisper_")[1]
        decoded = base64.urlsafe_b64decode(encoded).decode()
        target_id, content = decoded.split("|", 1)
    except Exception:
        await query.answer("⚠️ Invalid or expired whisper data.", show_alert=True)
        return

    if user_id != int(target_id):
        await query.answer("❌ You are not allowed to view this whisper!", show_alert=True)
        return

    await query.answer(content, show_alert=True)
# ================== FEEDBACK ======================
@safe_handler
async def complaint_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("📝 Usage: /complaint <your message>\nYou can also use /feedback.")
        return

    # prepare group info if in group
    group_info = ""
    if chat.type in ("group", "supergroup"):
        if chat.username:
            group_link = f"https://t.me/{chat.username}"
        else:
            group_link = f"(Private Group, ID: {chat.id})"
        group_info = f"🏷️ Group: {chat.title}\n🔗 {group_link}\n"

    # save entry
    entry = {
        "user_id": user.id,
        "username": user.username or user.full_name,
        "text": text,
        "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "chat_id": chat.id,
        "chat_title": chat.title if chat.type in ("group", "supergroup") else None,
    }
    complaints.append(entry)
    save_complaints(complaints)

    # Notify bot owner
    msg = (
        f"📩 <b>New Complaint/Feedback</b>\n"
        f"👤 From: <a href='tg://user?id={user.id}'>{user.first_name}</a> ({user.id})\n"
    )
    if group_info:
        msg += f"{group_info}"
    msg += f"🕒 {entry['date']}\n\n💬 {text}"

    try:
        await context.bot.send_message(BOT_OWNER_ID, msg, parse_mode="HTML")
    except Exception:
        pass

    await update.message.reply_text("✅ Your feedback/complaint has been sent to the bot owner. Thank you!")

# alias
feedback_command = complaint_command

# -------- /showcomplaints --------
@safe_handler
async def show_complaints_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != BOT_OWNER_ID:
        await update.message.reply_text("❌ Only the bot owner can view complaints.")
        return

    if not complaints:
        await update.message.reply_text("📭 No complaints or feedback yet.")
        return

    msg = "<b>📬 All Complaints/Feedback</b>\n\n"
    for i, c in enumerate(complaints[-10:], start=1):
        msg += (
            f"{i}. 👤 <a href='tg://user?id={c['user_id']}'>{c['username']}</a>\n"
            f"🕒 {c['date']}\n"
        )
        if c.get("chat_title"):
            msg += f"🏷️ Group: {c['chat_title']} ({c['chat_id']})\n"
        msg += f"💬 {c['text']}\n\n"

    await update.message.reply_text(msg, parse_mode="HTML")
# ================== ADD SUDO ============================
@safe_handler
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != bot_data["owner"]:
        await update.message.reply_text("❌ Only the bot owner can add sudo users.")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /addsudo <user_id or reply to user>")
        return

    try:
        target_id = int(context.args[0])
    except:
        if update.message.reply_to_message:
            target_id = update.message.reply_to_message.from_user.id
        else:
            await update.message.reply_text("⚠️ Provide a valid user ID or reply to a user's message.")
            return
    if target_id in bot_data["sudo_users"]:
        await update.message.reply_text("⚠️ That user is already a sudo user.")
        return

    bot_data["sudo_users"].append(target_id)
    save_bot()

    await update.message.reply_text(f"✅ Added user `{target_id}` as a sudo user.", parse_mode="Markdown")
    try:
        await context.bot.send_message(target_id, "🎉 You’ve been promoted to *SUDO USER* by the bot owner!", parse_mode="Markdown")
    except:
        pass
# ===≈====================== DELETE ==============================
@safe_handler
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a specific message using chat_id and message_id."""
    # Only allow owner/sudo
    user_id = str(update.effective_user.id)
    if user_id != str(bot_data["owner"]) and user_id not in str(bot_data["sudo_users"]):
        await update.message.reply_text("❌ Only owner/sudo can use this command.")
        return

    # Require two arguments: chat_id and message_id
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /delete <chat_id> <message_id>")
        return

    chat_id = context.args[0]
    message_id = context.args[1]

    try:
        await context.bot.delete_message(chat_id=int(chat_id), message_id=int(message_id))
        await update.message.reply_text(f"🗑️ Message `{message_id}` deleted from chat `{chat_id}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed to delete message:\n`{e}`", parse_mode="Markdown")
# -------------------------------
# 🔨 /ban <chat_id> <user_id>
# -------------------------------
@safe_handler
async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /ban <chat_id> <user_id>")
        return

    chat_id = int(context.args[0])
    user_id = int(context.args[1])

    try:
        await context.bot.ban_chat_member(chat_id, user_id)
        await update.message.reply_text(f"✅ User {user_id} has been banned in chat {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ban failed: {e}")


# -------------------------------
# 🔨 /unban <chat_id> <user_id>
# -------------------------------
@safe_handler
async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /unban <chat_id> <user_id>")
        return

    chat_id = int(context.args[0])
    user_id = int(context.args[1])

    try:
        await context.bot.unban_chat_member(chat_id, user_id)
        await update.message.reply_text(f"✅ User {user_id} has been unbanned in chat {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Unban failed: {e}")


# -------------------------------
# 🔇 /mute <chat_id> <user_id>
# -------------------------------
@safe_handler
async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /mute <chat_id> <user_id>")
        return

    chat_id = int(context.args[0])
    user_id = int(context.args[1])

    try:
        # Disable all permissions (mute completely)
        perms = ChatPermissions(can_send_messages=False)
        await context.bot.restrict_chat_member(chat_id, user_id, permissions=perms)
        await update.message.reply_text(f"🔇 User {user_id} muted in chat {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Mute failed: {e}")


# -------------------------------
# 🔊 /unmute <chat_id> <user_id>
# -------------------------------
@safe_handler
async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /unmute <chat_id> <user_id>")
        return

    chat_id = int(context.args[0])
    user_id = int(context.args[1])

    try:
        # Restore default permissions (can send messages again)
        perms = ChatPermissions(can_send_messages=True)
        await context.bot.restrict_chat_member(chat_id, user_id, permissions=perms)
        await update.message.reply_text(f"🔊 User {user_id} unmuted in chat {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Unmute failed: {e}")
# =========================================ZOMBIE ==============================================
@safe_handler
async def zombie_cleaner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Scans and removes deleted accounts from a group."""
    chat = update.effective_chat
    user = update.effective_user

    # Must be used in a group
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("⚠️ This command works only in groups.")
        return

    # Check if user is admin
    try:
        member = await chat.get_member(user.id)
        if not (member.status in ["administrator", "creator"] or user.id in SUDO_USERS or user.id == BOT_OWNER_ID):
            await update.message.reply_text("🚫 You must be an admin to use this command.")
            return
    except Exception as e:
        await update.message.reply_text(f"❌ Couldn't verify your admin status.\n{e}")
        return

    # Send temporary status message
    status_msg = await update.message.reply_text("🧹 Scanning group for deleted accounts...")

    deleted_users = []
    total_members = 0

    try:
        async for member in context.bot.get_chat_administrators(chat.id):
            pass  # Just to preload permissions if needed

        async for member in context.bot.get_chat_members(chat.id):
            total_members += 1
            if member.user.is_deleted:
                deleted_users.append(member.user)
    except Exception as e:
        await status_msg.edit_text(f"⚠️ Failed to fetch members. Probably due to privacy limits.\nError: {e}")
        return

    if not deleted_users:
        await status_msg.edit_text("✨ No deleted accounts found in this group!")
        return

    # If "clean" keyword given, remove them
    if context.args and context.args[0].lower() == "clean":
        removed = 0
        for user in deleted_users:
            try:
                await context.bot.ban_chat_member(chat.id, user.id)
                await context.bot.unban_chat_member(chat.id, user.id)
                removed += 1
            except (BadRequest, Forbidden):
                continue
            except Exception as e:
                print(f"[ZombieClean Error] {e}")
                continue

        await status_msg.edit_text(
            f"✅ Removed {removed} deleted accounts out of {len(deleted_users)} found.\n"
            f"Total group members scanned: {total_members}"
        )
    else:
        await status_msg.edit_text(
            f"💀 Found {len(deleted_users)} deleted accounts.\n"
            f"Use `/zombie clean` to remove them."
        )
#=====================PROMOTE =====================
@safe_handler
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Promote a user to admin in a group — Owner/Sudo only."""
    chat = update.effective_chat
    user_id = update.effective_user.id

    # Ensure command runs only in groups
    if chat.type == "private":
        await update.message.reply_text("❌ This command can only be used in groups.")
        return

    # Check if the user is owner/sudo
    if user_id != bot_data["owner"] and user_id not in bot_data["sudo_users"]:
        await update.message.reply_text("❌ Only owner/sudo can use this command.")
        return

    # Check if message is a reply
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user’s message to promote them.")
        return

    target = update.message.reply_to_message.from_user
    target_user_id = target.id
    target_name = target.first_name

    try:
        await context.bot.promote_chat_member(
            chat_id=chat.id,
            user_id=target_user_id,
            can_manage_chat=True,
            can_change_info=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=True,
            is_anonymous=False
        )

        await update.message.reply_text(
            f"✅ Promoted [{target_name}](tg://user?id={target_user_id}) to admin!",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Promotion failed:\n`{e}`", parse_mode="Markdown")
# ==================== SEND REACTION ==========================
async def send_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a reaction to a message in a group via bot DM"""
    if not context.args or len(context.args) < 3:
        await update.message.reply_text("Usage: /sendreaction <group_id> <message_id> <emoji>")
        return

    try:
        group_id = int(context.args[0])
        message_id = int(context.args[1])
        emoji = context.args[2]

        await context.bot.set_message_reaction(
            chat_id=group_id,
            message_id=message_id,
            reaction=[ReactionTypeEmoji(emoji=emoji)],
            is_big=False
        )

        await update.message.reply_text(f"✅ Reaction {emoji} sent to message {message_id} in group {group_id}")

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send reaction:\n{e}")

#===================== PIN FORWARD=====================
@safe_handler
async def forwardpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward and pin a replied message in all groups (owner/sudo only)."""
    user_id = update.effective_user.id
    if user_id != bot_data["owner"] and user_id not in bot_data["sudo_users"]:
        await update.message.reply_text("❌ Only owner/sudo can use this command.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("📌 Reply to a message you want to forward and pin.")
        return

    msg = update.message.reply_to_message
    forwarded = 0
    failed = 0

    for gid in bot_data["groups"]:
        try:
            fwd = await context.bot.forward_message(
                chat_id=int(gid),
                from_chat_id=msg.chat_id,
                message_id=msg.message_id
            )
            try:
                await fwd.pin(disable_notification=True)
            except Exception as e:
                print(f"[WARN] Couldn't pin in {gid}: {e}")
            forwarded += 1
            await asyncio.sleep(0.3)  # prevent flood limit
        except Exception as e:
            print(f"[WARN] Failed in {gid}: {e}")
            failed += 1

    await update.message.reply_text(
        f"📢 Forwarded & pinned in {forwarded} groups ✅\n❌ Failed in {failed} groups."
    )

#===================== FORWARD ALL =================
@safe_handler
async def forwardall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward a message to all groups (owner/sudo only)."""
    user_id = update.effective_user.id
    if user_id != bot_data["owner"] and user_id not in bot_data["sudo_users"]:
        await update.message.reply_text("❌ Only owner/sudo can use this command.")
        return

    # Must be used as a reply
    if not update.message.reply_to_message:
        await update.message.reply_text("🔁 Reply to a message you want to forward to all groups.")
        return

    msg = update.message.reply_to_message
    sent = 0
    failed = 0

    for gid in bot_data["groups"]:
        try:
            await context.bot.forward_message(chat_id=int(gid),
                                              from_chat_id=msg.chat_id,
                                              message_id=msg.message_id)
            sent += 1
            await asyncio.sleep(0.3)  # Avoid flood limit
        except Exception as e:
            print(f"[WARN] Failed to forward in {gid}: {e}")
            failed += 1

    await update.message.reply_text(f"📢 Forwarded to {sent} groups ✅\n❌ Failed: {failed}")
# ======================= PIN TO ==========================
@safe_handler
async def pinto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pin a message (sudo/owner can pin remotely too)."""
    msg = update.message
    bot_data = load_bot_data()
    owner = bot_data.get("owner")
    sudo_users = bot_data.get("sudo_users", [])

    user_id = msg.from_user.id

    # ---------------------- LOCAL PIN (REPLY) ----------------------
    if msg.reply_to_message:
        # Allow owner/sudo anywhere, group admins in groups
        if user_id != owner and user_id not in sudo_users:
            if msg.chat.type != "supergroup":
                await msg.reply_text("❌ Only sudo/owner can use this in private chats.")
                return
            # Check if user is admin
            member = await context.bot.get_chat_member(msg.chat_id, user_id)
            if member.status not in ["administrator", "creator"]:
                await msg.reply_text("❌ Only admins can pin messages in this group.")
                return

        try:
            await context.bot.pin_chat_message(
                chat_id=msg.chat_id,
                message_id=msg.reply_to_message.message_id,
                disable_notification=True,  # Silent pin
            )
            await msg.reply_text("📌 Message pinned successfully!")
        except Exception as e:
            await msg.reply_text(f"❌ Failed to pin message:\n`{e}`", parse_mode="Markdown")

    # ---------------------- REMOTE PIN (DM) ----------------------
    else:
        # Only owner/sudo can pin remotely
        if user_id != owner and user_id not in sudo_users:
            await msg.reply_text("❌ Only owner or sudo users can pin remotely.")
            return

        if len(context.args) < 2:
            await msg.reply_text(
                "Usage:\n`/pinto <chat_id> <message_id>`",
                parse_mode="Markdown",
            )
            return

        chat_id = int(context.args[0])
        message_id = int(context.args[1])

        try:
            await context.bot.pin_chat_message(
                chat_id=chat_id,
                message_id=message_id,
                disable_notification=True,
            )
            await msg.reply_text("📌 Message pinned successfully in remote chat!")
        except Exception as e:
            await msg.reply_text(f"❌ Failed to pin remotely:\n`{e}`", parse_mode="Markdown")
#========================CHAT MODE ======================
@safe_handler
async def chatmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable chat relay mode with a specific user."""
    user_id = update.effective_user.id

    # Only owner/sudo can use chatmode
    if user_id != bot_data["owner"] and user_id not in bot_data["sudo_users"]:
        await update.message.reply_text("❌ Only owner/sudo can use this command.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: /chatmode <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except:
        await update.message.reply_text("⚠️ Invalid user ID format.")
        return

    chat_mode_sessions[user_id] = target_id
    await update.message.reply_text(f"✅ Chat mode activated with user `{target_id}`.\nUse /stopchatmode to end.", parse_mode="Markdown")
    try:
        await context.bot.send_message(target_id, "💬 The bot owner started chat mode with you.")
    except:
        pass
#======================STOP CHATMODE ===========================
@safe_handler
async def stopchatmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Disable chat relay mode."""
    user_id = update.effective_user.id
    if user_id not in chat_mode_sessions:
        await update.message.reply_text("⚠️ You are not in chat mode.")
        return

    target_id = chat_mode_sessions.pop(user_id)
    await update.message.reply_text(f"❌ Chat mode with `{target_id}` stopped.", parse_mode="Markdown")
    try:
        await context.bot.send_message(target_id, "🛑 The bot owner has stopped chat.")
    except:
        pass
#=====================PINALL======================
@safe_handler
async def pinall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner/Sudo-only: Pin any type of message (text, media, poll, etc.) in all groups."""
    user_id = update.effective_user.id

    # Check permission
    if user_id != bot_data["owner"] and user_id not in bot_data["sudo_users"]:
        await update.message.reply_text("❌ Only owner/sudo can use this command.")
        return

    # Must reply to a message
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message to pin it in all groups.")
        return

    msg_to_pin = update.message.reply_to_message
    pinned = 0

    for gid in bot_data["groups"]:
        try:
            # If the message has text
            if msg_to_pin.text or msg_to_pin.caption:
                sent_msg = await context.bot.send_message(
                    chat_id=int(gid),
                    text=msg_to_pin.text or msg_to_pin.caption
                )

            # If the message contains a photo
            elif msg_to_pin.photo:
                sent_msg = await context.bot.send_photo(
                    chat_id=int(gid),
                    photo=msg_to_pin.photo[-1].file_id,
                    caption=msg_to_pin.caption or ""
                )

            # If the message contains a video
            elif msg_to_pin.video:
                sent_msg = await context.bot.send_video(
                    chat_id=int(gid),
                    video=msg_to_pin.video.file_id,
                    caption=msg_to_pin.caption or ""
                )

            # If the message contains a document
            elif msg_to_pin.document:
                sent_msg = await context.bot.send_document(
                    chat_id=int(gid),
                    document=msg_to_pin.document.file_id,
                    caption=msg_to_pin.caption or ""
                )

            # If the message contains a voice or audio
            elif msg_to_pin.voice or msg_to_pin.audio:
                sent_msg = await context.bot.send_audio(
                    chat_id=int(gid),
                    audio=(msg_to_pin.voice or msg_to_pin.audio).file_id,
                    caption=msg_to_pin.caption or ""
                )

            # If the message contains a poll
            elif msg_to_pin.poll:
                sent_msg = await context.bot.send_poll(
                    chat_id=int(gid),
                    question=msg_to_pin.poll.question,
                    options=[opt.text for opt in msg_to_pin.poll.options],
                    is_anonymous=msg_to_pin.poll.is_anonymous,
                    allows_multiple_answers=msg_to_pin.poll.allows_multiple_answers
                )

            else:
                print(f"[WARN] Unsupported message type in chat {gid}")
                continue

            # Pin the sent message
            await sent_msg.pin(disable_notification=True)
            pinned += 1

        except Exception as e:
            print(f"[WARN] Failed to pin in {gid}: {e}")

    await update.message.reply_text(f"📌 Pinned message in {pinned} groups ✅")
# ================== USER DATA ==========================
@safe_handler
async def userdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View or delete stored user data (owner/sudo only)."""
    msg = update.message or update.callback_query.message
    query = update.callback_query
    owner = bot_data.get("owner")
    sudo_users = bot_data.get("sudo_users", [])
    user = update.effective_user

    # Restrict access
    if user.id != OWNER_ID and user.id not in SUDO_USERS:
        if query:
            await query.answer("❌ You’re not authorized.", show_alert=True)
        else:
            await msg.reply_text("❌ Only owner or sudo users can use this command.")
        return

    # --- Handle Callback Actions ---
    if query:
        data = query.data.split(":")
        if data[0] == "delete_user":
            user_id = data[1]
            deleted_any = False

            for key in list(bot_data.keys()):
                if isinstance(bot_data[key], dict) and user_id in bot_data[key]:
                    del bot_data[key][user_id]
                    deleted_any = True

            if deleted_any:
                save_bot_data(bot_data)
                await query.edit_message_text(
                    f"🗑 Data for user `{user_id}` deleted successfully.",
                    parse_mode="Markdown",
                )
            else:
                await query.edit_message_text(
                    f"ℹ️ No data found for user `{user_id}`.",
                    parse_mode="Markdown",
                )
            return

        elif data[0] == "back_userdata":
            try:
                await query.message.delete()
            except:
                pass
            await query.message.reply_text("❌ User data deletion aborted.")
            return

    # --- Normal command execution ---
    if not context.args:
        await msg.reply_text("Usage:\n`/userdata <user_id>`", parse_mode="Markdown")
        return

    user_id = str(context.args[0])
    user_info = {}

    # Search for user data
    for key, value in bot_data.items():
        if isinstance(value, dict) and user_id in value:
            user_info[key] = value[user_id]

    if not user_info:
        await msg.reply_text(f"ℹ️ No stored data found for user `{user_id}`.", parse_mode="Markdown")
        return

    pretty_data = json.dumps(user_info, indent=2)
    if len(pretty_data) > 3500:
        pretty_data = pretty_data[:3500] + "\n… (truncated)"

    # Inline keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🗑 Delete Data", callback_data=f"delete_user:{user_id}"),
            InlineKeyboardButton("⬅ Back", callback_data="back_userdata")
        ]
    ])

    await msg.reply_text(
        f"📊 *User Data for `{user_id}`:*\n```\n{pretty_data}\n```",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
# =================== EDIT DELETE  ==============================   
# ==============================
# /editdelete TOGGLE
# ==============================
@safe_handler
async def toggle_edit_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle automatic edit deletion in a group (admins + owner/sudo only)."""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    owner = bot_data.get("owner")
    sudo_users = bot_data.get("sudo_users", [])
    config = bot_data.setdefault("edit_delete", {})

    # Permission check
    can_toggle = False
    if user.id == OWNER_ID or user.id in SUDO_USERS:
        can_toggle = True
    else:
        try:
            member = await chat.get_member(user.id)
            if member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                can_toggle = True
        except Exception as e:
            print(f"[EditDelete] Failed to fetch member info: {e}")

    if not can_toggle:
        await msg.reply_text("❌ Only group admins, sudo users, or the bot owner can toggle this feature.")
        return

    # Toggle feature
    if len(context.args) == 0:
        status = config.get(str(chat.id), False)
        await msg.reply_text(f"🛠 Edit delete is currently {'✅ ON' if status else '❌ OFF'}.")
        return

    state = context.args[0].lower()
    if state in ["on", "enable", "true"]:
        config[str(chat.id)] = True
        save_bot_data(bot_data)
        await msg.reply_text("✅ Edit delete feature enabled for this group.")
    elif state in ["off", "disable", "false"]:
        config[str(chat.id)] = False
        save_bot_data(bot_data)
        await msg.reply_text("❌ Edit delete feature disabled for this group.")
    else:
        await msg.reply_text("Usage: `/editdelete on` or `/editdelete off`", parse_mode="Markdown")
# =================== EDIT DELETE HANDLER =================
# ==============================
# HANDLE EDITED MESSAGES
# ==============================
@safe_handler
async def delete_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detect and handle edited messages — warn admins, delete users’ edits."""
    edited = update.edited_message
    if not edited:
        return

    owner = bot_data.get("owner")
    sudo_users = bot_data.get("sudo_users", [])
    config = bot_data.get("edit_delete", {})

    # Feature toggle
    if not config.get(str(edited.chat_id), False):
        return

    user = edited.from_user
    chat = edited.chat

    # Skip bot users
    if user.is_bot:
        return

    # Owner/sudo exemption
    if user.id == OWNER_ID or user.id in SUDO_USERS:
        return

    try:
        member = await chat.get_member(user.id)
        status = member.status

        # If admin/owner → only warn and delete the warning
        if status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            warn = await edited.reply_text(
                f"⚠️ {user.mention_html()}, please avoid editing messages — this is monitored.",
                parse_mode="HTML"
            )
            await asyncio.sleep(8)
            try:
                await context.bot.delete_message(chat_id=warn.chat_id, message_id=warn.message_id)
            except Exception:
                pass
            return

        # For normal users → warn + delete edited message after 30s
        warn_msg = await edited.reply_text(
            f"⚠️ {user.mention_html()} edited their message.\n"
            "This message will be deleted in 30 seconds.",
            parse_mode="HTML"
        )

        await asyncio.sleep(30)

        # Delete edited message
        try:
            await context.bot.delete_message(chat_id=edited.chat_id, message_id=edited.message_id)
        except Exception:
            pass

        # Delete warning
        try:
            await context.bot.delete_message(chat_id=warn_msg.chat_id, message_id=warn_msg.message_id)
        except Exception:
            pass

    except Exception as e:
        print(f"[EditDelete Error] {e}")
# =================== UPDATE DATA ==================
@safe_handler
async def updatedata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check all stored users and groups, remove those that blocked the bot or are invalid."""
    msg = update.effective_message
    user = update.effective_user

    bot_data = load_bot_data()
    owner = bot_data.get("owner")
    sudo_users = bot_data.get("sudo_users", [])

    if user.id != owner and user.id not in sudo_users:
        await msg.reply_text("❌ Only owner or sudo users can use this command.")
        return

    users = bot_data.get("users", {})
    groups = bot_data.get("groups", [])

    removed_users = []
    removed_groups = []

    await msg.reply_text("🔍 Checking all users and groups, please wait...")

    # --- Check users ---
    for user_id in list(users.keys()):
        try:
            await context.bot.send_chat_action(chat_id=int(user_id), action="typing")
            await asyncio.sleep(0.2)
        except (Forbidden, BadRequest, TimedOut) as e:
            if any(
                key in str(e)
                for key in [
                    "bot was blocked",
                    "user is deactivated",
                    "Chat not found",
                    "chat not found",
                ]
            ):
                removed_users.append(user_id)
                del users[user_id]
                print(f"[User Removed] {user_id} - {e}")

    # --- Check groups ---
    for group_id in list(groups):
        try:
            await context.bot.get_chat(chat_id=int(group_id))
            await asyncio.sleep(0.2)
        except (Forbidden, BadRequest, TimedOut) as e:
            if any(
                key in str(e)
                for key in [
                    "Chat not found",
                    "bot was kicked",
                    "bot is not a member",
                    "chat not found",
                ]
            ):
                removed_groups.append(group_id)
                groups.remove(group_id)
                print(f"[Group Removed] {group_id} - {e}")

    # --- Save updated data ---
    bot_data["users"] = users
    bot_data["groups"] = groups
    save_bot_data(bot_data)

    # --- Summary message ---
    report = (
        f"✅ **Data Update Complete**\n\n"
        f"👤 Users removed: `{len(removed_users)}`\n"
        f"👥 Groups removed: `{len(removed_groups)}`\n\n"
        f"🧾 Total users left: `{len(users)}`\n"
        f"🏠 Total groups left: `{len(groups)}`"
    )

    await msg.reply_text(report, parse_mode="Markdown")

# =================== SEND MESSAGE ==============
@safe_handler
async def sendto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Owner/Sudo command to send any message or media to a specific user or group.
    Usage:
    Reply to a message → /sendto <user_id/group_id>
    Or use directly → /sendto <user_id/group_id> <text>
    """
    user_id = update.effective_user.id
    if user_id != bot_data["owner"] and user_id not in bot_data["sudo_users"]:
        await update.message.reply_text("❌ Only owner/sudo can use this command")
        return

    if len(context.args) < 1:
        await update.message.reply_text("❌ Usage:\nReply to a message with /sendto <user_id/group_id>\nOr use /sendto <user_id/group_id> <text>")
        return

    target_id = int(context.args[0])
    msg = update.message

    try:
        # If the command is a reply — resend that message
        if msg.reply_to_message:
            rmsg = msg.reply_to_message

            if rmsg.text:
                await context.bot.send_message(target_id, rmsg.text)

            elif rmsg.photo:
                await context.bot.send_photo(
                    target_id,
                    photo=rmsg.photo[-1].file_id,
                    caption=rmsg.caption or ""
                )

            elif rmsg.video:
                await context.bot.send_video(
                    target_id,
                    video=rmsg.video.file_id,
                    caption=rmsg.caption or ""
                )

            elif rmsg.document:
                await context.bot.send_document(
                    target_id,
                    document=rmsg.document.file_id,
                    caption=rmsg.caption or ""
                )

            elif rmsg.audio:
                await context.bot.send_audio(
                    target_id,
                    audio=rmsg.audio.file_id,
                    caption=rmsg.caption or ""
                )

            elif rmsg.voice:
                await context.bot.send_voice(
                    target_id,
                    voice=rmsg.voice.file_id,
                    caption=rmsg.caption or ""
                )

            elif rmsg.sticker:
                await context.bot.send_sticker(
                    target_id,
                    sticker=rmsg.sticker.file_id
                )

            elif rmsg.poll:
                await context.bot.send_poll(
                    target_id,
                    question=rmsg.poll.question,
                    options=[o.text for o in rmsg.poll.options],
                    is_anonymous=rmsg.poll.is_anonymous
                )

            else:
                await msg.reply_text("⚠️ Unsupported media type for forwarding.")

        else:
            # No reply — just send text
            if len(context.args) < 2:
                await msg.reply_text("❌ Provide message text or reply to one.")
                return
            text = " ".join(context.args[1:])
            await context.bot.send_message(target_id, text)

        await msg.reply_text(f"✅ Message sent successfully to `{target_id}`", parse_mode="Markdown")

    except Exception as e:
        await msg.reply_text(f"❌ Failed to send message: `{e}`", parse_mode="Markdown")

# ================== BOT STATS ==================
@safe_handler
async def botstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    total_groups = len(bot_data["groups"])
    total_users = len(bot_data["users"])
    await update.message.reply_text(
        f"🤖 Bot Stats:\nGroups: {total_groups}\nUsers: {total_users}\nOwner:@AyuElite\nSudo: {', '.join(map(str, SUDO_USERS))}"
    )

# ================== PING ==================
@safe_handler
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = time.time() - START_TIME
    hrs, rem = divmod(int(uptime), 3600)
    mins, secs = divmod(rem, 60)
    await update.message.reply_text(f"🤖 𝔹𝕠𝕥 𝕌𝕡𝕥𝕚𝕞𝕖: {hrs}h {mins}m {secs}s")

# ================== PURGE =====================================
@safe_handler
async def purge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Purges messages either from group (by reply) or remotely from DM."""
    user = update.effective_user
    chat = update.effective_chat

    # ======= CASE 1: RUN FROM BOT DM =======
    if chat.type == "private":
        if len(context.args) < 2:
            await update.message.reply_text("🧹 Usage: /purge <group_id> <start_msg_id> [end_msg_id]")
            return

        try:
            group_id = int(context.args[0])
            start_id = int(context.args[1])
            end_id = int(context.args[2]) if len(context.args) > 2 else start_id
        except ValueError:
            await update.message.reply_text("⚠️ Invalid format. IDs must be numbers.")
            return

        if end_id < start_id:
            start_id, end_id = end_id, start_id

        deleted_count, failed = 0, 0
        await update.message.reply_text(
            f"🧹 Purging messages in <code>{group_id}</code>...\n"
            f"From <code>{start_id}</code> to <code>{end_id}</code>",
            parse_mode="HTML"
        )

        for msg_id in range(start_id, end_id + 1):
            try:
                await context.bot.delete_message(group_id, msg_id)
                deleted_count += 1
            except (Forbidden, BadRequest):
                failed += 1
                continue

        await update.message.reply_text(
            f"✅ Purge complete!\n🗑 Deleted: <b>{deleted_count}</b>\n⚠️ Failed: <b>{failed}</b>",
            parse_mode="HTML"
        )
        return

    # ======= CASE 2: RUN INSIDE GROUP =======
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a message to start purge.")
        return

    start_id = update.message.reply_to_message.message_id
    end_id = int(context.args[0]) if context.args else update.message.message_id

    if end_id < start_id:
        start_id, end_id = end_id, start_id

    deleted_count, failed = 0, 0

    # delete the trigger message first
    try:
        await context.bot.delete_message(chat.id, update.message.message_id)
    except Exception:
        pass

    for msg_id in range(start_id, end_id + 1):
        try:
            await context.bot.delete_message(chat.id, msg_id)
            deleted_count += 1
        except (Forbidden, BadRequest):
            failed += 1
            continue

    await context.bot.send_message(
        chat_id=chat.id,
        text=f"✅ Purge done.\n🗑 Deleted: <b>{deleted_count}</b>\n⚠️ Failed: <b>{failed}</b>",
        parse_mode="HTML"
    )
# ================== CHAT MODE RELAY HANDLER ==================
@safe_handler
async def chatmode_relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Relays messages between controller and target during chat mode."""
    user_id = str(update.effective_user.id)
    msg = update.message
    relayed = False  # <-- New flag

    # Loop through active sessions
    for controller_id, target_id in chat_mode_sessions.items():
        # Controller sends → forward to target
        if user_id == str(controller_id):
            try:
                if msg.text:
                    await context.bot.send_message(target_id, msg.text)
                elif msg.photo:
                    await context.bot.send_photo(target_id, photo=msg.photo[-1].file_id, caption=msg.caption or "")
                elif msg.document:
                    await context.bot.send_document(target_id, document=msg.document.file_id, caption=msg.caption or "")
                elif msg.video:
                    await context.bot.send_video(target_id, video=msg.video.file_id, caption=msg.caption or "")
                elif msg.voice:
                    await context.bot.send_voice(target_id, voice=msg.voice.file_id, caption=msg.caption or "")
                elif msg.sticker:
                    await context.bot.send_sticker(target_id, sticker=msg.sticker.file_id)
                relayed = True
            except Exception as e:
                print(f"[ChatMode Error - controller→target] {e}")
            break  # stop loop but not the function

        # Target replies → forward to controller
        elif user_id == str(target_id):
            try:
                if msg.text:
                    await context.bot.send_message(controller_id, f"👤 {update.effective_user.first_name}: {msg.text}")
                elif msg.photo:
                    await context.bot.send_photo(controller_id, photo=msg.photo[-1].file_id, caption=msg.caption or "")
                elif msg.document:
                    await context.bot.send_document(controller_id, document=msg.document.file_id, caption=msg.caption or "")
                elif msg.video:
                    await context.bot.send_video(controller_id, video=msg.video.file_id, caption=msg.caption or "")
                elif msg.voice:
                    await context.bot.send_voice(controller_id, voice=msg.voice.file_id, caption=msg.caption or "")
                elif msg.sticker:
                    await context.bot.send_sticker(controller_id, sticker=msg.sticker.file_id)
                relayed = True
            except Exception as e:
                print(f"[ChatMode Error - target→controller] {e}")
            break  # stop loop but not the function

    # ⬇️ IMPORTANT: if not in chatmode, allow normal handlers to run
    if not relayed:
        # Pass message to other handlers
        return await handle_message(update, context)
# ================== MESSAGE HANDLER ==================
@safe_handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = str(update.effective_chat.id)
    user = update.effective_user
    user_id = str(user.id)

    # Track groups and users
    if chat_id not in bot_data["groups"]:
        bot_data["groups"].append(chat_id)
    if user_id not in bot_data["users"]:
        bot_data["users"][user_id] = user.full_name
    save_bot()

    # Remove AFK if user sends message
    if chat_id in afk_data and user_id in afk_data[chat_id]:
        afk_info = afk_data[chat_id][user_id]
        duration = int(time.time() - float( afk_info["since"]))
        hrs, rem = divmod(duration, 3600)
        mins, secs = divmod(rem, 60)
        dur_text = f"{hrs}h {mins}m {secs}s" if hrs > 0 else f"{mins}m {secs}s"
        await update.message.reply_text(
            f"✅ Welcome back {user.mention_html()}!\nYou were AFK for {dur_text}\nMessages while away: {afk_info['count']}\nReason: {afk_info['reason']}",
            parse_mode="HTML"
        )
        del afk_data[chat_id][user_id]
        save_afk()
        return

    # Check mentions/replies
    await check_afk_mentions(update, context)

# ================== MENTION ALERT ==================
async def check_afk_mentions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if chat_id not in afk_data:
        return

    entities = update.message.entities or []
    mentioned_ids = set()
    for ent in entities:
        if ent.type in ["mention", "text_mention"] and ent.user:
            mentioned_ids.add(str(ent.user.id))
    if update.message.reply_to_message:
        mentioned_ids.add(str(update.message.reply_to_message.from_user.id))

    for uid in mentioned_ids:
        if uid in afk_data[chat_id]:
            afk_info = afk_data[chat_id][uid]
            duration = int(time.time() - float(afk_info["since"]))
            hrs, rem = divmod(duration, 3600)
            mins, secs = divmod(rem, 60)
            dur_text = f"{hrs}h {mins}m {secs}s" if hrs > 0 else f"{mins}m {secs}s"
            user = await context.bot.get_chat(uid)
            await update.message.reply_text(
                f"⚠️ {user.mention_html()} is AFK!\nReason: {afk_info['reason']}\nSince: {dur_text} ago",
                parse_mode="HTML"
            )
            afk_data[chat_id][uid]["count"] += 1
            save_afk()

# ================== BROADCAST ==================
@safe_handler
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != bot_data["owner"] and user_id not in sudo_users:
        await update.message.reply_text("❌ Only owner/sudo can use this command")
        return

    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text("Usage: /broadcast [all|groups|users] <message or reply to content>")
        return

    # Target: all / groups / users
    if context.args:
        target = context.args[0].lower()
        msg_text = " ".join(context.args[1:]) if len(context.args) > 1 else None
    else:
        target = "all"
        msg_text = None

    if target not in ["all", "groups", "users"]:
        await update.message.reply_text("❌ Invalid target! Use all / groups / users")
        return

    # Determine broadcast content
    reply = update.message.reply_to_message
    groups_sent = users_sent = 0

    async def send_broadcast(chat_id):
        nonlocal groups_sent, users_sent
        try:
            if reply:
                if reply.photo:
                    await context.bot.send_photo(chat_id, photo=reply.photo[-1].file_id, caption=reply.caption or msg_text)
                elif reply.video:
                    await context.bot.send_video(chat_id, video=reply.video.file_id, caption=reply.caption or msg_text)
                elif reply.document:
                    await context.bot.send_document(chat_id, document=reply.document.file_id, caption=reply.caption or msg_text)
                elif reply.audio:
                    await context.bot.send_audio(chat_id, audio=reply.audio.file_id, caption=reply.caption or msg_text)
                elif reply.voice:
                    await context.bot.send_voice(chat_id, voice=reply.voice.file_id, caption=reply.caption or msg_text)
                elif reply.poll:
                    await context.bot.send_poll(chat_id, question=reply.poll.question, options=[o.text for o in reply.poll.options])
                else:
                    await context.bot.send_message(chat_id, msg_text or reply.text or "📢 Broadcast message")
            else:
                await context.bot.send_message(chat_id, msg_text or "📢 Broadcast message")
            if str(chat_id).startswith("-"):  # group id
                groups_sent += 1
            else:
                users_sent += 1
        except Exception as e:
            print(f"[Broadcast Error] {chat_id}: {e}")

    # Send to all or selected targets
    if target in ["all", "groups"]:
        for gid in bot_data["groups"]:
            await send_broadcast(int(gid))

    if target in ["all", "users"]:
        for uid in bot_data["users"]:
            await send_broadcast(int(uid))

    await update.message.reply_text(
        f"✅ Broadcast sent successfully!\nGroups: {groups_sent}\nUsers: {users_sent}"
    )


# ================== GROUP JOIN ==================
@safe_handler
async def new_group_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.my_chat_member.chat.id
    BOT_MSG = f"🤖 Hello! I'm Shadow AFK bot,most advanced AFK bot on telegram. Use /afk to set AFK status.\nCurrent uptime: {int(time.time()-START_TIME)}s"
    await context.bot.send_message(chat_id, BOT_MSG)

# ================== MAIN ==================
if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("afk", afk))
    app.add_handler(CommandHandler("afklist", afklist))
    app.add_handler(CommandHandler("botstats", botstats))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("pinall",pinall))
    app.add_handler(CommandHandler("addsudo",addsudo))
    app.add_handler(CommandHandler("sendto",sendto))
    app.add_handler(CommandHandler("promote",promote))
    app.add_handler(CommandHandler("forwardall",forwardall))
    app.add_handler(CommandHandler("forwardpin",forwardpin))
    app.add_handler(CommandHandler("replygroup",replygroup))
    app.add_handler(CommandHandler("replymention",replymention))
    app.add_handler(CommandHandler("chatmode",chatmode))
    app.add_handler(CommandHandler("stopchatmode",stopchatmode))
    app.add_handler(CommandHandler("delete",delete))
    app.add_handler(CommandHandler("ban", cmd_ban))
    app.add_handler(CommandHandler("unban", cmd_unban))
    app.add_handler(CommandHandler("mute", cmd_mute))
    app.add_handler(CommandHandler("unmute", cmd_unmute))
    app.add_handler(CommandHandler("accept", accept_request))
    app.add_handler(CommandHandler("zombie", zombie_cleaner))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("purge", purge_command))
    app.add_handler(CommandHandler("complaint", complaint_command))
    app.add_handler(CommandHandler("feedback", feedback_command))
    app.add_handler(CommandHandler("showcomplaints", show_complaints_command))
    app.add_handler(CommandHandler("sendreaction", send_reaction))
    app.add_handler(CommandHandler("updatedata", updatedata))
    app.add_handler(CommandHandler("pinto",pinto))
# ─── Register handlers ─────────────────────────────────────

    app.add_handler(CommandHandler("whisper", whisper_command))
    app.add_handler(CallbackQueryHandler(whisper_button_handler, pattern="^whisper_"))	# ─── /whisper command ──────────────────────────────────────
    app.add_handler(CommandHandler("userdata", userdata))
    app.add_handler(CallbackQueryHandler(userdata, pattern="^(delete_user|back_userdata):"))
    app.add_handler(CommandHandler("editdelete", toggle_edit_delete))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, delete_edited_message))

# Messages
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, chatmode_relay))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    # Group join
    app.add_handler(ChatMemberHandler(new_group_welcome, ChatMemberHandler.MY_CHAT_MEMBER))

    print("Warrior AFK is running...")
    app.run_polling()

