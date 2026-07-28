from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandObject, Command
import asyncio

from src.main import users_db


bot = Bot(token="8943332047:AAFO9YE6_mRBWBELT56W30RL91UJ8E6CrXs")
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    token = command.args

    if not token:
        await message.answer("Привет! Пожалуйста, перейдите по ссылке из вашего личного кабинета на сайте.")
        return

    user_found = False
    for user_id, user_data in users_db.items():
        if user_data["telegram_token"] == token:
            user_data["telegram_id"] = message.from_user.id
            user_data["telegram_token"] = None
            user_found = True
            break

    if user_found:
        await message.answer("🎉 Аккаунт успешно привязан к сайту! Можете вернуться на страницу.")
    else:
        await message.answer("❌ Ошибка: Ссылка устарела или недействительна.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
