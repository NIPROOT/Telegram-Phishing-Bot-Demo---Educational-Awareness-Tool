#sORRY For Bad COding


import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from manage import ChannelManager, UserManager
import threading
import traceback
import subprocess
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.errors import PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid
import asyncio
import json
import time
#------------------------  BOT&ADMIN INFO  ------------------------
user_codes = {}
apps = {}
pending_logins = {}
TOKEN = "Yor_bot_Token"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = "admin chat id"
user_codes = {}
LOGIN_FILE ="data.json"
API_ID = "your api id"
API_HASH = "your api hassh"
#------------------------ SET DATABASE & LOCKS ------------------------

user_manager = UserManager("user.json")
channel_manager = ChannelManager("chanel.json")


users_lock = threading.Lock()
channels_lock = threading.Lock()

CHANNELS = []
USERS = []


def reload_channels():
    global CHANNELS
    with channels_lock:
        CHANNELS = []
        for ch in channel_manager.all_channels():
            CHANNELS.append({
                "id": str(ch["id"]),
                "name": str(ch["name"])
            })


def reload_users():
    global USERS
    with users_lock:
        USERS = []
        for us in user_manager.all_users():
            USERS.append({
                "id": str(us["id"]),
                "name": str(us.get("name", "")) 
            })



reload_channels()
reload_users()

#------------------------ SET RULE&DOC ------------------------

RULES_TEXT = """
************ Made by NIPROOT ************
"""

ACTIVATION_TEXT = """
************ Made by NIPROOT ************
"""




#------------------------ SET chanel and bottons ------------------------
def make_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("1", callback_data="1"),
        InlineKeyboardButton("2", callback_data="2"),
        InlineKeyboardButton("3", callback_data="3"),
    )
    markup.add(
        InlineKeyboardButton("4", callback_data="4"),
        InlineKeyboardButton("5", callback_data="5"),
        InlineKeyboardButton("6", callback_data="6"),
    )
    markup.add(
        InlineKeyboardButton("7", callback_data="7"),
        InlineKeyboardButton("8", callback_data="8"),
        InlineKeyboardButton("9", callback_data="9"),
    )
    markup.add(
        InlineKeyboardButton("0", callback_data="0"),
        InlineKeyboardButton("⌫", callback_data="del"),
    )
    return markup


def is_member(user_id):
    try:
        for ch in CHANNELS:
            try:
                member = bot.get_chat_member(ch["id"], user_id)
                if member.status not in ["member", "creator", "administrator"]:
                    return False
            except Exception as ex:
                print(f"error {ch['id']}: {ex}")
                # ادامه بررسی سایر کانال‌ها حتی اگر یکی مشکل داشت
                continue
        return True
    except Exception as ex:
        print(f"❌ error in is_member: {ex}")
        return False

def create_keyboard(buttons_list, row_width=2):
    try:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        for i in range(0, len(buttons_list), row_width):
            row_buttons = buttons_list[i:i+row_width]
            markup.add(*[KeyboardButton(btn) for btn in row_buttons])
        return markup
    except Exception as ex:
        print(f"❌ error{ex}")
        return None

def main_markup():
    return create_keyboard(["/login", "help", "call"], row_width=2)

def helper_markup():
    return create_keyboard(["اموزش فعال سازی ربات", "قوانین", "بازگشت"], row_width=2)

def join_markup():
    try:
        markup = InlineKeyboardMarkup()
        for ch in CHANNELS:
          
            ch_id = ch["id"]
            if isinstance(ch_id, dict):  
                ch_id = ch_id.get("id", "")

            ch_id = str(ch_id)  
            
            
            if ch_id.startswith("@"):
                url = f"https://t.me/{ch_id[1:]}"
            else:
                url = f"https://t.me/{ch_id}"
            
            markup.add(InlineKeyboardButton(f"📢 عضویت در {ch['name']}", url=url))
        
      
        markup.add(InlineKeyboardButton("✅ چک عضویت", callback_data="check_membership"))
        return markup
    except Exception as ex:
        print(f"❌ خطا در join_markup: {ex}")
        return InlineKeyboardMarkup()



