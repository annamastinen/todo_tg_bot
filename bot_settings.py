import telebot
from telebot import types
from pomo_token import TOKEN  # скрыть token

from google_calendar import Task, log_calendar, add_task_google
from todoist import Todo, log_todoist, add_todo

bot = telebot.TeleBot(TOKEN)

# я не знаю что будет вместо id, возмоэно тут будет класс или просто строка
# но доставать это нужно из базы данных для каждого из пользователей бота
todoist_id = None
google_id = None

# здесь я тоже не уверена, возможно все будет удобно доставать из какой-нибудь базы данных,
#  по пользователю изымать все нужные значения или проще будет просто хранить переменную я хз
current_task = None
current_todo = None  # хотя блин я думаю не нужны они как глобальные совсем


@bot.message_handler(commands=["start"])
def start_message(
    message,
):  # приветственное сообщение можно потом дополнить но пока не важно
    bot.send_message(message.chat.id, "Привет, я - твой помощник Помо!\n")


@bot.message_handler(content_types=["document", "audio", "gif", "photo", "video"])
def handle_unknown(message):  # вообще не знаю надо ли это
    bot.send_message(message.chat.id, "Я не понимаю, напиши текстом.\n")


@bot.message_handler(commands=["help"])  # можно и не через help потом если что поправлю
def button_message(message):
    """Пользователь выбирает нужную ему программу для задачи"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Google Calendar")
    markup.add(item1)
    item2 = types.KeyboardButton("Todoist")
    markup.add(item2)
    bot.send_message(
        message.chat.id, "С какой программой ты хочешь работать?", reply_markup=markup
    )


@bot.message_handler(content_types="text")
def message_reply(message):
    """Создание события"""
    if message.text == "Google Calendar":
        if google_id is None:  # если у нас нет доступа к аккаунту пользователя
            log_calendar(google_id)
        current_task = Task()
        while not current_task.is_ready():
            # происходит что-то c gpt и мы постепенно заполняем все поля класса
            # нужно предусмотреть удаление события(current_task = None) и
            # выход из цикла если пользователь захочет выйти
            pass
        add_task_google(current_task)
    elif message.text == "Todoist":
        if todoist_id is None:  # если у нас нет доступа к аккаунту
            log_todoist(todoist_id)
        current_todo = Todo()
        while not current_todo.is_ready():
            # происходит что-то c gpt и мы постепенно заполняем все поля класса
            # нужно предусмотреть удаление события(current_todo = None) и
            # выход из цикла если пользователь захочет выйти
            pass
        add_todo(current_todo)


bot.polling(none_stop=True, interval=0)
