from asyncio import run
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
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
import datetime
import pytz
from pomo_token import TOKEN
from user_states import Form
from aiogram.fsm.state import StatesGroup, State


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

command_router = Router()
dp.include_router(command_router)


# Обработчик изображений и других типов контента
@command_router.message(~F.text)
async def handle_photo(message: Message):
    await message.answer("К сожалению, пока я понимаю только текст...\U0001F622")


# Обработчик команды /start
@command_router.message(CommandStart())
async def cmd_hello(message: Message, state: FSMContext):
    # Приветственное сообщение
    await state.clear()
    await message.answer(
        f"Привет, {(message.from_user.full_name)}!\nЯ готов помочь тебе с добавлением задач и дел в Google Calendar!\n"
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Установить часовой пояс")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "Чтобы установить часовой пояс, воспользуйся командой /set_timezone или нажми на кнопку ниже:",
        reply_markup=keyboard,
    )


# Отменить текущее действие и завершить состояние
@command_router.message(
    Command("cancel")
    or StateFilter(Form.started_auth)
    or StateFilter(Form.waiting_for_auth)
    or StateFilter(Form.waiting_for_timezone)
)
async def cancel_handler(message: Message, state: FSMContext):
    # Завершение состояния
    await state.clear()
    await message.answer(
        "Операция отменена. Чтобы увидеть список команд, используй /help."
    )


# Определяем список часовых поясов
timezones = {
    "Калининград": "Europe/Kaliningrad",  # UTC+2
    "Москва": "Europe/Moscow",  # UTC+3
    "Самара": "Europe/Samara",  # UTC+4
    "Екатеринбург": "Asia/Yekaterinburg",  # UTC+5
    "Омск": "Asia/Omsk",  # UTC+6
    "Красноярск": "Asia/Krasnoyarsk",  # UTC+7
    "Иркутск": "Asia/Irkutsk",  # UTC+8
    "Якутск": "Asia/Yakutsk",  # UTC+9
    "Владивосток": "Asia/Vladivostok",  # UTC+10
    "Магадан": "Asia/Magadan",  # UTC+11
    "Камчатка": "Asia/Kamchatka",  # UTC+12
}


# Обработчик команды для запроса часового пояса
@command_router.message(F.text.lower().contains("установить часовой пояс"))
@command_router.message(Command("set_timezone"))
async def set_timezone(message: types.Message, state: FSMContext):
    keyboard = []
    # Создаем кнопки с городами, где callback_data будет содержать часовой пояс
    for city, timezone in timezones.items():
        keyboard.append([InlineKeyboardButton(text=city, callback_data=timezone)])
    keyboard.append([InlineKeyboardButton(text="Другой", callback_data="other")])
    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        "Пожалуйста, выбери свой часовой пояс из списка ниже или нажми 'Другой', чтобы ввести его вручную.",
        reply_markup=keyboard_markup,
    )
    await state.set_state(Form.waiting_for_timezone)


@command_router.callback_query(StateFilter(Form.waiting_for_timezone))
async def handle_timezone_selection(
    callback_query: types.CallbackQuery, state: FSMContext
):
    timezone = callback_query.data

    # Если был выбран "Другой", запросим ввод вручную
    if timezone == "other":
        await callback_query.message.answer(
            "Пожалуйста, укажи свой часовой пояс (например, 'Europe/Moscow')."
        )
        await state.set_state(Form.waiting_for_manual_timezone)
        return
    # Проверка на корректность введенного часового пояса
    if timezone not in pytz.all_timezones:
        await callback_query.message.answer(
            "Некорректный часовой пояс. Пожалуйста, попробуй снова."
        )
        return
    # Сохраняем часовой пояс в состоянии
    await state.update_data(timezone=timezone)
    await callback_query.message.answer(f"Часовой пояс '{timezone}' успешно сохранен!")

    await state.set_state(Form.waiting_for_auth)


@command_router.message(StateFilter(Form.waiting_for_manual_timezone))
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
async def register(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/auth")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "Чтобы подключить меня к Google Calendar, нажми на кнопку ниже:",
        reply_markup=keyboard,
    )
    await state.set_state(Form.started_auth)


@command_router.message(Command("auth") or StateFilter(Form.started_auth))
async def handle_register_choice(message: Message, state: FSMContext):
    await message.answer(
        "Для подключения к Google Calendar нужно авторизоваться, для этого отправь любое сообщение:"
    )
    # процесс авторизации
    # ... здесь что-то будет
    await state.set_state(Form.started_auth)


@command_router.message(StateFilter(Form.started_auth))
async def process_auth_response(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Хочу добавить событие!")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "Спасибо! Ты успешно авторизовался. Если хочешь добавить новое событие или дело, нажми на кнопку ниже или воспользуся командой /add_task.",
        reply_markup=keyboard,
    )
    await state.clear()


@command_router.message(Command("add_task"))
@command_router.message(F.text.lower().contains("добавить событие"))
async def task_adding(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_for_event_title)
    await message.answer("Отлично! Тогда отправь мне описание события")


@command_router.message(StateFilter(Form.waiting_for_event_title))
async def title_adding(message: Message, state: FSMContext):
    await state.update_data(event_title=message.text)
    await message.answer("Хорошо! Теперь, пожалуйста, отправь мне время события")
    await state.set_state(Form.waiting_for_event_time)


@command_router.message(StateFilter(Form.waiting_for_event_time))
async def time_adding(message: Message, state: FSMContext):
    await state.update_data(event_time=message.text)
    data = await state.get_data()
    event_title = data.get("event_title")
    event_time = data.get("event_time")
    await message.answer(f"Событие {event_title} установлено на время {event_time}")
    await state.clear()


commands = {
    "/start": "Запуск бота",
    "/help": "Просмотр доступных команд",
    "/cancel": "Вернуться назад",
    "/auth": "Авторизоваться в Google Calendar",
    "/set_timezone": "Установить часовой пояс",
    "/add_task": "Добавить новое событие",
}


@command_router.message(Command("help"))
async def commands_list(message: types.Message):
    commands_message = "\n".join(
        [f"{command}: {description}" for command, description in commands.items()]
    )
    await bot.send_message(message.from_user.id, "Список команд:\n" + commands_message)


@command_router.message(F.text)
async def handle_random_message(message: Message):
    await message.answer(
        "Я не понял что это значит, используй /help чтобы увидеть доступные команды."
    )


if __name__ == "__main__":
    run(dp.start_polling(bot))