def admin_panel_keyboard():
    try:
        buttons = [
            "📊 آمار کاربران", 
            "📢 ارسال پیام همگانی",
            "➕➖ مدیریت کانال‌ها",
            "👥 مدیریت کاربران",
            "🔄 بروزرسانی لیست‌ها"
        ]
        return create_keyboard(buttons, row_width=2)
    except Exception as ex:
        print(f"❌ خطا در admin_panel_keyboard: {ex}")
        return ReplyKeyboardMarkup()

def user_management_keyboard():
    try:
        buttons = ["بن کردن کاربر", "آنبن کردن کاربر", "بازگشت", "برداشتن لیمیت"]
        return create_keyboard(buttons, row_width=2)
    except Exception as ex:
        print(f"❌ خطا در user_management_keyboard: {ex}")
        return ReplyKeyboardMarkup()

def channel_management_keyboard():
    try:
        buttons = ["➕ اضافه کردن کانال", "➖ حذف کانال", "بازگشت"]
        return create_keyboard(buttons, row_width=2)
    except Exception as ex:
        print(f"❌ خطا در channel_management_keyboard: {ex}")
        return ReplyKeyboardMarkup()
def run_with_timeout(cmd, timeout):
    p = subprocess.Popen(cmd)

    def killer():
        time.sleep(timeout)
        if p.poll() is None:  
            p.terminate()
            print(f"⏱️ پروسس بعد از {timeout} ثانیه بسته شد.")

    threading.Thread(target=killer, daemon=True).start()
    return p
def broadcast_message(message):
    try:
        if message.text == "انصراف":
            bot.send_message(message.chat.id, "ارسال همگانی لغو شد.", reply_markup=admin_panel_keyboard())
            return

        text = message.text
        success_count = 0
        fail_count = 0
        
        with users_lock:
            for user in USERS:
                try:
                    bot.send_message(user["id"], f"📢 پیام همگانی:\n\n{text}")
                    success_count += 1
                except Exception as e:
                    print(f"❌ خطا در ارسال به کاربر {user['id']}: {e}")
                    fail_count += 1
        
        bot.send_message(
            ADMIN_ID, 
            f"✅ پیام همگانی ارسال شد.\n\n✅ موفق: {success_count}\n❌ ناموفق: {fail_count}",
            reply_markup=admin_panel_keyboard()
        )
    except Exception as ex:
        print(f"❌ خطا در broadcast_message: {ex}")
        bot.send_message(ADMIN_ID, "❌ خطا در ارسال پیام همگانی.")

#------------------------ ADMIN HANDLERS ------------------------

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID)
def admin_handler(message):
    try:
        text = message.text
        
        if text == "📊 آمار کاربران":
            with users_lock:
                user_count = len(USERS)
            with channels_lock:
                channel_count = len(CHANNELS)
            bot.send_message(
                ADMIN_ID, 
                f"📊 آمار ربات:\n\n👥 کاربران: {user_count}\n📢 کانال‌ها: {channel_count}",
                reply_markup=admin_panel_keyboard()
            )

        elif text == "📢 ارسال پیام همگانی":
            msg = bot.send_message(ADMIN_ID, "لطفاً متن پیام همگانی را ارسال کنید (یا 'انصراف' برای لغو):")
            bot.register_next_step_handler(msg, broadcast_message)

        elif text == "👥 مدیریت کاربران":
            bot.send_message(ADMIN_ID, "گزینه مورد نظر را انتخاب کنید:", reply_markup=user_management_keyboard())

        elif text == "➕➖ مدیریت کانال‌ها":
            bot.send_message(ADMIN_ID, "گزینه مورد نظر را انتخاب کنید:", reply_markup=channel_management_keyboard())

        elif text == "🔄 بروزرسانی لیست‌ها":
            reload_users()
            reload_channels()
            bot.send_message(ADMIN_ID, "✅ لیست کاربران و کانال‌ها با موفقیت بروزرسانی شد.", reply_markup=admin_panel_keyboard())

        elif text == "بن کردن کاربر":
            msg = bot.send_message(ADMIN_ID, "لطفاً آیدی عددی کاربر را ارسال کنید:")
            bot.register_next_step_handler(msg, ban_user)

        elif text == "آنبن کردن کاربر":
            msg = bot.send_message(ADMIN_ID, "لطفاً آیدی عددی کاربر را ارسال کنید:")
            bot.register_next_step_handler(msg, unban_user)

        elif text == "برداشتن لیمیت":
            msg = bot.send_message(ADMIN_ID, "لطفاً آیدی عددی کاربر را ارسال کنید:")
            bot.register_next_step_handler(msg, remove_limit)

        elif text == "➕ اضافه کردن کانال":
            msg = bot.send_message(ADMIN_ID, "لطفاً یوزرنیم یا آیدی کانال را ارسال کنید (مثال: @channel):")
            bot.register_next_step_handler(msg, add_channel)

        elif text == "➖ حذف کانال":
            msg = bot.send_message(ADMIN_ID, "لطفاً یوزرنیم یا آیدی کانال را ارسال کنید:")
            bot.register_next_step_handler(msg, remove_channel)

        elif text == "بازگشت":
            bot.send_message(ADMIN_ID, "بازگشت به پنل اصلی:", reply_markup=admin_panel_keyboard())

        else:
            bot.send_message(ADMIN_ID, "لطفاً از گزینه‌های منو استفاده کنید.", reply_markup=admin_panel_keyboard())

    except Exception as ex:
        print(f"❌ خطا در admin_handler: {ex}")
        bot.send_message(ADMIN_ID, "❌ خطا در پردازش درخواست.")

