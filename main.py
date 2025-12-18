# import requests
# import time
# from telegram import Update
# from telegram.ext import (
#     ApplicationBuilder,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     ContextTypes
# )

# BOT_TOKEN = "7443817822:AAHZYeyaEcjyNSSPQPuNzbpQonxRAdMQe-A"

# # Store alerts: {chat_id: {coin, price}}
# alerts = {}

# COINS = {
#     "btc": "bitcoin",
#     "eth": "ethereum",
#     "sol": "solana"
# }

# # ---- Helper: Get price ----
# def get_price(coin_id):
#     url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
#     return requests.get(url).json()[coin_id]["usd"]

# # ---- Commands ----
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         "Welcome 👋\n"
#         "Select coin: BTC, ETH, SOL\n"
#         "Example:\n"
#         "btc 65000"
#     )

# async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         coin, price = update.message.text.lower().split()
#         price = float(price)

#         if coin not in COINS:
#             await update.message.reply_text("❌ Invalid coin. Use BTC, ETH, SOL")
#             return

#         alerts[update.message.chat_id] = {
#             "coin": COINS[coin],
#             "target": price
#         }

#         await update.message.reply_text(
#             f"✅ Alert set for {coin.upper()} at ${price}"
#         )

#     except:
#         await update.message.reply_text(
#             "❌ Format wrong\nExample: btc 65000"
#         )

# # ---- Price Checker Loop ----
# async def price_checker(app):
#     while True:
#         for chat_id, data in list(alerts.items()):
#             current_price = get_price(data["coin"])

#             if current_price >= data["target"]:
#                 await app.bot.send_message(
#                     chat_id=chat_id,
#                     text=f"🚨 Alert!\n{data['coin'].upper()} price reached ${current_price}"
#                 )
#                 del alerts[chat_id]

#         time.sleep(30)

# # ---- Main ----
# app = ApplicationBuilder().token(BOT_TOKEN).build()

# app.add_handler(CommandHandler("start", start))
# app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_alert))

# # Start background price checker
# app.job_queue.run_repeating(lambda _: None, interval=30, first=0)
# app.create_task(price_checker(app))

# print("Bot running...")
# app.run_polling()


import telebot
import requests
import time
import threading

BOT_TOKEN = "7443817822:AAHZYeyaEcjyNSSPQPuNzbpQonxRAdMQe-A"
bot = telebot.TeleBot(BOT_TOKEN)

# Store alerts
# {chat_id: {"coin": "bitcoin", "target": 65000}}
alerts = {}

COINS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana"
}

# ---------- Price Fetch ----------
def get_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    response = requests.get(url, timeout=10)
    return response.json()[coin_id]["usd"]

# ---------- Commands ----------
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome!\n\n"
        "Set price alert like this:\n"
        "btc 65000\n"
        "eth 3500\n"
        "sol 150"
    )

@bot.message_handler(func=lambda message: True)
def set_alert(message):
    try:
        coin, price = message.text.lower().split()
        price = float(price)

        if coin not in COINS:
            bot.send_message(message.chat.id, "❌ Use BTC, ETH, or SOL")
            return

        alerts[message.chat.id] = {
            "coin": COINS[coin],
            "target": price
        }

        bot.send_message(
            message.chat.id,
            f"✅ Alert set for {coin.upper()} at ${price}"
        )

    except:
        bot.send_message(
            message.chat.id,
            "❌ Wrong format\nExample: btc 65000"
        )

# ---------- Background Price Checker ----------
def price_checker():
    while True:
        time.sleep(30)

        for chat_id, data in list(alerts.items()):
            try:
                current_price = get_price(data["coin"])

                if current_price >= data["target"]:
                    bot.send_message(
                        chat_id,
                        f"🚨 ALERT!\n{data['coin'].upper()} reached ${current_price}"
                    )
                    del alerts[chat_id]

            except Exception as e:
                print("Error:", e)

# ---------- Start Background Thread ----------
threading.Thread(target=price_checker, daemon=True).start()

print("🤖 Bot is running...")
bot.infinity_polling()
