import telebot
from telebot import types
from datetime import datetime
import json
import os

BOT_TOKEN = "9244500850:AAE4tTVFRmB_svDhaEM2BfkVWEkCNKQjQsU"
ADMIN_ID =8991837989
FOLDER_LINK = "https://t.me/addlist/HmeyViz5pRY2NDFk"
REQUIRED_REFS = 15

bot = telebot.TeleBot(BOT_TOKEN)

# --- Veri Yönetimi ---
DATA_FILE = "users.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user(user_id, username=None, first_name=None):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "id": user_id,
            "username": username or "Yok",
            "first_name": first_name or "Kullanıcı",
            "join_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "refs": 0,
            "referred_by": None,
            "unlocked": False
        }
        save_data(data)
    return data[uid]

def update_user(user_id, **kwargs):
    data = load_data()
    uid = str(user_id)
    if uid in data:
        data[uid].update(kwargs)
        save_data(data)

# --- /start ---
@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user
    args = message.text.split()
    
    u = get_user(user.id, user.username, user.first_name)
    
    # Referans kontrolü
    if len(args) > 1:
        ref_id = args[1]
        if ref_id != str(user.id) and not u["referred_by"]:
            data = load_data()
            update_user(user.id, referred_by=ref_id)
            if ref_id in data:
                new_refs = data[ref_id]["refs"] + 1
                update_user(int(ref_id), refs=new_refs)
                if new_refs >= REQUIRED_REFS:
                    update_user(int(ref_id), unlocked=True)
                try:
                    bot.send_message(int(ref_id), f"🎉 Yeni referansın geldi! Toplam: {new_refs}/{REQUIRED_REFS}")
                except:
                    pass

    text = (
        f"👋 Merhaba *{user.first_name}*!\n\n"
        f"Ben *Ücretsiz Sanal Numara Botuyum*.\n\n"
        f"🔒 Botu açmak için:\n"
        f"1️⃣ Klasöre katıl\n"
        f"2️⃣ Referans linkini paylaş ve *{REQUIRED_REFS} kişi* getir\n\n"
        f"✅ Şartları tamamlayınca bot otomatik açılır!"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("👤 Profilim", callback_data="profile"),
        types.InlineKeyboardButton("🔗 Referans Linkim", callback_data="referral"),
        types.InlineKeyboardButton("📁 Klasöre Katıl", url=FOLDER_LINK)
    )

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)


# --- Profil Callback ---
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def profile(call):
    u = get_user(call.from_user.id, call.from_user.username, call.from_user.first_name)
    status = "✅ Açık" if u["unlocked"] else f"🔒 Kapalı ({u['refs']}/{REQUIRED_REFS} referans)"

    text = (
        f"👤 *Profilim*\n\n"
        f"📛 İsim: {u['first_name']}\n"
        f"🔖 Kullanıcı adı: @{u['username']}\n"
        f"🆔 ID: `{u['id']}`\n"
        f"📅 Katılma tarihi: {u['join_date']}\n"
        f"👥 Referans sayısı: {u['refs']}/{REQUIRED_REFS}\n"
        f"🤖 Bot durumu: {status}"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Geri", callback_data="back"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)


# --- Referans Callback ---
@bot.callback_query_handler(func=lambda c: c.data == "referral")
def referral(call):
    uid = call.from_user.id
    link = f"https://t.me/UcretsizN0Bot?start={uid}"
    u = get_user(uid)

    text = (
        f"🔗 *Referans Linkin:*\n`{link}`\n\n"
        f"👥 Getirdiğin kişi: *{u['refs']}/{REQUIRED_REFS}*\n\n"
        f"Bu linki paylaş, {REQUIRED_REFS} kişi gelince bot açılır!"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Geri", callback_data="back"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)


# --- Geri Callback ---
@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(call):
    user = call.from_user
    text = (
        f"👋 Merhaba *{user.first_name}*!\n\n"
        f"🔒 Botu açmak için:\n"
        f"1️⃣ Klasöre katıl\n"
        f"2️⃣ {REQUIRED_REFS} kişi getir\n\n"
        f"✅ Şartları tamamlayınca bot otomatik açılır!"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("👤 Profilim", callback_data="profile"),
        types.InlineKeyboardButton("🔗 Referans Linkim", callback_data="referral"),
        types.InlineKeyboardButton("📁 Klasöre Katıl", url=FOLDER_LINK)
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)


# --- Admin Paneli ---
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "❌ Yetkisiz erişim.")

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 İstatistik", callback_data="admin_stats"),
        types.InlineKeyboardButton("📣 Duyuru", callback_data="admin_announce"),
        types.InlineKeyboardButton("🏆 Zenginler Listesi", callback_data="admin_rich"),
        types.InlineKeyboardButton("🔓 Kullanıcı Aç", callback_data="admin_unlock")
    )
    bot.send_message(message.chat.id, "🛠 *Admin Paneli*", parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == "admin_stats")
