from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    waiting_for_event_title = State()
    waiting_for_event_time = State()
    waiting_for_auth = State()
    waiting_for_timezone = State()
