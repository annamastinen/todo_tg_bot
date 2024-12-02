import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, F, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.fsm.context import FSMContext
import datetime
import pytz
from pomo_token import TOKEN  # скрыть token
from user_states import Form
from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    waiting_for_event_title = State()
    waiting_for_event_time = State()
    waiting_for_auth = State()
    waiting_for_timezone = State()


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

command_router = Router()
dp.include_router(command_router)


# Обработчик команды /start
@command_router.message(CommandStart())
async def cmd_hello(message: Message):
    # Приветственное сообщение
    await message.answer("Привет, я - твой помощник 2.0 и я пытаюсь работать!\n")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/set_timezone")]], resize_keyboard=True
    )
    await message.answer(
        "Чтобы установить часовой пояс, нажми на кнопку ниже:",
        reply_markup=keyboard,
    )


# Обработчик команды для запроса часового пояса
@command_router.message(Command("set_timezone"))
async def set_timezone(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, укажи свой часовой пояс (например, 'Europe/Moscow')."
    )
    await state.set_state(Form.waiting_for_timezone)


@command_router.message(StateFilter(Form.waiting_for_timezone))
async def process_timezone(message: types.Message, state: FSMContext):
    # Получаем введенный пользователем часовой пояс
    user_timezone = message.text.strip()

    # Проверка на корректность введенного часового пояса
    if user_timezone not in pytz.all_timezones:
        await message.answer("Некорректный часовой пояс. Пожалуйста, попробуй снова.")
        return
    # Сохраняем часовой пояс в состоянии
    await state.update_data(timezone=user_timezone)
    await message.answer(f"Часовой пояс '{user_timezone}' успешно сохранен!")
    await state.set_state(Form.waiting_for_auth)


@command_router.message(StateFilter(Form.waiting_for_auth))
async def register(message: Message):
    button_register = KeyboardButton("/auth")
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_register]], resize_keyboard=True)
    await message.answer(
        "Чтобы подключить меня к Google Calendar, нажми на кнопку ниже:",
        reply_markup=keyboard,
    )


@command_router.message(Command("auth"))
async def handle_register_choice(message: Message):
    await message.answer("Для подключения к Google Calendar вам нужно авторизоваться.")
    # Начинаем процесс авторизации
    # ... здесь что-то будет


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