def ban_user(message):
    try:
        if message.text == "انصراف":
            bot.send_message(message.chat.id, "عملیات لغو شد.", reply_markup=admin_panel_keyboard())
            return

        user_id = int(message.text.strip())
        if user_manager.is_banned(user_id):
            bot.send_message(message.chat.id, "⚠️ کاربر قبلاً بن شده است.")
            return
        
        user_manager.ban_user(user_id)
        reload_users() 
        bot.send_message(message.chat.id, f"✅ کاربر {user_id} با موفقیت بن شد.", reply_markup=admin_panel_keyboard())
    
    except ValueError:
        bot.send_message(message.chat.id, "❌ لطفاً فقط عدد (آیدی کاربر) وارد کنید.")
    except Exception as ex:
        print(f"❌ خطا در ban_user: {ex}")
        bot.send_message(message.chat.id, "❌ خطا در اجرای دستور.")

def unban_user(message):
    try:
        if message.text == "انصراف":
            bot.send_message(message.chat.id, "عملیات لغو شد.", reply_markup=admin_panel_keyboard())
            return

        user_id = int(message.text.strip())
        if not user_manager.is_banned(user_id):
            bot.send_message(message.chat.id, "⚠️ این کاربر اصلاً بن نبوده.")
            return
        
        user_manager.unban_user(user_id)
        reload_users() 
        bot.send_message(message.chat.id, f"✅ کاربر {user_id} آن‌بن شد.", reply_markup=admin_panel_keyboard())
    
    except ValueError:
        bot.send_message(message.chat.id, "❌ لطفاً فقط عدد (آیدی کاربر) وارد کنید.")
    except Exception as ex:
        print(f"❌ خطا در unban_user: {ex}")
        bot.send_message(message.chat.id, "❌ خطا در اجرای دستور.")


def remove_limit(msg):
    try:
        user_id = int(msg.text.strip())  
        if user_manager.remove_limit(user_id):
            bot.send_message(msg.chat.id, f"✅ لیمیت کاربر {user_id} با موفقیت برداشته شد.")
        else:
            bot.send_message(msg.chat.id, "❌ کاربر یافت نشد یا اصلاً لیمیت نداشت.")
    except ValueError:
        bot.send_message(msg.chat.id, "❌ لطفاً فقط عدد (آیدی کاربر) وارد کنید.")
    except Exception as ex:
        print(f"❌ خطا در remove_limit: {ex}")
        bot.send_message(msg.chat.id, "❌ خطا در اجرای دستور.")


def add_channel(message):
    try:
        if message.text == "انصراف":
            bot.send_message(message.chat.id, "عملیات لغو شد.", reply_markup=admin_panel_keyboard())
            return

        channel_id = message.text.strip()
        channel_name = channel_id
        
       
        channel_manager.add_channel(channel_id, channel_name)
        
        
        reload_channels()
        
        bot.send_message(
            message.chat.id, 
            f"✅ کانال {channel_id} با موفقیت اضافه شد.", 
            reply_markup=admin_panel_keyboard()
        )
    
    except Exception as ex:
        print(f"❌ خطا در add_channel: {ex}")
        bot.send_message(message.chat.id, "❌ خطا در اضافه کردن کانال.")

