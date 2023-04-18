import asyncio
import logging
from aiogram import Bot, Dispatcher, types, executor
from sql.models import User, Comment, Levels, Event
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

logging.basicConfig(level=logging.INFO)
bot = Bot(token="5899970158:AAEB_hBtdbQs4Izpv3foYmrIkARntrJZ6ug")
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    name = State()


class EventForm(StatesGroup):
    title = State()
    description = State()
    date = State()
    time = State()
    place = State()
    price = State()


async def set_main_menu():
    await bot.set_my_commands([
        BotCommand(command="/edit_bird", description="Изменить имя птицы"),
        BotCommand(command="/profile", description="Просмотреть профиль"),
        BotCommand(command="/create_event", description="Создать слет")
    ])

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Блин вау ну все")


@dp.message_handler(commands='edit_bird')
async def edit_bird(message: types.Message):
    await Form.name.set()
    await message.answer("Как вы хотите назвать птицу?")


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        id = message.from_user.id
        user = User()
        user.edit_bird_name(id, data['name'])
    await bot.send_message(id, f"Имя сменено на {data['name']}")
    await state.finish()

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

@dp.message_handler(content_types=['text'], commands=['profile'])
async def get_level_info(message: types.Message):
    if message.chat.type == 'private':
        id = message.from_user.id
        user = User().get_profile_data(id)
        l = Levels()
        level = User().get_profile_data(id).level
        bird = l.get_bird_data(level)
        msg = f"Ваша птица - {bird.bird_name}🐤\nИмя вашей птицы - {user.bird_name}\nВаш уровень - {level}\n{bird.bird_description}\nВаш прогресс - {user.level_progress}/100"
        await message.answer(msg)
    else:
        return

@dp.message_handler(commands=['create_event'])
async def create_event(message: types.Message):
    await EventForm.title.set()
    await message.answer("Введите название мероприятия")


@dp.message_handler(state=EventForm.title)
async def process_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await EventForm.next()
    await message.answer("Введите описание мероприятия")

@dp.message_handler(state=EventForm.description)
async def process_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await EventForm.next()
    await message.answer("Введите дату мероприятия")


@dp.message_handler(state=EventForm.date)
async def process_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text
    await EventForm.next()
    await message.answer("Введите время мероприятия")

@dp.message_handler(state=EventForm.time)
async def process_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
    await EventForm.next()
    await message.answer("Введите место мероприятия")


@dp.message_handler(state=EventForm.place)
async def process_place(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['place'] = message.text
    await EventForm.next()
    await message.answer("Введите стоимость мероприятия")


@dp.message_handler(state=EventForm.price)
async def process_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = int(message.text)
        await message.answer(f"{data['title']}\n{data['description']}")
        event = Event()
        event.create_event(data['title'], data['description'], data['date'], data['time'], data['place'], data['price'])
    await state.finish()


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


async def main():
    await set_main_menu()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
