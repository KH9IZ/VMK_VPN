import telebot
import os

from wg import *

conf = 'config'

try:
    token = os.environ['vpn_bot_token']
except:
    exit()

bot = telebot.TeleBot(token)


def gen_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(telebot.types.InlineKeyboardButton(
        "Get your config!", callback_data=conf))
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = gen_markup()
    bot.send_message(chat_id=message.chat.id,
                     text="Welcome to the CMC MSU bot for fast and secure VPN connection!",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == conf:
        doc = get_peer_config(call.from_user.id)

        if doc:
            bot.answer_callback_query(call.id, "Your config is ready!")
            bot.send_document(chat_id=call.message.chat.id, document=doc)
        else:
            bot.answer_callback_query(
                call.id, "No suitable config found. Sorry!")


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()