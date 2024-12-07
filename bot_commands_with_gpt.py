import asyncio
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
import json
import datetime
import pytz
from pomo_token import TOKEN
from user_states import Form
from aiogram.fsm.state import StatesGroup, State
from gpt_integration import get_gpt_response



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
        f"Привет, {(message.from_user.full_name)}!\n Я готов помочь тебе с добавлением задач и дел в Google Calendar!\n"
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/set_timezone")]],
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

data = [0,0,0]

async def handle_gpt_response(response, state: FSMContext):
    # Парсим ответ от GPT
    parsed_data = [int(x.strip()) if x.strip().isdigit() else x.strip() for x in response.split(',')]
    task_name = parsed_data[0]
    date = parsed_data[1]
    time = parsed_data[2]

    # Сохраняем данные в FSMContext
    await state.update_data(parsed_data=parsed_data)

    # Формируем сообщение для пользователя
    if str(date) == '0' or date == 0 or str(date) == ' 0' or str(date) == '0 ':
        if str(time) == '0' or time == 0 or str(time) == ' 0' or str(time) == '0 ':
            return f"Для события '{task_name}' уточните дату и время."
        return f"Для события '{task_name}' уточните дату."
    elif str(time) == '0' or time == 0 or str(time) == ' 0' or str(time) == '0 ':
        return f"Для события '{task_name}' уточните время."
    else:
        # Сбрасываем данные после успешного назначения
        await state.update_data(parsed_data=[0, 0, 0])
        return f"Событие '{task_name}' запланировано на {date} в {time}."






@command_router.message(StateFilter(Form.waiting_for_event_title))
async def title_adding(message: Message, state: FSMContext):
    user_input = message.text

    # Сохраняем ввод пользователя в FSM
    await state.update_data(event_title=user_input)
    print(f"сообщение юзера: {user_input}")  # Debugging

    # Формируем запрос для GPT

    prompt = (
        f"Твоя задача определить узнать детали о встречи пользователя: [название, дата, время]"
        f"Пользователь написал: '{user_input}', до этого ты уже знаешь что {await state.get_data()}"
        f"Определи название события, про которое он говорит, и в какое время пользователь хочет иметь это событие"
        f" Запиши свой ответ в формате трех элементов через запятую [x,x,x] -  [название события, дата ММ:ДД, время ЧЧ:ММ]." 
        f"Нулевой элемент отвечает за названиею. Определи его, например, встреча с клиентом, и запиши в массив. Если названия нет, то запиши 0."      
        f"Второй элемент массива - дата. Если она есть, запиши её в формате ММ:ДД, если нет, запиши 0."
        f" третий элемент массива - время. Если оно есть, запиши её в формате ЧЧ:ММ, если нет, запиши 0."
        f" У тебя строгий формат ответа: название, дата, время"
    )

    # Отправляем запрос к GPT
    gpt_response = await get_gpt_response(prompt)
    print(f"GPT response: {gpt_response}")  # Debugging

    # Обрабатываем ответ GPT
    user_message = await handle_gpt_response(gpt_response, state)
    await message.answer(user_message)

    #
    # # Если GPT просит уточнить время, переходим в состояние для ожидания времени
    # if "уточни время" in gpt_response.lower() or "не хватает времени" in gpt_response.lower():
    #     await state.set_state(Form.waiting_for_event_time)
    # else:
    #     # Если данных достаточно
    #     data = await state.get_data()
    #     event_title = data.get("event_title")
    #     await message.answer(f"Событие '{event_title}' готово для записи в календарь!")
    #     # TODO: Записать событие в Google Calendar
    #     await state.clear()


@command_router.message(Command("add_task"))
@command_router.message(F.text.lower().contains("добавить событие"))
async def task_adding(message: Message, state: FSMContext):
    # Сбрасываем данные в FSM
    await state.update_data(data={"values": [0, 0, 0]})

    # Переходим в состояние ожидания описания события
    await state.set_state(Form.waiting_for_event_title)
    print(f"State set to: {await state.get_state()}")  # Debugging

    # Просим пользователя отправить описание события
    await message.answer("Отлично! Тогда отправь мне описание события.")



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
    # Без дополнительных параметров
    asyncio.run(dp.start_polling(bot))

