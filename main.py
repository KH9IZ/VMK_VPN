"""
VPN Bot main function, that declares it's workflow, supported commands and replies
"""

import os
import gettext
import telebot

from wg import get_peer_config


translation = gettext.translation("messages", "trans", fallback=True)
_, ngettext = translation.gettext, translation.ngettext


try:
    token = os.environ['VPN_BOT_TOKEN']
except Exception as exc:
    print(_("Couldn't find VPN BOT token in environment variables. Please, set it!"))
    raise ModuleNotFoundError from exc

bot = telebot.TeleBot(token)


def gen_markup(keys, row_width):
    """
    Create inline keyboard of given shape with buttons specified like callback:name in dict
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = row_width
    for conf in keys:
        markup.add(telebot.types.InlineKeyboardButton(
            keys[conf], callback_data=conf))
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Handler for /start command
    """
    markup = gen_markup({"config":  _("Get your config!")}, 1)
    bot.send_message(chat_id=message.chat.id,
                     text=_(
                         "Welcome to the CMC MSU bot for fast and secure VPN connection!"),
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "config")
def callback_query(call):
    """
    Callback handler to send user his config or to tell him that he doesn't have one
    """
    doc = get_peer_config(call.from_user.id)

    if doc:
        bot.answer_callback_query(call.id, _("Your config is ready!"))
        bot.send_document(chat_id=call.message.chat.id, document=doc)
    else:
        bot.answer_callback_query(
            call.id, _("No suitable config found. Sorry!"))


def main():
    """
    Start bot
    """
    bot.infinity_polling()


if __name__ == "__main__":
    main()
