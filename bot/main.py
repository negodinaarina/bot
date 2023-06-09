import asyncio, logging, random, datetime, os, kb
from aiogram import Bot, Dispatcher, types, executor
from sql.models import User, Levels, Event, Chat, Attendance, Facts, Features
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, InputFile
from forms import Form, FactForm, EventForm, CheckEventForm, BirdMailForm, AdminSigninForm
from dateutil.parser import parse
import time
import locale
locale.setlocale(locale.LC_ALL, "ru")
bot = Bot(token="6178498873:AAHb-vf_yWBanGlFRh-WVMWVysaWAYoEFBg")
dp = Dispatcher(bot, storage=MemoryStorage())


async def set_main_menu():
    await bot.set_my_commands([
        BotCommand(command="/edit_bird", description="Изменить имя птицы"),
        BotCommand(command="/profile", description="Просмотреть профиль"),
        BotCommand(command="/create_event", description="Создать слёт"),
        BotCommand(command="/check_event", description="Отметить слёт"),
        BotCommand(command="/bird_mail", description="Отправить письмо"),
        BotCommand(command="/add_fact", description="Добавить факт о себе"),
        BotCommand(command="/play_facts", description="Играть в факты"),
        BotCommand(command="/powers_info", description="Способности птицы"),
        BotCommand(command="/use_superpower", description="Использовать способность птицы"),
        BotCommand(command="/a", description="Секретный секрет")
    ])

@dp.message_handler(commands='edit_bird')
async def edit_bird(message: types.Message):
    if User().if_exists(message.from_user.id):
        if message.chat.type == "private":
            await Form.name.set()
            await message.answer("Как вы хотите назвать птицу?")
        else: return
    else:
        await message.answer("Сначала - регистрация!")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer('Действие отменено')

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        id = message.from_user.id
        user = User()
        user.edit_bird_name(id, data['name'])
    await bot.send_message(id, f"Имя сменено на *{data['name']}*", parse_mode= 'Markdown')
    await state.finish()


@dp.message_handler(commands=['reg'])
async def reg_user(message: types.Message):
    if message.chat.type == 'private':
        nickname = message.from_user.username
        id = message.from_user.id
        user = User()
        if user.if_exists(id):
            await message.answer("Вы уже зарегистрированы!")
        else:
            user.add_user(id=id, nickname=nickname)
            await message.answer("Вы успешно зарегистрировались!")
            await get_level_info(message)
    else:
        return

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if message.chat.type == 'private':
        await set_main_menu()
        await message.answer("Привет! Я бот, который поможет вашему коллективу сплотиться! Отправь /reg , чтобы зарегистрироваться для дальнейшего взаимодействия:)")

@dp.message_handler(content_types=['text'], commands=['profile'])
async def get_level_info(message: types.Message):
    if message.chat.type == 'private':
        if User().if_exists(message.from_user.id):
            id = message.from_user.id
            user = User().get_profile_data(id)
            l = Levels()
            level = User().get_profile_data(id).level
            bird = l.get_bird_data(level)
            usr_path=os.path.abspath('images')[:-11]
            photo = InputFile(f"{usr_path}{bird.img_path}")
            msg = f"Ваша птица: *{bird.bird_name}*\nИмя вашей птицы: *{user.bird_name}*\nВаш уровень: *{level}*" \
                  f"\n{bird.bird_description}\nВаш прогресс: *{user.level_progress}/100 зёрен*."
            await bot.send_photo(message.from_user.id, photo,
                                 caption=msg,
                                 reply_to_message_id=message.message_id,
                                 parse_mode='Markdown')
        else:
            await message.answer("Профиль не найден...")

@dp.message_handler(commands=['create_event'])
async def create_event(message: types.Message):
    if User().if_exists(message.from_user.id):
        if User().is_admin(message.from_user.id):
            print(Chat.get_all_chats())
            if len(Chat.get_all_chats())!=0:
                await EventForm.title.set()
                await message.answer("Введите название мероприятия")
            else:
                await message.answer("Бот не зарегистрирован ни в одном чате!")
        else:
            await message.answer("Вы не являетесь птицей-админом!")
    else:
        await message.answer("Сначала нужно зарегистрироваться!")
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer('Отмена действия')

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
    await message.answer("Введите дату мероприятия в формате день/месяц/год")


@dp.message_handler(state=EventForm.date)
async def process_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            date = parse(message.text, dayfirst=True)
            if date > datetime.datetime.now():
                day = date.strftime("%d")
                day = day[1] if day[0] == '0' else day
                month = date.strftime("%B")
                lower_month = month[0].lower() + month[1:]
                padej = lower_month+'a' if lower_month in ['март','август'] else lower_month+'я'
                data['date'] = f'{day} {padej}'
                await EventForm.next()
                await message.answer("Введите время мероприятия в формате часы:минуты")
            else:
                await message.answer("Кажется к этой дате птицы не успеют слететься...\nПопробуйте ввести дату из "
                                     "будущего")
        except ValueError:
            await message.answer("Попробуйте ввести дату еще раз")




