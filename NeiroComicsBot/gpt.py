import telebot
import requests

TOKEN = '7186428634:AAG_d1Iz0lpHo5-XaUXHGaIGn5Tl3O7pdkQ'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я дружелюбный помощник в поиске информации о комиксах. Чем могу помочь?")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Я могу помочь в поиске информации о комиксах. Просто задайте мне вопрос.")

@bot.message_handler(func=lambda message: message.text.lower() == 'стоп')
def handle_stop(message):
    bot.send_message(message.chat.id, "До свидания!")

@bot.message_handler(func=lambda message: True)
def handle_continue(message):
    user_task = message.text
    resp = requests.post(
        'http://localhost:1234/v1/chat/completions', #Локальный сервер
        headers={"Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system",
                 "content": "Ты—дружелюбный помощник в поиске информации о комиксах. Ответь и изложи подробную информацию"},
                {"role": "user", "content": user_task}
            ],
            "temperature": 1,
            "max_tokens": 2048
        }
    )
    if resp.status_code == 200 and 'choices' in resp.json():
        bot.send_message(message.chat.id, resp.json()['choices'][0]['message']['content'])
    else:
        bot.send_message(message.chat.id, 'Не удалось получить ответ от нейросети')

bot.polling()

