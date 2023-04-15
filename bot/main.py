import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from sql.models import User, Comment, Levels

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="5899970158:AAEB_hBtdbQs4Izpv3foYmrIkARntrJZ6ug")
# Диспетчер
dp = Dispatcher(bot)


# Хэндлер на команду /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Блин вау ну все")


@dp.message_handler(commands=['edit_bird'])
async def edit_bird(message:types.Message):
    await message.answer("Как вы хотите назвать свою птицу?")
#     блять я птица


@dp.message_handler(commands=['reg'])
async def reg_user(message: types.Message):
    if message.chat.type == 'private':
        nickname = message.from_user.username
        id = message.from_user.id
        user = User()
        if user.if_exists(id):
            await message.answer("Ты ху?й")
        else:
            user.add_user(id=id, nickname=nickname)
            await message.answer("Вы успешно зарегались!")
            await get_level_info(message)
    else:
        return


@dp.message_handler(commands=['profile'])
async def get_level_info(message: types.Message):
    if message.chat.type == 'private':
        id = message.from_user.id
        u = User()
        user = u.get_profile_data(id)
        level = u.get_profile_data(id).level
        l = Levels()
        bird = l.get_bird_data(level)
        msg = f"Ваша птица - {bird.bird_name}🐤\nИмя вашей птицы - {user.bird_name}\nВаш уровень - {level}\n{bird.bird_description}\nВаш прогресс - {user.level_progress}/100"
        await message.answer(msg)
    else:
        return

@dp.message_handler(commands=['edit'])

@dp.message_handler(commands=['нахуй_сходи'])
async def cmd_start(message: types.Message):
    await message.answer("Сходил")


@dp.message_handler(commands=['блять'])
async def cmd_start(message: types.Message):
    await message.answer("Согласен")


@dp.message_handler(commands=['как_дела'])
async def cmd_start(message: types.Message):
    await message.answer("я хочу псж")


@dp.message_handler()
async def cmd_start(message: types.Message):
    return message.text
# Запуск процесса поллинга новых апдейтов


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
