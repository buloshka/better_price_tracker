import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from src.config import settings  # Безопасный импорт

# Инициализация бота с токеном из переменной окружения
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Логика бота...
    pass

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
