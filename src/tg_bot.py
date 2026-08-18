import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from src.config import settings


bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    return await message.answer('Hi, this bot helps to confirm users telegram id.')

async def send_verification_tg(
        tg_to: int,
        user_name: str,
        verification_url: str,
):
    text = f'Hi {user_name},\n\nOpen the link below to confirm user {tg_to}\n\n{verification_url}'
    return await bot.send_message(tg_to, text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
