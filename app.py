import os
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

# Flask приложение
app = Flask(__name__)

# Бот
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Обработчики
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я бот на Render! 🤖")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"✅ Ты написал: {message.text}")

# Flask эндпоинты
@app.route('/')
def index():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK"

# Запуск бота в фоновом потоке
def run_bot():
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем Flask на порту, который даёт Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)