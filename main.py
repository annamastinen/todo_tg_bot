import telebot
from google_auth_httplib2 import Request
from telebot import types
from scheduler import Task, add_task_google, SCOPES  # Убедитесь, что у вас есть реализация add_task_google
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
import os

# TOKEN = "ADD_SECRET_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

# Хранение идентификаторов пользователей и токенов
user_data = {}

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Для разработки на localhost
CLIENT_SECRETS_FILE = "credentials.json"

@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Привет, я - твой помощник Помо!\n")

@bot.message_handler(content_types=["document", "audio", "gif", "photo", "video"])
def handle_unknown(message):
    bot.send_message(message.chat.id, "Я не понимаю, напиши текстом.\n")

@bot.message_handler(commands=["help"])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Google Calendar")
    item2 = types.KeyboardButton("Todoist")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "С какой программой ты хочешь работать?", reply_markup=markup)

@bot.message_handler(content_types="text")
def message_reply(message):
    user_id = message.chat.id

    if message.text == "Google Calendar":
        if user_id not in user_data or 'google_email' not in user_data[user_id]:
            bot.send_message(user_id, "Пожалуйста, введите ваш адрес электронной почты для Google Календаря:")
            bot.register_next_step_handler(message, process_email)
        else:
            ask_event_details(user_id)

@bot.message_handler(func=lambda message: True)  # Обработчик для всех текстовых сообщений
def handle_text_messages(message):
    user_id = message.chat.id

    if message.text.startswith("http"):  # Предполагается, что вы отправили пользователю ссылку на авторизацию
        process_auth_callback(message)  # Обработка URL-адреса для аутентификации
    elif message.text == "Google Calendar":
        if user_id not in user_data or 'google_email' not in user_data[user_id]:
            bot.send_message(user_id, "Пожалуйста, введите ваш адрес электронной почты для Google Календаря:")
            bot.register_next_step_handler(message, process_email)
        else:
            ask_event_details(user_id)
def process_email(message):
    user_id = message.chat.id
    email = message.text.strip()

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['google_email'] = email

    # Запуск процесса аутентификации
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri='http://localhost:8080/callback'  # Укажите свой редирект URI
    )
    authorization_url, state = flow.authorization_url(access_type='offline')
    user_data[user_id]['state'] = state  # Сохраняем состояние для последующего использования

    bot.send_message(user_id, f"Перейдите по следующей ссылке для авторизации: {authorization_url}")


def process_auth_callback(message):
    user_id = message.chat.id
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=user_data[user_id]['state']
    )
    flow.fetch_token(authorization_response=message.text)

    credentials = flow.credentials
    user_data[user_id]['credentials'] = credentials  # Сохраняем токены доступа

    bot.send_message(user_id, "Аутентификация прошла успешно! Теперь введите название события:")
    ask_event_details(user_id)  # Переход к запросу названия события

def ask_event_details(user_id):
    bot.send_message(user_id, "Введите название события:")
    bot.register_next_step_handler_by_chat_id(user_id, process_event_title)


def process_event_title(message):
    user_id = message.chat.id
    title = message.text.strip()

    if 'current_task' not in user_data[user_id]:
        user_data[user_id]['current_task'] = Task()

    user_data[user_id]['current_task'].title = title

    bot.send_message(user_id, "Введите дату события (в формате ГГГГ-ММ-ДД):")
    bot.register_next_step_handler_by_chat_id(user_id, process_event_date)

def process_event_date(message):
    user_id = message.chat.id
    date_str = message.text.strip()

    user_data[user_id]['current_task'].date = date_str

    bot.send_message(user_id, "Введите время события (в формате ЧЧ:ММ):")
    bot.register_next_step_handler_by_chat_id(user_id, process_event_time)

def process_event_time(message):
    user_id = message.chat.id
    time_str = message.text.strip()

    current_task = user_data[user_id]['current_task']
    current_task.time = time_str

    # Создаем событие в календаре
    create_calendar_event(user_id, current_task)
def create_calendar_event(user_id, task):
    # Получаем токен доступа из user_data
    credentials = get_credentials(user_id)  # Предполагается, что у вас есть функция для получения токена

    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': task.title,
        'start': {
            'dateTime': f"{task.date}T{task.time}:00",
            'timeZone': 'America/Los_Angeles',  # Укажите свой часовой пояс
        },
        'end': {
            'dateTime': f"{task.date}T{task.time}:00",
            'timeZone': 'America/Los_Angeles',  # Укажите свой часовой пояс
        },
    }

    try:
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        bot.send_message(user_id, f"Событие создано: {event_result.get('htmlLink')}")
    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка при создании события: {str(e)}")


def get_credentials(user_id):
    # Проверяем, есть ли у пользователя сохраненные учетные данные
    if user_id in user_data and 'credentials' in user_data[user_id]:
        creds = user_data[user_id]['credentials']
        # Проверяем, действительны ли учетные данные
        if creds and creds.valid:
            return creds
        elif creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
    else:
        # Если учетных данных нет, запускаем процесс аутентификации
        flow = InstalledAppFlow.from_client_secrets_file(
            r'C:\Users\User\PycharmProjects\pythonProject4\credentials.json',  # Путь к вашему файлу client_secret_.json
            SCOPES)  # Укажите необходимые области доступа

        creds = flow.run_local_server(port=0)

        # Сохраняем учетные данные в user_data
        user_data[user_id] = {'credentials': creds}

        return creds

    return None  # Если не удалось получить учетные данные


# Запуск бота
bot.polling(none_stop=True)