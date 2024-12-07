# google_calendar.py
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Укажите необходимые области
SCOPES = ['https://www.googleapis.com/auth/calendar']


class Task:
    def __init__(self):
        self.title = None
        self.date = None
        self.time = None

    def is_ready(self):
        return self.title is not None and self.date is not None and self.time is not None



def get_google_calendar_service(user_email):
    """Создает и возвращает сервис для работы с Google Calendar API."""
    # Путь к вашему JSON ключу сервисного аккаунта
    SERVICE_ACCOUNT_FILE = r'C:\Users\User\PycharmProjects\pythonProject4\credentials.json'

    # Создание учетных данных для сервисного аккаунта с делегированием
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Делегирование полномочий
    delegated_credentials = credentials.with_subject(user_email)

    # Создание службы для работы с Google Calendar API
    service = build('calendar', 'v3', credentials=delegated_credentials)

    return service


def add_task_google(task, user_email):
    # Замените 'path_to_your_credentials.json' на путь к вашим учетным данным
    creds = Credentials.from_authorized_user_file(r'C:\Users\User\PycharmProjects\pythonProject4\credentials.json', SCOPES)

    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': task.title,
        'start': {
            'dateTime': f"{task.date}T{task.time}:00",
            'timeZone': 'Europe/Moscow',  # Укажите ваш часовой пояс
        },
        'end': {
            'dateTime': f"{task.date}T{task.time}:00",
            'timeZone': 'Europe/Moscow',
        },
    }

    try:
        service.events().insert(calendarId='primary', body=event).execute()
    except Exception as e:
        print(f"Ошибка при добавлении события: {e}")
        raise  # Вызовите исключение, чтобы оно было обработано в вызывающем коде
