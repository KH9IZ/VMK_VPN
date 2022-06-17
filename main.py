"""VPN Bot main function, that declares it's workflow, supported commands and replies."""

import os
import gettext
import telebot

from wg import get_peer_config
from models import QuestionAnswer

translation = gettext.translation("messages", "trans", fallback=True)
_, ngettext = translation.gettext, translation.ngettext


try:
    token = os.environ['vpn_bot_token']
except Exception as exc:
    print(_("Couldn't find VPN BOT token in environment variables. Please, set it!"))
    raise ModuleNotFoundError from exc

bot = telebot.TeleBot(token)

def gen_markup(keys: dict, row_width: int):
    """Create inline keyboard of given shape with buttons specified like callback:name in dict."""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = row_width
    for conf_data, conf_text in keys.items():
        markup.add(telebot.types.InlineKeyboardButton(
            conf_text, callback_data=conf_data))
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Menu for /start command."""
    markup = gen_markup({"config":  _("Get your config!"),
                         "faq": _("FAQ")}, 1)
    bot.send_message(chat_id=message.chat.id,
                     text=_(
                         "Welcome to the CMC MSU bot for fast and secure VPN connection!"),
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "config")
def config_query(call):
    """Send user his config or to tell him that he doesn't have one."""
    # pylint: disable = unspecified-encoding
    if (doc := get_peer_config(call.from_user.id)):
        bot.answer_callback_query(call.id, _("Your config is ready!"))
        with open(doc, 'r') as config_file:
            bot.send_document(chat_id=call.message.chat.id, document=config_file)
    else:
        bot.answer_callback_query(
            call.id, _("No suitable config found. Sorry!"))


@bot.callback_query_handler(func=lambda call: call.data == 'faq')
def faq_menu_query(call):
    """Handle FAQ menu."""
    config: dict = {}
    for question in QuestionAnswer.select():
        config["faq_question_" + str(question.id)] = question.question
    config["back_to_main_menu"] = _(" « Back")
    bot.edit_message_text(_("Frequently asked questions"), call.message.chat.id,
                              call.message.message_id, reply_markup=gen_markup(config, 1))


@bot.callback_query_handler(func=lambda call: call.data.startswith("faq_question_"))
def faq_question_query(call):
    """Handle FAQ question button."""
    question_id = int(call.data.removeprefix("faq_question_"))
    query = QuestionAnswer.get_by_id(question_id)
    message_text = f"**{query.question}**\n\n{query.answer}"
    bot.answer_callback_query(call.id, _("See your answer:"))
    bot.edit_message_text(message_text, call.message.chat.id,
                          call.message.message_id,
                          reply_markup=gen_markup({"faq": _(" « Back")}, 1),
                          parse_mode="MARKDOWN")


@bot.callback_query_handler(func=lambda call: call.data == "back_to_main_menu")
def back_to_main_menu_query(call):
    """Handle back to main menu button."""
    markup = gen_markup({"config":  _("Get your config!"),
                         "faq": _("FAQ")}, 1)
    bot.edit_message_text(_("Welcome to the CMC MSU bot for fast and secure VPN connection!"),
                          call.message.chat.id,
                          call.message.message_id, reply_markup=markup)


def main():
    """Start bot."""
    bot.infinity_polling()


if __name__ == "__main__":
    main()