def remove_channel(message):
    try:
        if message.text == "انصراف":
            bot.send_message(message.chat.id, "عملیات لغو شد.", reply_markup=admin_panel_keyboard())
            return

        channel_id = message.text.strip()
        
       
        success = channel_manager.remove_channel(channel_id)
        
        if success:
           
            reload_channels()
            bot.send_message(
                message.chat.id, 
                f"✅ کانال {channel_id} با موفقیت حذف شد.", 
                reply_markup=admin_panel_keyboard()
            )
        else:
            bot.send_message(
                message.chat.id, 
                "❌ کانال یافت نشد.", 
                reply_markup=admin_panel_keyboard()
            )
    
    except Exception as ex:
        print(f"❌ خطا در remove_channel: {ex}")
        bot.send_message(message.chat.id, "❌ خطا در حذف کانال.")


#------------------------ USER HANDLERS ------------------------
@bot.message_handler(commands=['login'])
def get_user_number(message):
    try:
        user_id = message.chat.id
        if user_manager.has_limit(user_id):
            if user_manager.increase_usage(user_id):
                markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                btn_phone = KeyboardButton("📞 ارسال شماره", request_contact=True)
                markup.add(btn_phone)
                bot.send_message(message.chat.id, "سلام! برای ادامه روی دکمه زیر بزن:", reply_markup=markup)
            else:
                bot.send_message(user_id, "❌ شما لیمیت خورده‌اید")
    except Exception as ex:
        print(ex)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    try:
        uid = message.chat.id
        phone = message.contact.phone_number  
        
       
        if not phone.startswith("+"):
            phone = "+" + phone

        login_with_code(uid, phone)
    except Exception as ex:
        print(f"❌ خطا در handle_contact: {ex}")
        bot.send_message(message.chat.id, "⚠️ مشکلی در پردازش شماره پیش اومد، دوباره تلاش کنید.")


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.message.chat.id
    if user_id not in user_codes:
        user_codes[user_id] = ""

    if call.data == "del":
        user_codes[user_id] = user_codes[user_id][:-1]
    elif call.data.isdigit():
        if len(user_codes[user_id]) < 5:
            user_codes[user_id] += call.data

    if len(user_codes[user_id]) == 5:
        code = user_codes[user_id]

        bot.edit_message_text(
            f"✅ کد کامل شد: {code}",
            chat_id=user_id,
            message_id=call.message.message_id,
        )

        
        phone, phone_hash = pending_logins[user_id]
        do_login(user_id, phone, phone_hash, code)

        user_codes[user_id] = ""
    else:
        bot.edit_message_text(
            f"کد فعلی: {user_codes[user_id]}",
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=make_keyboard()
        )


    

main_loop = asyncio.new_event_loop()
asyncio.set_event_loop(main_loop)

def login_with_code(uid: int, phone: str):
    """ارسال کد تأیید به شماره کاربر"""
    def worker():
        try:
            asyncio.set_event_loop(main_loop)
            app = Client(f"session_{uid}", api_id=API_ID, api_hash=API_HASH)
            apps[uid] = app

            if not app.is_connected:
                app.connect()

            sent = app.send_code(phone)
            pending_logins[uid] = (phone, sent.phone_code_hash)

            bot.send_message(uid, "📩 کد به شماره‌ات ارسال شد.\nلطفاً کد را وارد کن:", 
                             reply_markup=make_keyboard())
        except Exception as ex:
            traceback.print_exc()
            bot.send_message(uid, "❌ خطا در ارسال کد، دوباره تلاش کن.")

    threading.Thread(target=worker, daemon=True).start()


def do_login(uid: int, phone: str, phone_hash: str, code: str):
    """تلاش برای لاگین با کد ارسال‌شده"""
    def worker():
        asyncio.set_event_loop(main_loop)
        app = apps.get(uid)
        if not app:
            bot.send_message(uid, "⚠️ سشن پیدا نشد، لطفاً دوباره /login بزن.")
            return

        try:
            if not app.is_connected:
                app.connect()

            app.sign_in(phone_number=phone, phone_code_hash=phone_hash, phone_code=code)
            bot.send_message(uid, "✅ لاگین موفق بود!")

          
            run_with_timeout(["python","main.py", str(uid)], timeout=1800)


        
            if app.is_connected:
                app.disconnect()
            apps.pop(uid, None)
            pending_logins.pop(uid, None)

        except SessionPasswordNeeded:
            
            bot.send_message(uid, "پسورد دو مرحله ای خودرا غیر فعال کنید")

        except Exception as ex:
            traceback.print_exc()
            bot.send_message(uid, "⚠️ یک خطای ناشناخته رخ داد. دوباره /login بزن.")
            if app.is_connected:
                app.disconnect()
            apps.pop(uid, None)
            pending_logins.pop(uid, None)

    threading.Thread(target=worker, daemon=True).start()


