import datetime
import os.path
import pprint

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendar:
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    FILE_PATH = 'todo-bot-calendar-db2a7174b28f.json'

    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(
            filename=self.FILE_PATH, scopes=self.SCOPES
        )
        self.service = build('calendar', 'v3', credentials=creds)

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {
            'id': calendar_id  # пользователь в своём аккаунте должен найти
        }

        return self.service.calendarList().insert(body=calendar_list_entry).execute()

    def add_event(self, calendar_id):
        event = {
            'summary': 'test',
            'location': 'location',
            'description': 'test',
            'start': {
                'date': '2024-12-10',
                # 'timeZone': 'timeZone',
            },
            'end': {
                'date': '2024-12-10',
                # 'timeZone': 'timeZone',
            },
        }

        try:
            return self.service.events().insert(calendarId=calendar_id, body=event).execute()
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None


our_calendar = 'telegram-bot@todo-bot-calendar.iam.gserviceaccount.com'  # пользователь вручную даёт доступ
obj = GoogleCalendar()

# obj.add_calendar(
#     calendar_id='irinuwka04@gmail.com'
# )

# pprint.pprint(obj.get_calendar_list())

# event = obj.add_event(calendar_id=our_calendar)
# Добавляем календарь
# obj.add_calendar(calendar_id='irinuwka04@gmail.com')

# Получаем список календарей
# calendar_list = obj.service.calendarList().list().execute()
# pprint.pprint(calendar_list)

# pprint.pprint(obj.get_calendar_list())

# Добавляем событие
event = obj.add_event(calendar_id='irinuwka04@gmail.com')
if event:
    print("Event created:", event)
else:
    print("Failed to create event.")
