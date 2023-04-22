import asyncio
import logging
from aiogram import Bot, Dispatcher, types, executor
from sql.models import User, Comment, Levels, Event, Chat
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, InputFile
import random
import datetime

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
    code_phrase = State()
    chat_id = State()

class CheckEventForm(StatesGroup):
    code_phrase = State()

class AdminSigninForm(StatesGroup):
    password = State()

class BirdMailForm(StatesGroup):
    letter = State()

# async def set_main_menu():
#     await bot.set_my_commands([
#         BotCommand(command="/edit_bird", description="Изменить имя птицы"),
#         BotCommand(command="/profile", description="Просмотреть профиль"),
#         BotCommand(command="/create_event", description="Создать слёт"),
#         BotCommand(command="/check_event", description="Отметить слёт"),
#         BotCommand(command="/bird_mail", description="Отправить письмо")
#     ])

@dp.message_handler(commands='edit_bird')
async def edit_bird(message: types.Message):
    if User().if_exists(message.from_user.id) and message.chat.type == "private":
        await Form.name.set()
        await message.answer("Как вы хотите назвать птицу?")

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer('конец')

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

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот, который поможет вашему коллективу сплотиться! Отправь /reg , чтобы зарегистрироваться для дальнейшего взаимодействия:)")

@dp.message_handler(content_types=['text'], commands=['profile'])
async def get_level_info(message: types.Message):
    if message.chat.type == 'private' and User().if_exists(message.from_user.id):
        id = message.from_user.id
        user = User().get_profile_data(id)
        l = Levels()
        level = User().get_profile_data(id).level
        bird = l.get_bird_data(level)
        photo = InputFile(f"{bird.img_path}")
        msg = f"Ваша птица - {bird.bird_name}🐤\nИмя вашей птицы - {user.bird_name}\nВаш уровень - {level}\n{bird.bird_description}\nВаш прогресс - {user.level_progress}/100"
        # await message.answer(msg)
        await bot.send_photo(message.from_user.id, photo,
                             caption=msg,
                             reply_to_message_id=message.message_id)

    else:
        return

@dp.message_handler(commands=['create_event'])
async def create_event(message: types.Message):
    if User().if_exists(message.from_user.id) and User().is_admin(message.from_user.id):
        await EventForm.title.set()
        await message.answer("Введите название мероприятия")
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer('конец')

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
    await EventForm.next()
    await message.answer("Введите кодовое слово")


@dp.message_handler(state=EventForm.code_phrase)
async def process_phrase(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['code_phrase'] = message.text
        event = Event()
        event.create_event(data['title'], data['description'], data['date'], data['time'], data['place'], data['price'], data['code_phrase'])
    await EventForm().next()
    chats = Chat.get_all_chats()
    choice = ''
    for chat in chats:
        choice += f"{chat.chat_name}\n"
    await message.answer(f"Выберите чат:\n{choice}")


@dp.message_handler(state=EventForm.chat_id)
async def end_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['chat_id'] = message.text
        ch = Chat()
        chat = ch.get_chat_by_title(data['chat_id'])
        msg = f"Новый слёт!\n{data['title']}\n{data['description']}\n{data['date']} {data['time']}\n{data['place']}\n Награда - {data['price']} зёрен."
        await message.answer("Мероприятие создано, объявление отправлено в общий чат")
        await bot.send_message(chat.chat_id, msg)
    await state.finish()


@dp.message_handler(commands=['reg_chat'])
async def cmd_reg_chat(message: types.Message):
    id = message.chat.id
    title = message.chat.title
    chat = Chat()
    chat.add_chat(id, title)
    await message.answer("Чат зарегистрирован")


@dp.message_handler(commands=['check_event'])
async def check_event(message: types.Message):
    if message.chat.type == 'private' and User().if_exists(message.from_user.id):
        await CheckEventForm.code_phrase.set()
        await message.answer("Введите кодовое слово")
    else:
        pass

@dp.message_handler(state=CheckEventForm.code_phrase)
async def process_phrase(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['code_phrase'] = message.text
        try:
            e = Event()
            event = e.get_event(data['code_phrase'])
            points = event.price
            id = message.from_user.id
            user = User().get_profile_data(id)
            user.change_level_progress(id, points)
            await message.answer(f"Мероприятие отмечено, вы получили  {points} зерен!")
        except:
            await message.answer(f"Мероприятие не найдено...")
    await state.finish()


@dp.message_handler(commands=['bird_mail'])
async def cmd_start(message: types.Message):
    if message.chat.type == 'private' and User().if_exists(message.from_user.id):
        u = User()
        user = u.get_profile_data(message.from_user.id)
        delta = datetime.datetime.now() - user.last_mail
        if delta.days >= 1:
            u.change_mail_date(message.from_user.id, datetime.datetime.now())
            await BirdMailForm.letter.set()
            await message.answer("Напишите письмо!")
        else:
            await message.answer("Вы уже писали письмо за последние сутки!")
            return
    else:
        pass

@dp.message_handler(state=BirdMailForm.letter)
async def process_phrase(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['letter'] = message.text
        try:
            u = User()
            users = u.all_users()
            while True:
                user = random.choice(users)
                if user.tg_id != message.from_user.id:
                    await bot.send_message(user.tg_id, f"Вам пришлописьмо по птичьей почте:\n{data['letter']}")
                    u.change_level_progress(message.from_user.id, 5)
                    await message.answer("Сообщение отправлено, вы получили 5 зёрен.")
                    break
        except:
            await message.answer(f"Что-то пошло не так...")
    await state.finish()


@dp.message_handler(commands=['a'])
async def admin_signin(message: types.Message):
    if User().if_exists(message.from_user.id) and message.chat.type == "private":
        await AdminSigninForm.password.set()
        await message.answer("Введите пароль")
    else:
        await message.answer('Вас нет!')


@dp.message_handler(state=AdminSigninForm.password)
async def process_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
        if data['password'] == 'password':
            User().change_status(message.from_user.id, True)
            await message.answer("Статус сменен!")
        else:
            await message.answer("Неверный пароль")
    await state.finish()


async def main():
    # await set_main_menu()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