@dp.message_handler(state=EventForm.time)
async def process_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            t = time.strptime(message.text, "%H:%M")
            data['time'] = message.text
            await EventForm.next()
            await message.answer("Введите место мероприятия")
        except:
            await message.answer("Попробуйте ввести время еще раз")


@dp.message_handler(state=EventForm.place)
async def process_place(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['place'] = message.text
    await EventForm.next()
    await message.answer("Введите стоимость мероприятия")


@dp.message_handler(state=EventForm.price)
async def process_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            data['price'] = int(message.text)
            await EventForm.next()
            await message.answer("Введите кодовое слово")
        except:
            await message.answer("Неверный формат, попробуйте снова!")

@dp.message_handler(state=EventForm.code_phrase)
async def process_phrase(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['code_phrase'] = message.text
        event = Event()
        if event.get_event(data['code_phrase']) == None:
            event.create_event(data['title'], data['description'], data['date'], data['time'], data['place'], data['price'], data['code_phrase'])
            await EventForm().next()
            chats = Chat.get_all_chats()
            choice = ''
            for chat in chats:
                choice += f"`{chat.chat_name}`\n"
            await message.answer(f"Выберите чат:\n{choice}", parse_mode='Markdown')
        else:
            await message.answer("Такое кодовое слово уже существует, попробуйте снова!")


@dp.message_handler(state=EventForm.chat_id)
async def end_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['chat_id'] = message.text
        ch = Chat()
        chat = ch.get_chat_by_title(data['chat_id'])
        msg = f"Новый слёт!\n*{data['title']}*\n{data['description']}\n{data['date']} {data['time']}\n" \
              f"{data['place']}\nНаграда - *{data['price']} зёрен*."
        await message.answer("Мероприятие создано, объявление отправлено в общий чат")
        await bot.send_message(chat.chat_id, msg, parse_mode='Markdown')
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
    if message.chat.type == 'private':
        if User().if_exists(message.from_user.id):
            await CheckEventForm.code_phrase.set()
            await message.answer("Введите кодовое слово")
        else:
            await message.answer("Необходима регистрация!")


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
            a = Attendance()
            attendance = a.get_attendance(id, event.id)
            if attendance:
                await message.answer("Вы уже отметились на данное мероприятие!")
            else:
                a.add_attendance(id, event.id)
                user.change_level_progress(id, points)
                await message.answer(f"Мероприятие отмечено. Зерен получено: *{points}* ", parse_mode='Markdown')
        except:
            await message.answer(f"Мероприятие не найдено...")
    await state.finish()


@dp.message_handler(commands=['bird_mail'])
async def cmd_start(message: types.Message):
    if message.chat.type == 'private':
        if User().if_exists(message.from_user.id):
            u = User()
            user = u.get_profile_data(message.from_user.id)
            delta = datetime.datetime.now() - user.last_mail
            if delta.days >= 1:
                random_user = u.get_user_notid(message.from_user.id)
                if random_user is not None:
                    u.change_mail_date(message.from_user.id, datetime.datetime.now())
                    await BirdMailForm.letter.set()
                    await message.answer("Напишите письмо!")
                else:
                    await message.answer("Некому писать....")
                    return
            else: await message.answer("Вы уже писали письмо за последние сутки!")
            return
        else:
            await message.answer("Вы не можете пользоваться птичьей почтой до регистрации!")


@dp.message_handler(state=BirdMailForm.letter)
async def process_phrase(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['letter'] = message.text
        u = User()
        random_user = u.get_user_notid(message.from_user.id)
        await bot.send_message(random_user.tg_id, f"Вам пришло письмо по птичьей почте:\n\n\U0001F48C	"
                                                  f"_{data['letter']}_\U0001F48C",
                               parse_mode='Markdown')
        u.change_level_progress(message.from_user.id, 5)
        await message.answer("Сообщение отправлено, вы получили *5 зёрен*.", parse_mode='Markdown')
    await state.finish()


@dp.message_handler(commands=['add_fact'])
async def cmd_start(message: types.Message):
    if message.chat.type == 'private':
        if User().if_exists(message.from_user.id):
            await FactForm.is_true.set()
            await message.answer("Введите тип факта: правда/ложь")
        else:
            await message.answer("Зарегистрируйтесь!")



@dp.message_handler(state=FactForm.is_true)
async def process_phrase(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['is_true'] = message.text
        if data['is_true'] in ['правда', 'ложь', 'Правда', 'Ложь']:
            await FactForm.next()
            await message.answer("Введите факт о себе")
        else: await message.answer("Неверный формат типа факта, попробуйте еще раз!")

@dp.message_handler(state=FactForm.fact)
async def process_phrase(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['fact'] = message.text
        fact = Facts()
        if data['is_true'] == 'правда':
            is_true = True
        else:
            is_true = False
        fact.add_fact(message.from_user.id, message.from_user.full_name, data['fact'], is_true)
    await message.answer("Факт добавлен в копилку викторины!")
    await state.finish()

@dp.message_handler(commands=['play_facts'])
async def play_facts(message: types.Message):
    if message.chat.type == 'private' and User().if_exists(message.from_user.id):
        u = User()
        user = u.get_profile_data(message.from_user.id)
        f = Facts()
        fact = f.get_fact(user.tg_id, user.last_fact)
        if fact is not None:
            await message.answer(f"ФАКТ:\n{fact.fact}\nОТ:{fact.user_name}", reply_markup=kb.inline_kb_full)
        else: await message.answer("Факты закончились.... Подождите, пока кто-нибудь не расскажет о себе!")

@dp.callback_query_handler(lambda c: c.data == 'pressed_true')
async def process_callback_true(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    f = Facts()
    u = User()
    user = u.get_profile_data(callback_query.from_user.id)
    fact = f.get_fact(user.tg_id, user.last_fact)
    if fact.is_true:
        await bot.send_message(callback_query.from_user.id, 'Правильный ответ!')
        u.change_level_progress(callback_query.from_user.id, 5)
    else:
        await bot.send_message(callback_query.from_user.id, 'К сожалению,не верно...')
    try:
        if fact.id == user.last_fact:
            user.change_last_fact(fact.id + 1)
        else:
            user.change_last_fact(fact.id)
    except AttributeError:
        pass


@dp.callback_query_handler(lambda c: c.data == 'pressed_false')
async def process_callback_false(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    f = Facts()
    u = User()
    user = u.get_profile_data(callback_query.from_user.id)
    fact = f.get_fact(user.tg_id, user.last_fact)
    if not fact.is_true:
        await bot.send_message(callback_query.from_user.id, 'Правильный ответ!')
        u.change_level_progress(callback_query.from_user.id, 5)
    else:
        await bot.send_message(callback_query.from_user.id, 'К сожалению,не верно...')
    try:
        if fact.id == user.last_fact:
            user.change_last_fact(fact.id + 1)
        else:
            user.change_last_fact(fact.id)
    except AttributeError:
        pass


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

@dp.message_handler(commands=['powers_info'])
async def powers_info(message: types.Message):
    if message.chat.type == 'private':
        if User().if_exists(message.from_user.id):
            user = User().get_profile_data(message.from_user.id)
            features = Features().get_level_features(user.level)
            msg = 'Способности птицы вашего уровня:'
            for feature in features:
                if feature.is_stolen:
                    stolen = 'Воровство'
                else:
                    stolen = 'Удача'
                msg += f'\n*{feature.name}*\n{feature.description}\nКоличество зерен, которое можно получить: от' \
                       f' *{feature.min_seeds}* до *{feature.max_seeds}*\nТип способности:*{stolen}*\n\n'
            await message.answer(msg, parse_mode= 'Markdown')
        else:
            await message.answer("Вы не зарегистрированы!")


@dp.message_handler(commands=['use_superpower'])
async def use_superpower(message: types.Message):
    if message.chat.type == 'private' and User().if_exists(message.from_user.id):
        u = User()
        user = u.get_profile_data(message.from_user.id)
        if user.powers_used < 5:
            await message.answer(f"Выберите номер суперспособности(написанные номера способностей не соответствуют номерам из описания, выбирая номер, вы выбираете случайную способность)", reply_markup=kb.features_kb_full)
        else:
            await message.answer("Вы уже исчерпали лимит использования способностей на вашем уровне!")
@dp.callback_query_handler(lambda c: int(c.data) == 0)
async def process_callback_1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    u = User()
    user = u.get_profile_data(callback_query.from_user.id)
    if user.powers_used >= 5:
        await bot.send_message(callback_query.from_user.id, "К сожалению, вы использовали все возможные попытки использовать способность на вашем уровне!")
        return
    f = Features()
    features = f.get_level_features(user.level)
    random.shuffle(features)
    feature = features[0]
    usr_path = os.path.abspath('images')[:-11]
    photo = InputFile(f"{usr_path}{feature.img_path}")
    seeds = random.randint(feature.min_seeds, feature.max_seeds)
    if feature.is_stolen:
        random_user = u.get_user_notid(callback_query.from_user.id)
        if random_user is not None and random_user.level > 0 and random_user.level_progress >= seeds:
            random_user.change_level_progress(random_user.tg_id, seeds*(-1))
            await bot.send_message(random_user.tg_id, f"Птица *{user.bird_name}* игрока *{user.tg_nickname}* забрал у "
                                                      f"вашей птицы зёрен: *{seeds}*", parse_mode='Markdown')
            user.change_level_progress(user.tg_id, seeds)
            user.change_powers_used(1)
            await bot.send_photo(callback_query.from_user.id, photo, caption=f"Использована суперспособность:\n{feature.name}\nВы забрали зёрна: {seeds} от пользователя {random_user.tg_nickname}")
        else: await bot.send_message(callback_query.from_user.id, "Шалость не удалась, вам выпала способность типа Воровство, однако вы не ожете украсть зёрна, так как у другого игрока меньше зёрен.")
    else:
        user.change_level_progress(user.tg_id, seeds)
        await bot.send_photo(callback_query.from_user.id, photo,
                               caption=f"Использована суперспособность:{feature.name}\nВы получили зерна:{seeds}")
    user.change_powers_used(1)


@dp.callback_query_handler(lambda c: int(c.data) == 1)
async def process_callback_2(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    u = User()
    user = u.get_profile_data(callback_query.from_user.id)
    if user.powers_used >= 5:
        await bot.send_message(callback_query.from_user.id, "К сожалению, вы использовали все возможные попытки использовать способность на вашем уровне!")
        return
    f = Features()
    features = f.get_level_features(user.level)
    random.shuffle(features)
    feature = features[1]
    usr_path = os.path.abspath('images')[:-11]
    photo = InputFile(f"{usr_path}{feature.img_path}")
    seeds = random.randint(feature.min_seeds, feature.max_seeds)
    if feature.is_stolen:
        random_user = u.get_user_notid(callback_query.from_user.id)
        if random_user is not None and random_user.level > 0 and random_user.level_progress >= seeds:
            random_user.change_level_progress(random_user.tg_id, seeds*(-1))
            await bot.send_message(random_user.tg_id, f"Птица *{user.bird_name}* игрока *{user.tg_nickname}* забрал у "
                                                      f"вашей птицы зёрен: *{seeds}*", parse_mode='Markdown')
            user.change_level_progress(user.tg_id, seeds)
            user.change_powers_used(1)
            await bot.send_photo(callback_query.from_user.id, photo, caption=f"Использована суперспособность:\n{feature.name}\nВы забрали зёрна: {seeds} от пользователя {random_user.tg_nickname}")
        else: await bot.send_message(callback_query.from_user.id, "Шалость не удалась, вам выпала способность типа Воровство, однако вы не ожете украсть зёрна, так как у другого игрока меньше зёрен.")
    else:
        user.change_level_progress(user.tg_id, seeds)
        await bot.send_photo(callback_query.from_user.id, photo,
                               caption=f"Использована суперспособность:{feature.name}\nВы получили зерна:{seeds}")
    user.change_powers_used(1)


@dp.callback_query_handler(lambda c: int(c.data) == 2)
async def process_callback_3(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    u = User()
    user = u.get_profile_data(callback_query.from_user.id)
    if user.powers_used >= 5:
        await bot.send_message(callback_query.from_user.id, "К сожалению, вы использовали все возможные попытки использовать способность на вашем уровне!")
        return
    f = Features()
    features = f.get_level_features(user.level)
    random.shuffle(features)
    feature = features[2]
    usr_path = os.path.abspath('images')[:-11]
    photo = InputFile(f"{usr_path}{feature.img_path}")
    seeds = random.randint(feature.min_seeds, feature.max_seeds)
    if feature.is_stolen:
        random_user = u.get_user_notid(callback_query.from_user.id)
        if random_user is not None and random_user.level > 0 and random_user.level_progress >= seeds:
            random_user.change_level_progress(random_user.tg_id, seeds*(-1))
            await bot.send_message(random_user.tg_id, f"Птица *{user.bird_name}* игрока *{user.tg_nickname}* забрал у "
                                                      f"вашей птицы зёрен: *{seeds}*", parse_mode= 'Markdown')
            user.change_level_progress(user.tg_id, seeds)
            user.change_powers_used(1)
            await bot.send_photo(callback_query.from_user.id, photo, caption=f"Использована суперспособность:\n{feature.name}\nВы забрали зёрна: {seeds} от пользователя {random_user.tg_nickname}")
        else: await bot.send_message(callback_query.from_user.id, "Шалость не удалась, вам выпала способность типа Воровство, однако вы не ожете украсть зёрна, так как у другого игрока меньше зёрен.")
    else:
        user.change_level_progress(user.tg_id, seeds)
        await bot.send_photo(callback_query.from_user.id, photo,
                               caption=f"Использована суперспособность:{feature.name}\nВы получили зерна:{seeds}")
    user.change_powers_used(1)

async def main():
    await set_main_menu()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