def admin_stats(call):
    if call.from_user.id != ADMIN_ID:
        return
    data = load_data()
    total = len(data)
    unlocked = sum(1 for u in data.values() if u["unlocked"])
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id,
        f"📊 *İstatistik*\n\n👥 Toplam kullanıcı: {total}\n✅ Açık hesap: {unlocked}\n🔒 Kilitli: {total - unlocked}",
        parse_mode="Markdown")


@bot.callback_query_handler(func=lambda c: c.data == "admin_rich")
def admin_rich(call):
    if call.from_user.id != ADMIN_ID:
        return
    data = load_data()
    sorted_users = sorted(data.values(), key=lambda x: x["refs"], reverse=True)[:10]
    text = "🏆 *En Çok Referans Getirenler*\n\n"
    for i, u in enumerate(sorted_users, 1):
        text += f"{i}. {u['first_name']} — {u['refs']} referans\n"
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")


# Duyuru için state
announce_mode = {}

@bot.callback_query_handler(func=lambda c: c.data == "admin_announce")
def admin_announce(call):
    if call.from_user.id != ADMIN_ID:
        return
    announce_mode[ADMIN_ID] = True
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "📣 Duyuru mesajını yaz:")


@bot.message_handler(func=lambda m: announce_mode.get(m.from_user.id))
def send_announce(message):
    if message.from_user.id != ADMIN_ID:
        return
    announce_mode.pop(ADMIN_ID, None)
    data = load_data()
    success = 0
    for uid in data:
        try:
            bot.send_message(int(uid), f"📣 *Duyuru:*\n\n{message.text}", parse_mode="Markdown")
            success += 1
        except:
            pass
    bot.send_message(message.chat.id, f"✅ Duyuru {success} kullanıcıya gönderildi.")


# Kullanıcı kilidi açma
unlock_mode = {}

@bot.callback_query_handler(func=lambda c: c.data == "admin_unlock")
def admin_unlock(call):
    if call.from_user.id != ADMIN_ID:
        return
    unlock_mode[ADMIN_ID] = True
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🔓 Açmak istediğin kullanıcının ID'sini gönder:")


@bot.message_handler(func=lambda m: unlock_mode.get(m.from_user.id))
def do_unlock(message):
    if message.from_user.id != ADMIN_ID:
        return
    unlock_mode.pop(ADMIN_ID, None)
    uid = message.text.strip()
    data = load_data()
    if uid in data:
        update_user(int(uid), unlocked=True)
        bot.send_message(message.chat.id, f"✅ {uid} açıldı.")
        try:
            bot.send_message(int(uid), "🎉 Botun açıldı! Artık kullanabilirsin.")
        except:
            pass
    else:
        bot.send_message(message.chat.id, "❌ Kullanıcı bulunamadı.")


print("Bot başlatıldı...")
bot.infinity_polling()