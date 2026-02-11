import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from geopy.geocoders import Nominatim

TOKEN = os.getenv("BOT_TOKEN")
geolocator = Nominatim(user_agent="my_telegram_bot")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"Namaste {user.first_name}!\n\n"
        f"🆔 ID: `{user.id}`\n"
        f"👤 Username: @{user.username}\n\n"
        "📍 Neeche button par click karke apni location share karein:"
    )
    
    keyboard = [[KeyboardButton("📍 Share Location", request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    lat, lon = location.latitude, location.longitude

    try:
        # Latitude/Longitude se address nikalna
        address = geolocator.reverse(f"{lat}, {lon}", timeout=10).raw.get('address', {})
        
        city = address.get('city') or address.get('town') or address.get('village') or "N/A"
        state = address.get('state', "N/A")
        country = address.get('country', "N/A")
        area = address.get('suburb') or address.get('neighbourhood') or "N/A"

        result = (
            f"✅ **Location Details:**\n\n"
            f"🌍 Country: {country}\n"
            f"🏙️ State: {state}\n"
            f"🏙️ City/Town: {city}\n"
            f"🏘️ Area: {area}\n"
            f"📍 Lat/Lon: `{lat}, {lon}`"
        )
    except Exception as e:
        result = f"Location mil gayi, par address fetch nahi ho paya.\nLat: {lat}, Lon: {lon}"

    await update.message.reply_text(result, parse_mode='Markdown')

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.run_polling()