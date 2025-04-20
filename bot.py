import os
import logging
from PIL import Image
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 🔐 Bot tokenni bu yerga qo'y
API_KEY = "8075419027:AAEcOn8Husprt1418WGaNqMCJ7Q9T2Dl6Ho"

# 🧠 Foydalanuvchi ma'lumotlarini saqlash uchun
user_data = {}

# 🔧 Loglar
logging.basicConfig(level=logging.INFO)

# 💬 Start komandasi
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Salom! Rasmga logotip qo‘shuvchi botga xush kelibsiz.\n"
        "Avval logotipni yuboring (fayl ko'rinishida, rasm emas)."
    )
    user_data[update.message.chat_id] = {"step": "logo"}

# 📎 Logotipni qabul qilish
def handle_document(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if user_data.get(chat_id, {}).get("step") != "logo":
        return

    file = update.message.document.get_file()
    file_path = f"logo_{chat_id}.png"
    file.download(file_path)
    user_data[chat_id]["logo_path"] = file_path
    user_data[chat_id]["step"] = "image"

    markup = ReplyKeyboardMarkup(
        [['⬆️', '⬇️'], ['⬅️', '➡️'], ['◀️⬆️', '▶️⬇️']],
        resize_keyboard=True
    )
    update.message.reply_text(
        "✅ Logotip saqlandi. Endi surat yuboring va keyin logotip joylashuvini tanlang:",
        reply_markup=markup
    )

# 🖼 Rasmni qabul qilish
def handle_photo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if user_data.get(chat_id, {}).get("step") != "image":
        return

    photo = update.message.photo[-1].get_file()
    image_path = f"image_{chat_id}.jpg"
    photo.download(image_path)
    user_data[chat_id]["image_path"] = image_path
    update.message.reply_text("📍 Iltimos, logotip joylashuvini tanlang.")

# 📌 Joylashuvni tanlash
def handle_text(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    if user_data.get(chat_id, {}).get("step") != "image":
        return

    logo_path = user_data[chat_id]["logo_path"]
    image_path = user_data[chat_id]["image_path"]

    base_image = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    # Logoni kichiklashtirish
    logo.thumbnail((100, 100))
    base_width, base_height = base_image.size
    logo_width, logo_height = logo.size

    # Joylashuvlar
    positions = {
        '⬆️': (base_width // 2 - logo_width // 2, 10),
        '⬇️': (base_width // 2 - logo_width // 2, base_height - logo_height - 10),
        '⬅️': (10, base_height // 2 - logo_height // 2),
        '➡️': (base_width - logo_width - 10, base_height // 2 - logo_height // 2),
        '◀️⬆️': (10, 10),
        '▶️⬇️': (base_width - logo_width - 10, base_height - logo_height - 10),
    }

    pos = positions.get(text)
    if not pos:
        update.message.reply_text("❌ Noto‘g‘ri tanlov.")
        return

    base_image.paste(logo, pos, logo)

    output_path = f"result_{chat_id}.png"
    base_image.save(output_path)

    with open(output_path, 'rb') as f:
        update.message.reply_photo(photo=f, caption="✅ Tayyor! Logotip qo‘shildi.")

    # Fayllarni tozalash
    os.remove(logo_path)
    os.remove(image_path)
    os.remove(output_path)
    user_data.pop(chat_id)

# 🧠 Xatoliklar uchun fallback
def handle_unknown(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Noto‘g‘ri buyruq.")

# 🏃🏻‍♂️ Botni ishga tushirish
def main():
    updater = Updater(API_KEY)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_document))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(MessageHandler(Filters.text, handle_text))
    dp.add_handler(MessageHandler(Filters.command, handle_unknown))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
