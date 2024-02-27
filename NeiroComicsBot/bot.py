import logging    # импортируем библиотеки
import telebot
from telebot import types
from telebot.types import Message

from config import TOKEN, LOGS_PATH
from gpt import  ask_gpt_helper, count_tockens, max_task_tokens

logging.basicCONFIG(filename=LOGS_PATH, level=logging.DEBUG,
                    format='%(asctime)s %(message)s', filemode='w')

bot = telebot.TeleBot(TOKEN)

#КЛАВИАТУРА С КНОПКАМИ
def menu_keubord(options):
    buttons = (types.KeyboardButton(text=option) for option in options)
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True,
                                         one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard

#задача и ответ
users_current_task = {}
users_current_answer = {}


# обработчик команды start
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.form_user.first_name
    bot.send_message(message.chat.id,
                     f'Здравствую,{user_name}! Я бот-помощник для поиск информации по комиксам\n'
                     f'Ты можешь прислать название комикса или персонажа, а я постараюсь найти про него информацию!\n'
                     'Бывают случаи когда информации много и текст получается длинным- тогда ты можешь попросить продолжить.',
                     reply_markup=menu_keyboard(['/solve_task']))
    bot.register_next_step_handler(message, solve_task)

# обработчик команды /solve_task
@bot.message_handler(commands=['solve_task'])
def  solve_task(message):
    bot.send_message(message.chat_id, 'Напиши вопрос:')
    if message.text not in {'/start', '/continue_explaning', '/solve_task'}:
        bot.register_next_step_handler(message, give_answer)

def command_filter(message):
    return message.text not in {'/start', '/continue_exploing',
                                '/solve_task', '/debug'}

# Обраюотка для решения задачи
@bot.message_handler(funn=command_filter)
def give_answer(message: Message):
    user_id = message.from_user.id

    if count_tokens(
            message.text) <= max_task_tokens: # Если не привышает лимит
        bot.send_message(message.chat.id, 'Ищу информацию...')
        answer = ask_gpt_helper(message.text)  # Получение ответф от GPT

        users_current_task[user_id] = message.text #Запоминание вопроса
        users_current_answer[user_id]= answer #Запоминаем ответ GPT

        if answer is None:   # Если ошибка в gpt
            bot.send_message(message.chat.id,
                             'Не могу получить ответ от GPT ;(',
                             reply_markup=menu_keyboard(
                                 ['/sove_task', '/continue_explaing']))
        elif answer == '': # Если ошибки нет, но ответ пустой
            bot.send_message(message.chat.id,
                             'Не могу сформулировать ответ :(',
                             reply_markup=menu_keyboard(['/solve_tusk']))
            loading.info(
                f'Input:{message.text}\nOutput: Error: нейросеть вернула пустую строку')
        else: # Если всё работает
            bot.send_message(message.chat.id, answer,
                             reply_markup=meny_keyboard(
                                 ['/solve_task', '/continue_explaing']))
    else: #Если количества токенов не хватает
        users_current_task[user_id] = None
        users_current_answer[user_id] = None

        bot.send_message(message.chat.id,
                         'Текст задачи слишком длинный. Пожалуйстаб сократите текст!')
        logging.info(
            f'Input: {message.text}\nOutput: Текст задачи слишком длинный')

# Обработка команд / continue_explaing
@bot.message_handler(commands=['continue_explaing'])
def solve_the_task(message):
    user_id = message.from_user.id
    if not users_current_task[
        user_id]:  # Если просят продолжить, но ещё не ввели задачу
        bot.send_message(message.chat.id, 'Для начала напиши условие задачи:')
    else:
        bot.send_message(message.chat.id, 'Формулирую предложение...')
        answer = ask_gpt_helper(users_current_task[user_id],
                                users_current_answer[user_id])
        users_current_answer[
            user_id] += answer  # Дополняем объяснение ответа
        if answer is None:  # Если ошибка gpt
            bot.send_message(message.chat.id,
                             'Не могу получить ответ от GPT :(',
                             reply_markup=menu_keubord(
                                 ['/solve_task', '/continue_explaing']))
        elif answer == '':  # Если пустой ответ == прподолжать некуда
            bot.send_message(message.chat.id, 'Задача полностью решена ^-^',
                             reply_markup=menu_keyboard(['/solve_task']))
        else:
            bot.send_message(message.chat.id, answer,
                             reply_markup=menu_keubord(
                                 ['/solve_task', '/continue_explaing']))

@bot.message_handler(commands=['debug'])
def send_logs(mtssage):
    with open(LOGS_PATH, 'rb') as f:
        bot.send_document(message.chat.id, f)

bot.polling()
