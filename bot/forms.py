from aiogram.dispatcher.filters.state import State, StatesGroup
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

class FactForm(StatesGroup):
    is_true = State()
    fact = State()