@bot.message_handler(commands=["start"])
def start(message):
    try:
            
        user_id = message.from_user.id
        username = message.from_user.username or "بدون نام"
        
            
   
        user_manager.add_user(user_id)
        reload_users() 


        if user_manager.is_banned(user_id):
            bot.send_message(user_id, "🚫 شما بن شده‌اید و نمی‌توانید از ربات استفاده کنید.")
            return

        
        if user_id == ADMIN_ID:
            bot.send_message(
                user_id,
                "👑 پنل مدیریت فعال شد:",
                reply_markup=admin_panel_keyboard()
            )
            return

        if user_manager.has_limit(user_id):
            pass
        else:
            user_manager.set_limit(user_id, 3)
      
        if is_member(user_id):
           
            if 1 == 1:
                bot.send_message(user_id, f"🎉 خوش آمدید! شما بار فرصت استفاده دارید.", reply_markup=main_markup())
            else:
                bot.send_message(user_id, "شما لیمیت خورده اید")

        else:
            bot.send_message(
                user_id,
                f"⚠️ برای استفاده از ربات باید در کانال‌های ما عضو شوید:",
                reply_markup=join_markup()
            )

    except Exception as ex:
        print(f"❌ [ERROR in /start] {ex}")
        bot.send_message(
            message.chat.id,
            "❌ یک خطای غیرمنتظره رخ داد. لطفاً دوباره تلاش کنید."
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check_membership(call):
    try:
        user_id = call.from_user.id
        
        if is_member(user_id):
            bot.send_message(
                user_id,
                "✅ شما در همه کانال‌ها عضو هستید. اکنون می‌توانید از ربات استفاده کنید.",
                reply_markup=main_markup()
            )
        else:
            bot.answer_callback_query(
                call.id,
                "❌ هنوز در برخی کانال‌ها عضو نشده‌اید.",
                show_alert=True
            )
    
    except Exception as ex:
        print(f"❌ خطا در check_membership: {ex}")

@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
def user_text_handler(message):
    try:
        text = message.text
        user_id = message.from_user.id
        
        
     
        if user_manager.is_banned(user_id):
            bot.send_message(user_id, "🚫 شما بن شده‌اید و نمی‌توانید از ربات استفاده کنید.")
            return

       
        if not is_member(user_id):
            bot.send_message(
                user_id,
                "⚠️ برای استفاده از ربات باید در کانال‌های ما عضو شوید:",
                reply_markup=join_markup()
            )
            return

        


        if text == "login":
            if 1 == 1:
                bot.send_message(user_id, "🔑 لطفاً شماره خود را وارد کنید:")
                bot.register_next_step_handler(message, ) 
            else:
                bot.send_message(user_id, "شما لیمیت خورده اید")

        elif text == "پشتیبانی":
            bot.send_message(message.chat.id, "فعلا پشتیبانی نداریم !!")

        elif text == "راهنما":
            bot.send_message(message.chat.id, "انتخاب کنید:", reply_markup=helper_markup())

        elif text == "قوانین":
            bot.send_message(message.chat.id, RULES_TEXT)

        elif text == "اموزش فعال سازی ربات":
            bot.send_message(message.chat.id, ACTIVATION_TEXT, reply_markup=main_markup())

        elif text == "بازگشت":
            bot.send_message(message.chat.id, "بازگشت به منوی اصلی:", reply_markup=main_markup())

        else:
            bot.send_message(message.chat.id, "❓ متوجه نشدم، لطفاً دوباره امتحان کنید.")

    except Exception as ex:
        print(f"❌ [ERROR in user_text_handler] {ex}")
        bot.send_message(message.chat.id, "❌ یک خطای غیرمنتظره رخ داد. دوباره تلاش کنید.")

#------------------------ MAIN ------------------------

if __name__ == "__main__":
    print("🤖 ربات شروع به کار کرد...")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ خطای کلی در اجرای ربات: {e}")
       